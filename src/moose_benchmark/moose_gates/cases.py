"""Case-specific protected gate orchestration."""

from __future__ import annotations

import fnmatch
import shlex
import tempfile
from pathlib import Path

from ..contracts import EvaluationContext, ExternalGateResult, SubmissionRecord
from .base import (
    GateTools,
    GateWorkspace,
    command_succeeded,
    external_gate_result,
    run_configured_command,
    validate_gate_results,
)
from .config import MooseGateConfig
from .errors import GateInfrastructureError
from .hit import HitTool
from .metrics import (
    contains_any,
    final_reported_time,
    read_csv_rows,
    within_tolerance,
)


def _gate(
    context: EvaluationContext,
    submission: SubmissionRecord,
    gate_id: str,
    passed: bool,
    detail: str,
    evidence: list[str] | None = None,
) -> ExternalGateResult:
    return external_gate_result(
        context,
        submission,
        gate_id,
        passed,
        detail,
        evidence,
    )


def _hit_changed_paths(workspace: GateWorkspace, tools: GateTools) -> set[str]:
    suffix = workspace.candidate_path.suffix or ".i"
    reference_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as stream:
            stream.write(workspace.reference_artifact)
            reference_path = Path(stream.name)
        return (
            HitTool(tools.moose_dir)
            .diff(
                reference_path,
                workspace.candidate_path,
            )
            .changed_paths
        )
    finally:
        if reference_path is not None:
            reference_path.unlink(missing_ok=True)


def _paths_are_authorized(changed_paths: set[str], patterns: list[str]) -> bool:
    return all(
        any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns) for path in changed_paths
    )


def _scope_result(
    config: MooseGateConfig,
    workspace: GateWorkspace,
    tools: GateTools,
    context: EvaluationContext,
    submission: SubmissionRecord,
    *,
    required_paths: set[str] | None = None,
) -> tuple[ExternalGateResult, set[str], bool]:
    changed = _hit_changed_paths(workspace, tools)
    authorized = _paths_are_authorized(changed, config.authorized_hit_paths)
    if required_paths is not None:
        authorized = authorized and changed == required_paths
    detail = (
        "candidate changes are confined to the authorized HIT paths"
        if authorized
        else "candidate changes include missing or unauthorized HIT paths"
    )
    result = _gate(
        context,
        submission,
        "authorized_edit_scope",
        authorized,
        detail,
        [f"changed_path:{path}" for path in sorted(changed)],
    )
    return result, changed, authorized


def _blocked_gate(
    context: EvaluationContext,
    submission: SubmissionRecord,
    gate_id: str,
    prerequisite: str,
) -> ExternalGateResult:
    return _gate(
        context,
        submission,
        gate_id,
        False,
        f"not evaluated because {prerequisite} failed",
    )


def _command_evidence(command_name: str, result) -> list[str]:
    return [
        f"command:{command_name}",
        f"exit_code:{result.exit_code}",
        f"wall_time_seconds:{result.wall_time_seconds}",
        f"timed_out:{str(result.timed_out).lower()}",
        f"output_limit_exceeded:{str(result.output_limit_exceeded).lower()}",
        f"process_limit_exceeded:{str(result.process_limit_exceeded).lower()}",
    ]


def _command_gate(
    config: MooseGateConfig,
    command_name: str,
    gate_id: str,
    workspace: GateWorkspace,
    tools: GateTools,
    context: EvaluationContext,
    submission: SubmissionRecord,
):
    result = run_configured_command(config, command_name, workspace, tools)
    passed = command_succeeded(result)
    return (
        _gate(
            context,
            submission,
            gate_id,
            passed,
            (
                f"{command_name} completed within evaluator limits"
                if passed
                else f"{command_name} failed or exceeded evaluator limits"
            ),
            _command_evidence(command_name, result),
        ),
        result,
    )


def _combined_output(result) -> str:
    return f"{result.stdout}\n{result.stderr}"


def _load_rows(config: MooseGateConfig, workspace: GateWorkspace) -> list[dict[str, float]]:
    if config.csv_path is None:
        raise GateInfrastructureError("gate configuration does not declare csv_path")
    return read_csv_rows(workspace.root / config.csv_path)


def _row_value(
    rows: list[dict[str, float]],
    row_index: int,
    column: str,
) -> float:
    try:
        row = rows[row_index]
        return row[column]
    except (IndexError, KeyError) as exc:
        raise GateInfrastructureError(
            f"configured CSV sample is unavailable: row={row_index}, column={column}"
        ) from exc


def _check_metric_expectations(
    config: MooseGateConfig,
    rows: list[dict[str, float]],
    prefix: str,
) -> tuple[bool, list[str]]:
    selected = {
        name: expectation
        for name, expectation in config.metric_expectations.items()
        if name.startswith(prefix)
    }
    if not selected:
        raise GateInfrastructureError(f"no metric expectations configured for {prefix}")
    evidence: list[str] = []
    passed = True
    for name, expectation in selected.items():
        actual = _row_value(rows, expectation.row, expectation.column)
        accepted = within_tolerance(actual, expectation.expected, expectation.tolerance)
        passed = passed and accepted
        evidence.append(
            f"{name}:actual={actual:.16g},expected={expectation.expected:.16g},"
            f"passed={str(accepted).lower()}"
        )
    return passed, evidence


def _check_metric_equalities(
    config: MooseGateConfig,
    rows: list[dict[str, float]],
    prefix: str,
) -> tuple[bool, list[str]]:
    selected = {
        name: equality
        for name, equality in config.metric_equalities.items()
        if name.startswith(prefix)
    }
    if not selected:
        raise GateInfrastructureError(f"no metric equalities configured for {prefix}")
    evidence: list[str] = []
    passed = True
    for name, equality in selected.items():
        left = _row_value(rows, equality.row, equality.left_column)
        right = _row_value(rows, equality.row, equality.right_column)
        accepted = within_tolerance(left, right, equality.tolerance)
        passed = passed and accepted
        evidence.append(
            f"{name}:left={left:.16g},right={right:.16g}," f"passed={str(accepted).lower()}"
        )
    return passed, evidence


def _run_r1(
    config: MooseGateConfig,
    workspace: GateWorkspace,
    tools: GateTools,
    context: EvaluationContext,
    submission: SubmissionRecord,
) -> list[ExternalGateResult]:
    scope, _changed, scope_ok = _scope_result(
        config,
        workspace,
        tools,
        context,
        submission,
    )
    results = [
        scope,
        _gate(
            context,
            submission,
            "physics_preservation",
            scope_ok,
            "all frozen physics paths are unchanged" if scope_ok else "frozen paths changed",
        ),
    ]
    if not scope_ok:
        results.extend(
            _blocked_gate(context, submission, gate_id, "authorized_edit_scope")
            for gate_id in config.required_gates
            if gate_id not in {"authorized_edit_scope", "physics_preservation"}
        )
        return validate_gate_results(config, results)

    validation, check = _command_gate(
        config,
        "check_input",
        "input_validation",
        workspace,
        tools,
        context,
        submission,
    )
    results.append(validation)
    if not command_succeeded(check):
        results.extend(
            _blocked_gate(context, submission, gate_id, "input_validation")
            for gate_id in config.required_gates
            if gate_id not in {result.gate_id for result in results}
        )
        return validate_gate_results(config, results)

    execution, run = _command_gate(
        config,
        "run",
        "bounded_execution",
        workspace,
        tools,
        context,
        submission,
    )
    results.append(execution)
    run_output = _combined_output(run)
    removed = command_succeeded(run) and not contains_any(run_output, config.failure_signatures)
    removed = removed and (
        not config.success_signatures or contains_any(run_output, config.success_signatures)
    )
    results.append(
        _gate(
            context,
            submission,
            "target_failure_removed",
            removed,
            "periodic neighbor construction succeeds" if removed else "target failure remains",
        )
    )
    if command_succeeded(run):
        rows = _load_rows(config, workspace)
        equal, equal_evidence = _check_metric_equalities(config, rows, "translated.")
        preserved, preserved_evidence = _check_metric_expectations(
            config, rows, "integral_average."
        )
        results.extend(
            [
                _gate(
                    context,
                    submission,
                    "translated_point_equality",
                    equal,
                    "translated point values agree" if equal else "translated values differ",
                    equal_evidence,
                ),
                _gate(
                    context,
                    submission,
                    "integral_average_preservation",
                    preserved,
                    (
                        "reference scalar quantities are preserved"
                        if preserved
                        else "reference scalar quantities changed"
                    ),
                    preserved_evidence,
                ),
            ]
        )
    else:
        results.extend(
            _blocked_gate(context, submission, gate_id, "bounded_execution")
            for gate_id in ("translated_point_equality", "integral_average_preservation")
        )
    return validate_gate_results(config, results)


def _coupling_configuration(
    config: MooseGateConfig,
    workspace: GateWorkspace,
    tools: GateTools,
) -> tuple[bool, list[str]]:
    if config.coupling_path is None or config.coupling_variable is None:
        raise GateInfrastructureError("R2 coupling configuration is incomplete")
    values = HitTool(tools.moose_dir).find(config.coupling_path, workspace.candidate_path)
    raw = values.get(config.coupling_path)
    if raw is None:
        return False, [f"{config.coupling_path}:missing"]
    actual = shlex.split(raw)
    expected = [config.coupling_variable]
    return actual == expected, [
        f"{config.coupling_path}:actual={','.join(actual)}",
        f"{config.coupling_path}:expected={config.coupling_variable}",
    ]


def _run_r2(
    config: MooseGateConfig,
    workspace: GateWorkspace,
    tools: GateTools,
    context: EvaluationContext,
    submission: SubmissionRecord,
) -> list[ExternalGateResult]:
    required_paths = set(config.authorized_hit_paths)
    scope, _changed, scope_ok = _scope_result(
        config,
        workspace,
        tools,
        context,
        submission,
        required_paths=required_paths,
    )
    coupling_ok, coupling_evidence = _coupling_configuration(config, workspace, tools)
    results = [
        scope,
        _gate(
            context,
            submission,
            "coupling_configuration",
            coupling_ok,
            (
                "the required variable is declared on the dependent material"
                if coupling_ok
                else "the dependent material has a missing or incorrect variable declaration"
            ),
            coupling_evidence,
        ),
    ]
    if not scope_ok:
        results.append(
            _gate(
                context,
                submission,
                "physics_preservation",
                False,
                "candidate changes extend beyond the coupling declaration",
            )
        )
        results.extend(
            _blocked_gate(context, submission, gate_id, "authorized_edit_scope")
            for gate_id in config.required_gates
            if gate_id not in {result.gate_id for result in results}
        )
        return validate_gate_results(config, results)

    validation, check = _command_gate(
        config,
        "check_input",
        "input_validation",
        workspace,
        tools,
        context,
        submission,
    )
    results.append(validation)
    if not command_succeeded(check):
        results.extend(
            [
                _blocked_gate(
                    context,
                    submission,
                    "bounded_execution",
                    "input_validation",
                ),
                _gate(
                    context,
                    submission,
                    "target_failure_removed",
                    False,
                    "the missing-variable diagnostic remains",
                ),
                _gate(
                    context,
                    submission,
                    "physics_preservation",
                    scope_ok,
                    "all frozen input paths remain unchanged",
                ),
            ]
        )
        return validate_gate_results(config, results)

    execution, run = _command_gate(
        config,
        "run",
        "bounded_execution",
        workspace,
        tools,
        context,
        submission,
    )
    results.append(execution)
    output = _combined_output(run)
    removed = (
        coupling_ok
        and command_succeeded(run)
        and not contains_any(output, config.failure_signatures)
        and (not config.success_signatures or contains_any(output, config.success_signatures))
    )
    results.append(
        _gate(
            context,
            submission,
            "target_failure_removed",
            removed,
            (
                "the declared dependency parses and the solve converges"
                if removed
                else "the coupling failure remains or the solve does not converge"
            ),
        )
    )
    physics_ok = scope_ok
    physics_evidence: list[str] = []
    if command_succeeded(run):
        rows = _load_rows(config, workspace)
        reference_ok, physics_evidence = _check_metric_expectations(config, rows, "reference.")
        physics_ok = physics_ok and reference_ok
    else:
        physics_ok = False
    results.append(
        _gate(
            context,
            submission,
            "physics_preservation",
            physics_ok,
            (
                "frozen input paths and reference quantities are preserved"
                if physics_ok
                else "frozen input paths or reference quantities changed"
            ),
            physics_evidence,
        )
    )
    return validate_gate_results(config, results)


def _fieldsplit_partition(
    config: MooseGateConfig,
    workspace: GateWorkspace,
    tools: GateTools,
) -> tuple[bool, list[str]]:
    hit = HitTool(tools.moose_dir)
    found = hit.find(
        "Preconditioning/**/vars",
        workspace.candidate_path,
    )
    found_children = hit.find(
        "Preconditioning/**/splitting",
        workspace.candidate_path,
    )
    actual: dict[str, set[str]] = {}
    evidence: list[str] = []
    for node, expected_values in config.partition_variables.items():
        if node == "__all__":
            actual[node] = set(expected_values)
            continue
        matches = [value for path, value in found.items() if path.endswith(f"/{node}/vars")]
        if len(matches) != 1:
            evidence.append(f"{node}:ownership_declarations={len(matches)}")
            return False, evidence
        actual[node] = set(shlex.split(matches[0]))
        evidence.append(f"{node}:vars={','.join(sorted(actual[node]))}")
        if actual[node] != set(expected_values):
            return False, evidence
    for parent, children in config.partition_children.items():
        if parent not in actual or any(child not in actual for child in children):
            raise GateInfrastructureError(f"partition config references unknown node {parent}")
        matches = [
            value for path, value in found_children.items() if path.endswith(f"/{parent}/splitting")
        ]
        if len(matches) != 1:
            evidence.append(f"{parent}:splitting_declarations={len(matches)}")
            return False, evidence
        actual_children = set(shlex.split(matches[0]))
        evidence.append(f"{parent}:children={','.join(sorted(actual_children))}")
        if actual_children != set(children):
            return False, evidence
        child_sets = [actual[child] for child in children]
        if any(not values <= actual[parent] for values in child_sets):
            return False, evidence
        for index, left in enumerate(child_sets):
            if any(left & right for right in child_sets[index + 1 :]):
                return False, evidence
        if set().union(*child_sets) != actual[parent]:
            return False, evidence
    return True, evidence


def _run_r3(
    config: MooseGateConfig,
    workspace: GateWorkspace,
    tools: GateTools,
    context: EvaluationContext,
    submission: SubmissionRecord,
) -> list[ExternalGateResult]:
    scope, _changed, scope_ok = _scope_result(config, workspace, tools, context, submission)
    partition_ok, partition_evidence = _fieldsplit_partition(config, workspace, tools)
    results = [
        scope,
        _gate(
            context,
            submission,
            "fieldsplit_partition",
            partition_ok,
            (
                "nested split ownership is complete and disjoint"
                if partition_ok
                else "nested split ownership is incomplete or overlapping"
            ),
            partition_evidence,
        ),
        _gate(
            context,
            submission,
            "solver_preservation",
            scope_ok,
            (
                "the intended field-split solver is preserved"
                if scope_ok
                else "solver configuration changed outside ownership wiring"
            ),
        ),
    ]
    if not scope_ok or not partition_ok:
        prerequisite = "authorized_edit_scope" if not scope_ok else "fieldsplit_partition"
        results.extend(
            _blocked_gate(context, submission, gate_id, prerequisite)
            for gate_id in config.required_gates
            if gate_id not in {result.gate_id for result in results}
        )
        return validate_gate_results(config, results)

    validation, check = _command_gate(
        config,
        "check_input",
        "input_validation",
        workspace,
        tools,
        context,
        submission,
    )
    results.append(validation)
    if not command_succeeded(check):
        results.extend(
            _blocked_gate(context, submission, gate_id, "input_validation")
            for gate_id in config.required_gates
            if gate_id not in {result.gate_id for result in results}
        )
        return validate_gate_results(config, results)

    execution, run = _command_gate(
        config, "run", "bounded_execution", workspace, tools, context, submission
    )
    results.append(execution)
    output = _combined_output(run)
    removed = command_succeeded(run) and not contains_any(output, config.failure_signatures)
    removed = removed and (
        not config.success_signatures or contains_any(output, config.success_signatures)
    )
    results.append(
        _gate(
            context,
            submission,
            "target_failure_removed",
            removed,
            "field-split setup succeeds" if removed else "field-split failure remains",
        )
    )
    if command_succeeded(run):
        rows = _load_rows(config, workspace)
        preserved, evidence = _check_metric_expectations(config, rows, "reference.")
        results.append(
            _gate(
                context,
                submission,
                "reference_quantities",
                preserved,
                (
                    "flow and concentration quantities match"
                    if preserved
                    else "flow or concentration quantities changed"
                ),
                evidence,
            )
        )
    else:
        results.append(
            _blocked_gate(context, submission, "reference_quantities", "bounded_execution")
        )
    return validate_gate_results(config, results)


def _accepted_hit_values(
    config: MooseGateConfig,
    workspace: GateWorkspace,
    tools: GateTools,
) -> tuple[bool, list[str]]:
    hit = HitTool(tools.moose_dir)
    passed = True
    evidence: list[str] = []
    for path, (lower, upper) in config.accepted_ranges.items():
        values = hit.find(path, workspace.candidate_path)
        raw = values.get(path)
        if raw is None:
            passed = False
            evidence.append(f"{path}:missing")
            continue
        try:
            value = float(raw.strip().strip("'\""))
        except ValueError:
            passed = False
            evidence.append(f"{path}:not_numeric")
            continue
        accepted = lower <= value <= upper
        passed = passed and accepted
        evidence.append(f"{path}:value={value:.16g},in_range={str(accepted).lower()}")
    return passed, evidence


def _run_r4(
    config: MooseGateConfig,
    workspace: GateWorkspace,
    tools: GateTools,
    context: EvaluationContext,
    submission: SubmissionRecord,
) -> list[ExternalGateResult]:
    scope, _changed, scope_ok = _scope_result(
        config,
        workspace,
        tools,
        context,
        submission,
        required_paths=set(config.accepted_ranges),
    )
    results = [scope]
    if not scope_ok:
        results.extend(
            _blocked_gate(context, submission, gate_id, "authorized_edit_scope")
            for gate_id in config.required_gates
            if gate_id != "authorized_edit_scope"
        )
        return validate_gate_results(config, results)

    values_ok, value_evidence = _accepted_hit_values(config, workspace, tools)
    validation, check = _command_gate(
        config,
        "check_input",
        "input_validation",
        workspace,
        tools,
        context,
        submission,
    )
    results.append(validation)
    if not command_succeeded(check):
        results.extend(
            _blocked_gate(context, submission, gate_id, "input_validation")
            for gate_id in config.required_gates
            if gate_id not in {result.gate_id for result in results}
        )
        return validate_gate_results(config, results)

    _execution, run = _command_gate(
        config, "run", "bounded_completion", workspace, tools, context, submission
    )
    output = _combined_output(run)
    final_time = final_reported_time(output)
    progress_ok = bool(
        final_time is not None
        and config.minimum_progress_time is not None
        and final_time >= config.minimum_progress_time
    )
    complete = bool(
        command_succeeded(run)
        and final_time is not None
        and config.minimum_final_time is not None
        and final_time >= config.minimum_final_time
    )
    results.extend(
        [
            _gate(
                context,
                submission,
                "progress_beyond_failure",
                progress_ok,
                (
                    "transient advanced beyond the faulty breakdown time"
                    if progress_ok
                    else "transient did not advance beyond the faulty breakdown time"
                ),
                [f"final_reported_time:{final_time}"],
            ),
            _gate(
                context,
                submission,
                "bounded_completion",
                complete,
                (
                    "transient completed within evaluator limits"
                    if complete
                    else "transient did not complete within evaluator limits"
                ),
                _command_evidence("run", run),
            ),
        ]
    )
    removed = progress_ok and not contains_any(output, config.failure_signatures)
    results.append(
        _gate(
            context,
            submission,
            "target_failure_removed",
            removed,
            (
                "the transient SUBPC failure is absent"
                if removed
                else "the transient SUBPC failure remains"
            ),
        )
    )
    if complete:
        rows = _load_rows(config, workspace)
        constraint_ok, constraint_evidence = _check_metric_expectations(
            config, rows, "phase_constraint."
        )
        evolution_ok, evolution_evidence = _check_metric_expectations(
            config, rows, "early_evolution."
        )
        results.extend(
            [
                _gate(
                    context,
                    submission,
                    "phase_sum_constraint",
                    constraint_ok and values_ok,
                    (
                        "constraint and private repair ranges are satisfied"
                        if constraint_ok and values_ok
                        else "constraint or private repair ranges are violated"
                    ),
                    [*value_evidence, *constraint_evidence],
                ),
                _gate(
                    context,
                    submission,
                    "early_evolution_preservation",
                    evolution_ok,
                    (
                        "early transient evolution matches the reference"
                        if evolution_ok
                        else "early transient evolution changed"
                    ),
                    evolution_evidence,
                ),
            ]
        )
    else:
        results.extend(
            _blocked_gate(context, submission, gate_id, "bounded_completion")
            for gate_id in ("phase_sum_constraint", "early_evolution_preservation")
        )
    return validate_gate_results(config, results)


def generate_case_gates(
    config: MooseGateConfig,
    workspace: GateWorkspace,
    tools: GateTools,
    context: EvaluationContext,
    submission: SubmissionRecord,
) -> list[ExternalGateResult]:
    if config.case_id != submission.case_id:
        raise ValueError("gate configuration and submission case IDs must match")
    runners = {
        "r1_periodic_sideset": _run_r1,
        "r2_coupled_variable_wiring": _run_r2,
        "r3_fieldsplit_partition": _run_r3,
        "r4_lagrange_transient": _run_r4,
    }
    return runners[config.case_type](
        config,
        workspace,
        tools,
        context,
        submission,
    )
