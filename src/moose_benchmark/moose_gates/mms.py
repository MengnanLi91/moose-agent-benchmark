"""Protected execution and scoring gates for MMS refinement studies."""

from __future__ import annotations

import json
import math
import re
import shlex
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

from ..contracts import (
    CaseContract,
    EvaluationContext,
    ExternalGateResult,
    MmsExecutionMeasurement,
    MmsReferenceData,
    MmsResponse,
    MmsTask,
    SubmissionRecord,
)
from ..loader import load_model, resolve_inside, sha256_file
from ..runner import RunLimits, RunResult, run_command
from .base import (
    GateTools,
    _verify_submission_files,
    external_gate_result,
    safe_environment,
    validate_gate_results,
)
from .config import MmsGateConfig
from .hit import HitTool
from .metrics import (
    classify_mms_verdict,
    observed_orders,
    read_csv_rows,
    values_within_tolerance,
)


@dataclass
class MmsLevelResult:
    level: int
    parameter: float
    controls: dict[str, int | float | str]
    errors: dict[str, float]
    secondary_metrics: dict[str, float]
    run: RunResult
    csv_bytes: bytes


@dataclass
class MmsStudyResult:
    check: RunResult
    levels: list[MmsLevelResult]
    orders: dict[str, list[float]]
    oracle_valid: bool
    oracle_evidence: list[str]

    @property
    def successful(self) -> bool:
        if len(self.levels) != 4:
            return False
        results = [self.check, *(level.run for level in self.levels)]
        return all(
            result.exit_code == 0
            and not result.timed_out
            and not result.output_limit_exceeded
            and not result.process_limit_exceeded
            for result in results
        )

    @property
    def resource_compliant(self) -> bool:
        results = [self.check, *(level.run for level in self.levels)]
        return all(
            result.process_limit_enforced
            and not result.timed_out
            and not result.output_limit_exceeded
            and not result.process_limit_exceeded
            for result in results
        )


def _public_scaffold(case: CaseContract, public_root: Path, relative_path: str) -> Path:
    artifact = next(
        (item for item in case.artifacts if item.path == relative_path),
        None,
    )
    if artifact is None or artifact.sha256 is None:
        raise ValueError("MMS scaffold must be a hash-pinned public artifact")
    path = resolve_inside(public_root, relative_path)
    if not path.is_file() or sha256_file(path) != artifact.sha256:
        raise ValueError("MMS scaffold does not match its case contract")
    return path


def _normalized_hit_value(value: str) -> str:
    try:
        return " ".join(shlex.split(value))
    except ValueError:
        return value.strip().strip("'\"")


def _protected_instrumentation_matches(
    scaffold: Path,
    candidate: Path,
    patterns: list[str],
    tools: GateTools,
) -> tuple[bool, list[str]]:
    violations = _input_policy_violations(candidate, patterns)
    if violations:
        return False, violations

    hit = HitTool(tools.moose_dir)
    evidence: list[str] = []
    passed = True
    for pattern in patterns:
        expected = hit.find(pattern, scaffold)
        actual = hit.find(pattern, candidate)
        matches = expected == actual and bool(expected)
        passed = passed and matches
        evidence.append(f"{pattern}:passed={str(matches).lower()}")
    return passed, evidence


_SECTION_LINE = re.compile(r"^\s*\[([^\]]*)\]\s*(?:#.*)?$")


def _section_path_counts(input_text: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    stack: list[str] = []
    for line in input_text.splitlines():
        match = _SECTION_LINE.match(line)
        if match is None:
            continue
        token = match.group(1).strip()
        if token in {"", "../"}:
            if stack:
                stack.pop()
            continue
        if token.startswith("./"):
            token = token[2:]
        stack.append(token)
        path = "/".join(stack)
        counts[path] = counts.get(path, 0) + 1
    return counts


def _protected_object_paths(patterns: list[str]) -> set[str]:
    paths = set()
    for pattern in patterns:
        parts = pattern.split("/")
        if pattern.endswith("/**") and len(parts) >= 3:
            paths.add("/".join(parts[:-1]))
        elif len(parts) >= 3:
            paths.add("/".join(parts[:2]))
    return paths


def _input_policy_violations(candidate: Path, protected_patterns: list[str]) -> list[str]:
    text = candidate.read_text(encoding="utf-8")
    evidence = []
    if re.search(r"(?m)^\s*!include\b", text):
        evidence.append("unsafe_include:true")
    counts = _section_path_counts(text)
    for path in sorted(_protected_object_paths(protected_patterns)):
        if counts.get(path, 0) != 1:
            evidence.append(f"reserved_name:{path},count={counts.get(path, 0)}")
    return evidence


def _physics_conforms(
    candidate: Path,
    config: MmsGateConfig,
    tools: GateTools,
) -> tuple[bool, list[str]]:
    violations = _input_policy_violations(candidate, config.protected_hit_patterns)
    if violations:
        return False, violations

    hit = HitTool(tools.moose_dir)
    evidence: list[str] = []
    passed = True
    for requirement in config.physics_requirements:
        found = {
            _normalized_hit_value(value)
            for value in hit.find(requirement.pattern, candidate).values()
        }
        expected = {_normalized_hit_value(value) for value in requirement.required_values}
        accepted = expected <= found
        passed = passed and accepted
        evidence.append(
            f"{requirement.pattern}:expected={sorted(expected)},actual={sorted(found)},"
            f"passed={str(accepted).lower()}"
        )
    solve_values = {
        _normalized_hit_value(value).lower()
        for value in hit.find("Executioner/solve", candidate).values()
    }
    disabled_solve = "false" in solve_values
    if disabled_solve:
        evidence.append("Executioner/solve:false")
    return passed and not disabled_solve, evidence


def _run_limits(config: MmsGateConfig) -> RunLimits:
    return RunLimits(
        wall_time_seconds=config.limits.wall_time_seconds,
        cpu_seconds=config.limits.cpu_seconds,
        memory_mib=config.limits.memory_mib,
        max_output_bytes=config.limits.max_output_bytes,
        max_processes=config.limits.max_processes,
    )


def _execute(
    tools: GateTools,
    input_path: Path,
    overrides: list[str],
    cwd: Path,
    limits: RunLimits,
    *,
    check_input: bool = False,
) -> RunResult:
    argv = [str(tools.executable), "-i", str(input_path)]
    if check_input:
        argv.append("--check-input")
    argv.extend(overrides)
    return run_command(
        argv,
        cwd=cwd,
        limits=limits,
        environment=safe_environment(tools),
    )


def _extract_level(
    config: MmsGateConfig,
    level,
    run: RunResult,
    csv_path: Path,
) -> tuple[MmsLevelResult, bool, list[str]]:
    errors: dict[str, float] = {}
    secondary: dict[str, float] = {}
    evidence: list[str] = []
    valid = run.exit_code == 0 and csv_path.is_file()
    rows = read_csv_rows(csv_path) if valid else []
    if rows:
        final = rows[-1]
        for field, column in config.error_columns.items():
            value = final.get(column, math.nan)
            accepted = math.isfinite(value) and value > 0
            valid = valid and accepted
            errors[field] = value
            evidence.append(f"level={level.level},field={field},error={value:.16g}")
        for name, expectation in config.secondary_metrics.items():
            samples = rows if expectation.every_row else [final]
            accepted = all(
                column_value is not None
                and values_within_tolerance(
                    column_value,
                    expectation.expected,
                    absolute=expectation.tolerance.absolute,
                    relative=expectation.tolerance.relative,
                )
                for row in samples
                if (column_value := row.get(expectation.column)) is not None
            )
            accepted = accepted and all(expectation.column in row for row in samples)
            valid = valid and accepted
            secondary[name] = final.get(expectation.column, math.nan)
            evidence.append(f"level={level.level},secondary={name},passed={accepted}")
    return (
        MmsLevelResult(
            level=level.level,
            parameter=level.parameter,
            controls=level.controls,
            errors=errors,
            secondary_metrics=secondary,
            run=run,
            csv_bytes=csv_path.read_bytes() if csv_path.is_file() else b"",
        ),
        valid,
        evidence,
    )


def run_mms_study(
    case: CaseContract,
    config: MmsGateConfig,
    public_root: Path,
    input_path: Path,
    tools: GateTools,
) -> MmsStudyResult:
    study = case.verification_study
    if study is None or case.mms_task != MmsTask.IMPLEMENTATION:
        raise ValueError("MMS execution requires an implementation verification study")
    if set(config.error_columns) != set(study.required_fields):
        raise ValueError("MMS error columns must match the public required fields")
    if not input_path.is_file() or input_path.is_symlink():
        raise ValueError(f"MMS input is not a regular file: {input_path}")

    limits = _run_limits(config)
    level_results: list[MmsLevelResult] = []
    oracle_valid = True
    oracle_evidence: list[str] = []
    with tempfile.TemporaryDirectory(prefix=f"{case.case_id}-mms-") as directory:
        temporary_root = Path(directory)
        check_root = temporary_root / "check"
        shutil.copytree(public_root, check_root)
        check_input = resolve_inside(check_root, config.submitted_input_path)
        check_input.parent.mkdir(parents=True, exist_ok=True)
        check_input.write_bytes(input_path.read_bytes())
        check = _execute(
            tools,
            check_input,
            study.levels[0].overrides,
            check_root,
            limits,
            check_input=True,
        )
        if check.exit_code == 0 and not check.timed_out:
            for level in study.levels:
                level_root = temporary_root / f"level-{level.level}"
                shutil.copytree(public_root, level_root)
                level_input = resolve_inside(level_root, config.submitted_input_path)
                level_input.parent.mkdir(parents=True, exist_ok=True)
                level_input.write_bytes(input_path.read_bytes())
                run = _execute(
                    tools,
                    level_input,
                    level.overrides,
                    level_root,
                    limits,
                )
                result, valid, evidence = _extract_level(
                    config,
                    level,
                    run,
                    resolve_inside(level_root, config.csv_path),
                )
                level_results.append(result)
                oracle_valid = oracle_valid and valid
                oracle_evidence.extend(evidence)

    orders: dict[str, list[float]] = {}
    if len(level_results) == 4 and all(level.errors for level in level_results):
        parameters = [level.parameter for level in level_results]
        for field in study.required_fields:
            try:
                orders[field] = observed_orders(
                    parameters,
                    [level.errors[field] for level in level_results],
                )
            except (KeyError, ValueError):
                oracle_valid = False
    else:
        oracle_valid = False
    return MmsStudyResult(
        check=check,
        levels=level_results,
        orders=orders,
        oracle_valid=oracle_valid,
        oracle_evidence=oracle_evidence,
    )


def _response(context: EvaluationContext, submission: SubmissionRecord) -> MmsResponse:
    if submission.response is None:
        raise ValueError("MMS submission is missing response.json")
    path = resolve_inside(context.submission_root, submission.response.path)
    return MmsResponse.model_validate(json.loads(path.read_text(encoding="utf-8")))


def _sequence_matches(case: CaseContract, response: MmsResponse) -> bool:
    study = case.verification_study
    if study is None:
        return False
    claim = response.claim
    if claim.norm != study.norm or claim.refinement_parameter != study.refinement_parameter:
        return False
    return all(
        actual.level == expected.level
        and math.isclose(actual.parameter, expected.parameter)
        and actual.controls == expected.controls
        and set(actual.errors) == set(study.required_fields)
        for actual, expected in zip(claim.runs, study.levels, strict=True)
    )


def reference_data_matches(
    current: MmsReferenceData,
    frozen: MmsReferenceData,
) -> bool:
    if (
        current.norm != frozen.norm
        or current.refinement_parameter != frozen.refinement_parameter
        or current.expected_order != frozen.expected_order
        or current.asymptotic_regime != frozen.asymptotic_regime
        or current.verdict != frozen.verdict
        or current.moose_revision != frozen.moose_revision
        or current.executable_sha256 != frozen.executable_sha256
        or len(current.runs) != len(frozen.runs)
    ):
        return False
    for actual, expected in zip(current.runs, frozen.runs, strict=True):
        if actual.level != expected.level or actual.controls != expected.controls:
            return False
        if not math.isclose(actual.parameter, expected.parameter):
            return False
        for field, expected_value in expected.errors.items():
            actual_value = actual.errors.get(field, math.nan)
            if not values_within_tolerance(
                actual_value,
                expected_value,
                absolute=frozen.error_tolerance.absolute,
                relative=frozen.error_tolerance.relative,
            ):
                return False
    return _orders_match(
        current.observed_orders,
        frozen.observed_orders,
        frozen.order_tolerance,
    )


def _orders_match(actual: dict[str, list[float]], expected, tolerance) -> bool:
    if set(actual) != set(expected):
        return False
    return all(
        len(actual[field]) == len(expected_values)
        and all(
            values_within_tolerance(
                actual_value,
                expected_value,
                absolute=tolerance.absolute,
                relative=tolerance.relative,
            )
            for actual_value, expected_value in zip(
                actual[field],
                expected_values,
                strict=True,
            )
        )
        for field, expected_values in expected.items()
    )


def _response_matches_measurement(
    response: MmsResponse,
    measurement: MmsExecutionMeasurement,
    reference: MmsReferenceData,
) -> bool:
    claim = response.claim
    if (
        claim.norm != measurement.norm
        or claim.refinement_parameter != measurement.refinement_parameter
        or claim.asymptotic_regime != measurement.asymptotic_regime
        or claim.verdict != measurement.verdict
        or set(claim.expected_order) != set(measurement.expected_order)
    ):
        return False
    if any(
        not values_within_tolerance(
            claim.expected_order[field],
            expected,
            absolute=reference.order_tolerance.absolute,
            relative=reference.order_tolerance.relative,
        )
        for field, expected in measurement.expected_order.items()
    ):
        return False

    actual_runs = {run.level: run for run in response.claim.runs}
    for measured in measurement.runs:
        reported = actual_runs.get(measured.level)
        if (
            reported is None
            or not math.isclose(reported.parameter, measured.parameter)
            or reported.controls != measured.controls
            or set(reported.errors) != set(measured.errors)
        ):
            return False
        for field, value in measured.errors.items():
            if not values_within_tolerance(
                reported.errors.get(field, math.nan),
                value,
                absolute=reference.error_tolerance.absolute,
                relative=reference.error_tolerance.relative,
            ):
                return False
    return _orders_match(
        response.claim.observed_orders,
        measurement.observed_orders,
        reference.order_tolerance,
    )


def _gate(
    context: EvaluationContext,
    submission: SubmissionRecord,
    gate_id: str,
    passed: bool,
    detail: str,
    evidence: list[str] | None = None,
    measurement: MmsExecutionMeasurement | None = None,
) -> ExternalGateResult:
    return external_gate_result(
        context,
        submission,
        gate_id,
        passed,
        detail,
        evidence,
        measurement,
    )


def _measurement(
    case: CaseContract,
    submission: SubmissionRecord,
    study: MmsStudyResult,
) -> MmsExecutionMeasurement | None:
    public_study = case.verification_study
    if public_study is None or not study.successful or not study.oracle_valid:
        return None
    asymptotic, verdict = classify_mms_verdict(
        study.orders,
        public_study.expected_orders,
    )
    return MmsExecutionMeasurement(
        schema_version="1.0",
        case_id=case.case_id,
        submission_sha256=submission.submission_sha256,
        norm=public_study.norm,
        refinement_parameter=public_study.refinement_parameter,
        runs=[
            {
                "level": level.level,
                "parameter": level.parameter,
                "controls": level.controls,
                "errors": level.errors,
            }
            for level in study.levels
        ],
        observed_orders=study.orders,
        expected_order=public_study.expected_orders,
        asymptotic_regime=asymptotic,
        verdict=verdict,
    )


def generate_mms_gates(
    case: CaseContract,
    config: MmsGateConfig,
    tools: GateTools,
    context: EvaluationContext,
    submission: SubmissionRecord,
) -> list[ExternalGateResult]:
    if config.case_id != case.case_id or submission.case_id != case.case_id:
        raise ValueError("MMS case, gate configuration, and submission IDs must match")
    if case.mms_task != MmsTask.IMPLEMENTATION:
        raise ValueError("MMS protected execution requires an implementation case")
    if config.reference_data is None:
        raise ValueError("MMS gate generation requires frozen reference data")

    scaffold = _public_scaffold(
        case,
        context.public_case_root,
        config.public_scaffold_path,
    )
    candidate = _verify_submission_files(
        context.submission_root.resolve(),
        submission,
        config.submitted_input_path,
    )
    instrumentation_ok, instrumentation_evidence = _protected_instrumentation_matches(
        scaffold,
        candidate,
        config.protected_hit_patterns,
        tools,
    )
    physics_ok, physics_evidence = _physics_conforms(candidate, config, tools)
    response = _response(context, submission)
    complete = _sequence_matches(case, response)
    reference = load_model(
        resolve_inside(context.private_case_root, config.reference_data),
        MmsReferenceData,
    )
    study = run_mms_study(
        case,
        config,
        context.public_case_root,
        candidate,
        tools,
    )
    measurement = _measurement(case, submission, study)
    protected = instrumentation_ok and study.successful and study.oracle_valid
    convergence_ok = bool(measurement and measurement.verdict == "verified")
    reported = (
        complete
        and measurement is not None
        and _response_matches_measurement(
            response,
            measurement,
            reference,
        )
    )
    usage = submission.usage
    budget = case.budget
    resource_ok = study.resource_compliant and (
        usage.wall_time_seconds <= budget.wall_time_seconds
        and usage.cpu_seconds <= budget.cpu_seconds
        and usage.memory_mib <= budget.memory_mib
        and usage.validation_attempts <= budget.validation_attempts
        and usage.execution_attempts <= budget.execution_attempts
    )
    results = [
        _gate(
            context,
            submission,
            "physics_conformance",
            physics_ok,
            (
                "submitted input contains the required physics structure"
                if physics_ok
                else "submitted input is missing required physics or uses an unsafe include"
            ),
            physics_evidence,
        ),
        _gate(
            context,
            submission,
            "complete_refinement_sequence",
            complete,
            (
                "all prescribed refinement levels are present exactly once"
                if complete
                else "reported refinement levels or controls differ from the contract"
            ),
        ),
        _gate(
            context,
            submission,
            "successful_moose_runs",
            study.successful,
            (
                "check-input and all four authoritative runs succeeded"
                if study.successful
                else "check-input or an authoritative refinement run failed"
            ),
        ),
        _gate(
            context,
            submission,
            "protected_error_oracle",
            protected,
            (
                "protected instrumentation is unchanged and produced finite errors"
                if protected
                else "protected instrumentation changed or failed to produce valid errors"
            ),
            [*instrumentation_evidence, *study.oracle_evidence],
        ),
        _gate(
            context,
            submission,
            "required_convergence",
            convergence_ok,
            (
                "every required field meets the formal-order convergence band"
                if convergence_ok
                else "one or more required fields do not meet the convergence band"
            ),
        ),
        _gate(
            context,
            submission,
            "reported_values_match",
            reported,
            (
                "reported errors and orders match the authoritative rerun"
                if reported
                else "reported errors or orders differ from the authoritative rerun"
            ),
            measurement=measurement,
        ),
        _gate(
            context,
            submission,
            "resource_compliance",
            resource_ok,
            (
                "runner-owned usage and protected execution remain within limits"
                if resource_ok
                else "runner-owned usage or protected execution exceeded a limit"
            ),
        ),
    ]
    return validate_gate_results(config, results)


def build_reference_data(
    case: CaseContract,
    config: MmsGateConfig,
    tools: GateTools,
    study: MmsStudyResult,
) -> MmsReferenceData:
    public_study = case.verification_study
    if public_study is None:
        raise ValueError("MMS reference generation requires verification_study")
    if not study.successful or not study.oracle_valid:
        raise ValueError("cannot freeze an unsuccessful or invalid MMS study")
    asymptotic, verdict = classify_mms_verdict(
        study.orders,
        public_study.expected_orders,
    )
    if verdict == "inconclusive":
        raise ValueError("cannot freeze an inconclusive MMS study")
    return MmsReferenceData(
        schema_version="1.0",
        norm=public_study.norm,
        refinement_parameter=public_study.refinement_parameter,
        runs=[
            {
                "level": level.level,
                "parameter": level.parameter,
                "controls": level.controls,
                "errors": level.errors,
            }
            for level in study.levels
        ],
        observed_orders=study.orders,
        expected_order=public_study.expected_orders,
        asymptotic_regime=asymptotic,
        verdict=verdict,
        moose_revision=config.expected_moose_revision,
        executable_sha256=sha256_file(tools.executable),
    )


def write_validation_artifacts(
    study: MmsStudyResult,
    output_dir: Path,
    *,
    case: CaseContract,
    config: MmsGateConfig,
    tools: GateTools,
    public_root: Path,
    private_root: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    scaffold = resolve_inside(public_root, config.public_scaffold_path)
    canonical_input = resolve_inside(private_root, config.canonical_input_path)
    protected, protected_evidence = _protected_instrumentation_matches(
        scaffold,
        canonical_input,
        config.protected_hit_patterns,
        tools,
    )
    physics, physics_evidence = _physics_conforms(canonical_input, config, tools)
    metadata = {
        "schema_version": "1.0",
        "case_id": case.case_id,
        "moose_revision": config.expected_moose_revision,
        "executable_sha256": sha256_file(tools.executable),
        "public_scaffold_sha256": sha256_file(scaffold),
        "canonical_input_sha256": sha256_file(canonical_input),
        "protected_instrumentation_unchanged": protected,
        "protected_instrumentation_evidence": protected_evidence,
        "canonical_physics_conforms": physics,
        "canonical_physics_evidence": physics_evidence,
    }
    (output_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "check-input.json").write_text(
        json.dumps(study.check.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    for level in study.levels:
        prefix = output_dir / f"level-{level.level}"
        prefix.with_suffix(".run.json").write_text(
            json.dumps(level.run.to_dict(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        prefix.with_suffix(".csv").write_bytes(level.csv_bytes)
