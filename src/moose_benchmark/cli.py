"""Command-line interface for validating, scoring, and aggregating benchmark cases."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel, TypeAdapter, ValidationError

from .catalog.loader import load_coverage_config
from .catalog.report import build_catalog_report, format_catalog_report
from .catalog.validator import validate_catalog
from .contracts import (
    CaseResult,
    EvaluationContext,
    ExternalGateResult,
    ModelIdentity,
    ResponseMode,
    TokenUsage,
    UsageRecord,
)
from .evaluators import get_evaluator
from .llm import EvaluatorInfrastructureError, LLMClient, load_llm_config
from .loader import (
    case_bundle_paths,
    load_case,
    load_evaluation,
    load_manifest,
    load_model,
    load_submission_record,
    resolve_inside,
    sha256_file,
)
from .moose_gates import (
    GateInfrastructureError,
    MooseGateConfig,
    generate_case_gates,
    prepare_workspace,
    verify_tools,
)
from .runner import RunLimits, build_submission_record, run_moose_check
from .scoring import aggregate_results


def _write_json(data: BaseModel | dict | list, output: str | None) -> None:
    if isinstance(data, BaseModel):
        data = data.model_dump(mode="json")
    text = json.dumps(data, indent=2, sort_keys=True) + "\n"
    if output:
        target = Path(output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


def _write_text(text: str, output: str | None) -> None:
    if output:
        target = Path(output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


def validate_manifest(
    manifest_path: str | Path,
    *,
    include_disabled: bool = False,
) -> list[str]:
    manifest_path = Path(manifest_path).resolve()
    manifest = load_manifest(manifest_path)
    errors: list[str] = []
    root = manifest_path.parent
    base_problem_splits: dict[str, set[str]] = defaultdict(set)
    for ref in manifest.cases:
        if not ref.enabled and not include_disabled:
            continue
        try:
            if not ref.public_case.startswith("public/"):
                errors.append(f"{ref.case_id}: public_case must be under benchmark/public")
            if not ref.private_evaluation.startswith("private/"):
                errors.append(f"{ref.case_id}: private_evaluation must be under benchmark/private")
            case_path = resolve_inside(root, ref.public_case)
            evaluation_path = resolve_inside(root, ref.private_evaluation)
            case = load_case(case_path)
            evaluation = load_evaluation(evaluation_path)
            get_evaluator(evaluation.evaluator)
            gate_config_path = evaluation_path.parent / "gate-config.yaml"
            if gate_config_path.is_file():
                gate_config = load_model(gate_config_path, MooseGateConfig)
                external_ids = [
                    gate.id for gate in evaluation.hard_gates if gate.kind == "external"
                ]
                if gate_config.case_id != ref.case_id:
                    errors.append(f"{ref.case_id}: gate configuration case ID differs")
                if gate_config.required_gates != external_ids:
                    errors.append(
                        f"{ref.case_id}: gate configuration and evaluation hard gates differ"
                    )
            if (
                evaluation.evaluator == "semantic_rubric_v1"
                and case.submission.response_mode == ResponseMode.STRUCTURED_JSON
            ):
                errors.append(f"{ref.case_id}: semantic evaluator requires a free response")
            if (
                evaluation.evaluator == "structured_claim_v2"
                and case.submission.response_mode != ResponseMode.STRUCTURED_JSON
            ):
                errors.append(f"{ref.case_id}: structured evaluator requires structured_json")
            if case.case_id != ref.case_id or evaluation.case_id != ref.case_id:
                errors.append(f"{ref.case_id}: manifest, case, and evaluation IDs differ")
            if case.target.version.startswith("replace-with-"):
                errors.append(f"{ref.case_id}: target version is still a placeholder")
            base_problem_splits[case.base_problem_id].add(ref.split)
            case_root = case_path.parent
            prompt = resolve_inside(case_root, case.prompt_path)
            if not prompt.is_file():
                errors.append(f"{ref.case_id}: prompt does not exist: {prompt}")
            elif case.prompt_sha256 is None:
                errors.append(f"{ref.case_id}: prompt is missing a sha256")
            elif sha256_file(prompt) != case.prompt_sha256:
                errors.append(f"{ref.case_id}: prompt hash mismatch: {prompt}")
            for item in case.artifacts:
                artifact = resolve_inside(case_root, item.path)
                if not artifact.is_file():
                    errors.append(f"{ref.case_id}: referenced file does not exist: {artifact}")
                elif item.sha256 is None:
                    errors.append(f"{ref.case_id}: artifact is missing a sha256: {artifact}")
                elif sha256_file(artifact) != item.sha256:
                    errors.append(f"{ref.case_id}: artifact hash mismatch: {artifact}")
            for item in case.evidence_sources:
                evidence = resolve_inside(case_root, item.path)
                if not evidence.is_file():
                    errors.append(f"{ref.case_id}: referenced file does not exist: {evidence}")
                elif item.sha256 is None:
                    errors.append(f"{ref.case_id}: evidence is missing a sha256: {evidence}")
                elif sha256_file(evidence) != item.sha256:
                    errors.append(f"{ref.case_id}: evidence hash mismatch: {evidence}")
            if evaluation.reference_solution is not None:
                reference = resolve_inside(
                    evaluation_path.parent,
                    evaluation.reference_solution,
                )
                if not reference.is_file():
                    errors.append(f"{ref.case_id}: reference solution does not exist: {reference}")
        except Exception as exc:  # validation reports every case before failing
            errors.append(f"{ref.case_id}: {exc}")
    for base_problem_id, splits in sorted(base_problem_splits.items()):
        if len(splits) > 1:
            errors.append(
                f"{base_problem_id}: sibling cases cannot span dataset splits: {sorted(splits)}"
            )
    return errors


def _load_external_gates(
    path: str | None,
    *,
    private_case_root: Path,
) -> list[ExternalGateResult]:
    if not path:
        return []
    resolved = resolve_inside(private_case_root, path)
    data = json.loads(resolved.read_text(encoding="utf-8"))
    return TypeAdapter(list[ExternalGateResult]).validate_python(data)


def command_validate(args: argparse.Namespace) -> int:
    errors = validate_manifest(args.manifest, include_disabled=args.include_disabled)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    manifest = load_manifest(args.manifest)
    count = (
        len(manifest.cases)
        if args.include_disabled
        else sum(item.enabled for item in manifest.cases)
    )
    qualifier = "registered" if args.include_disabled else "enabled"
    print(f"validated {count} {qualifier} case(s) in {manifest.benchmark_id}")
    return 0


def command_score(args: argparse.Namespace) -> int:
    errors = validate_manifest(args.manifest, include_disabled=args.include_disabled)
    if errors:
        raise ValueError("manifest validation failed: " + "; ".join(errors))
    manifest = load_manifest(args.manifest)
    case_path, evaluation_path = case_bundle_paths(
        args.manifest,
        args.case_id,
        include_disabled=args.include_disabled,
    )
    case = load_case(case_path)
    evaluation = load_evaluation(evaluation_path)
    submission_root = Path(args.submission_dir).resolve()
    run_record_path = (
        Path(args.run_record).resolve() if args.run_record else submission_root / "run-record.json"
    )
    submission = load_submission_record(run_record_path)
    external_gates = _load_external_gates(
        args.external_gates,
        private_case_root=evaluation_path.parent,
    )
    evaluator = get_evaluator(evaluation.evaluator)
    context = EvaluationContext(
        benchmark_id=manifest.benchmark_id,
        benchmark_version=manifest.benchmark_version,
        submission_sha256=submission.submission_sha256,
        run_record_sha256=sha256_file(run_record_path),
        submission_root=submission_root,
        public_case_root=case_path.parent,
        private_case_root=evaluation_path.parent,
    )
    llm_client = None
    if evaluation.evaluator == "semantic_rubric_v1":
        if not args.llm_config:
            raise ValueError("--llm-config is required for semantic evaluation")
        llm_client = LLMClient(load_llm_config(args.llm_config))
    result = evaluator.evaluate(
        case,
        evaluation,
        submission,
        external_gates,
        context,
        llm_client=llm_client,
    )
    _write_json(result, args.output)
    return 0


def _parse_timestamp(value: str | None) -> datetime:
    if value is None:
        return datetime.now(UTC)
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamps must include a timezone")
    return parsed


def command_record_submission(args: argparse.Namespace) -> int:
    case_path, _evaluation_path = case_bundle_paths(
        args.manifest,
        args.case_id,
        include_disabled=args.include_disabled,
    )
    case = load_case(case_path)
    token_usage = None
    if any((args.input_tokens, args.output_tokens, args.total_tokens)):
        total_tokens = args.total_tokens or args.input_tokens + args.output_tokens
        token_usage = TokenUsage(
            input_tokens=args.input_tokens,
            output_tokens=args.output_tokens,
            total_tokens=total_tokens,
        )
    configuration = json.loads(args.model_configuration)
    if not isinstance(configuration, dict):
        raise ValueError("--model-configuration must be a JSON object")
    submission_root = Path(args.submission_dir).resolve()
    record = build_submission_record(
        case,
        submission_root,
        model=ModelIdentity(
            provider=args.model_provider,
            model=args.model,
            configuration=configuration,
        ),
        started_at=_parse_timestamp(args.started_at),
        finished_at=_parse_timestamp(args.finished_at),
        usage=UsageRecord(
            wall_time_seconds=args.wall_time,
            cpu_seconds=args.cpu_time,
            memory_mib=args.memory_mib,
            validation_attempts=args.validation_attempts,
            execution_attempts=args.execution_attempts,
            tokens=token_usage,
        ),
    )
    output = args.output or str(submission_root / "run-record.json")
    _write_json(record, output)
    return 0


def command_aggregate(args: argparse.Namespace) -> int:
    manifest = load_manifest(args.manifest)
    results = [
        CaseResult.model_validate(json.loads(Path(path).read_text(encoding="utf-8")))
        for path in args.results
    ]
    aggregate = aggregate_results(
        results,
        required_atomic_subcategories=manifest.required_atomic_subcategories,
        benchmark_id=manifest.benchmark_id,
        benchmark_version=manifest.benchmark_version,
    )
    _write_json(aggregate, args.output)
    return 0


def command_run_check(args: argparse.Namespace) -> int:
    result = run_moose_check(
        Path(args.executable),
        Path(args.case_root),
        args.input,
        RunLimits(args.wall_time, args.cpu_time, args.memory_mib),
    )
    _write_json(result.to_dict(), args.output)
    return (
        0
        if result.exit_code == 0
        and not result.timed_out
        and not result.output_limit_exceeded
        and not result.process_limit_exceeded
        else 1
    )


def command_generate_gates(args: argparse.Namespace) -> int:
    output_path = Path(args.output)
    errors = validate_manifest(args.manifest, include_disabled=args.include_disabled)
    if errors:
        raise ValueError("manifest validation failed: " + "; ".join(errors))
    manifest = load_manifest(args.manifest)
    case_path, evaluation_path = case_bundle_paths(
        args.manifest,
        args.case_id,
        include_disabled=args.include_disabled,
    )
    case = load_case(case_path)
    evaluation = load_evaluation(evaluation_path)
    config_path = evaluation_path.parent / "gate-config.yaml"
    if not config_path.is_file():
        raise GateInfrastructureError(f"private gate configuration is missing: {config_path}")
    config = load_model(config_path, MooseGateConfig)
    external_ids = [gate.id for gate in evaluation.hard_gates if gate.kind == "external"]
    if external_ids != config.required_gates:
        raise GateInfrastructureError(
            "evaluation hard gates do not match gate-config required_gates"
        )
    if len(case.submission.required_artifacts) != 1:
        raise ValueError("gate generation requires exactly one submission artifact")
    submission_root = Path(args.submission_dir).resolve()
    run_record_path = submission_root / "run-record.json"
    submission = load_submission_record(run_record_path)
    context = EvaluationContext(
        benchmark_id=manifest.benchmark_id,
        benchmark_version=manifest.benchmark_version,
        submission_sha256=submission.submission_sha256,
        run_record_sha256=sha256_file(run_record_path),
        submission_root=submission_root,
        public_case_root=case_path.parent,
        private_case_root=evaluation_path.parent,
    )
    tools = verify_tools(Path(args.moose_dir), Path(args.executable), config)
    artifact_path = case.submission.required_artifacts[0].path
    with prepare_workspace(
        evaluation_path.parent,
        submission_root,
        submission,
        artifact_path,
        config,
    ) as workspace:
        gates = generate_case_gates(config, workspace, tools, context, submission)
    _write_json([gate.model_dump(mode="json") for gate in gates], str(output_path))
    return 0


def command_catalog_validate(args: argparse.Namespace) -> int:
    result = validate_catalog(args.repo_root, strict=args.strict)
    if result.errors:
        for error in result.errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    mode = "strict" if args.strict else "standard"
    print(f"validated {len(result.documents)} catalog case(s) in {mode} mode")
    return 0


def command_catalog_report(args: argparse.Namespace) -> int:
    validation = validate_catalog(args.repo_root)
    if validation.errors:
        for error in validation.errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    repo_root = Path(args.repo_root).resolve()
    coverage = load_coverage_config(repo_root / "catalog/coverage.yaml")
    report = build_catalog_report(validation, coverage)
    if args.format == "json":
        _write_json(report, args.output)
    else:
        _write_text(format_catalog_report(report), args.output)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="moose-benchmark")
    subparsers = parser.add_subparsers(dest="command", required=True)

    catalog = subparsers.add_parser("catalog", help="manage the collaboration catalog")
    catalog_commands = catalog.add_subparsers(dest="catalog_command", required=True)

    catalog_validate = catalog_commands.add_parser(
        "validate",
        help="validate catalog records and benchmark consistency",
    )
    catalog_validate.add_argument("--strict", action="store_true")
    catalog_validate.add_argument("--repo-root", default=".")
    catalog_validate.set_defaults(handler=command_catalog_validate)

    catalog_report = catalog_commands.add_parser(
        "report",
        help="report catalog development status",
    )
    catalog_report.add_argument("--format", choices=("text", "json"), default="text")
    catalog_report.add_argument("--output")
    catalog_report.add_argument("--repo-root", default=".")
    catalog_report.set_defaults(handler=command_catalog_report)

    validate = subparsers.add_parser("validate", help="validate a benchmark manifest")
    validate.add_argument("manifest")
    validate.add_argument(
        "--include-disabled",
        action="store_true",
        help="also validate disabled development cases",
    )
    validate.set_defaults(handler=command_validate)

    score = subparsers.add_parser("score", help="score one submission")
    score.add_argument("--manifest", required=True)
    score.add_argument("--case-id", required=True)
    score.add_argument("--submission-dir", required=True)
    score.add_argument(
        "--run-record",
        help="runner-owned record (defaults to <submission-dir>/run-record.json)",
    )
    score.add_argument("--llm-config", help="private semantic-judge configuration")
    score.add_argument(
        "--external-gates",
        help="evaluator-only gate file relative to the private case directory",
    )
    score.add_argument("--output")
    score.add_argument(
        "--include-disabled",
        action="store_true",
        help="allow scoring a disabled development case",
    )
    score.set_defaults(handler=command_score)

    record = subparsers.add_parser(
        "record-submission",
        help="capture runner-owned response, artifact, model, and usage metadata",
    )
    record.add_argument("--manifest", required=True)
    record.add_argument("--case-id", required=True)
    record.add_argument("--submission-dir", required=True)
    record.add_argument("--model-provider", required=True)
    record.add_argument("--model", required=True)
    record.add_argument("--model-configuration", default="{}")
    record.add_argument("--started-at")
    record.add_argument("--finished-at")
    record.add_argument("--wall-time", type=float, default=0)
    record.add_argument("--cpu-time", type=float, default=0)
    record.add_argument("--memory-mib", type=float, default=0)
    record.add_argument("--validation-attempts", type=int, default=0)
    record.add_argument("--execution-attempts", type=int, default=0)
    record.add_argument("--input-tokens", type=int, default=0)
    record.add_argument("--output-tokens", type=int, default=0)
    record.add_argument("--total-tokens", type=int, default=0)
    record.add_argument("--output")
    record.add_argument(
        "--include-disabled",
        action="store_true",
        help="allow recording a disabled development case",
    )
    record.set_defaults(handler=command_record_submission)

    generate = subparsers.add_parser(
        "generate-gates",
        help="run protected MOOSE gates for one recorded submission",
    )
    generate.add_argument("--manifest", required=True)
    generate.add_argument("--case-id", required=True)
    generate.add_argument("--submission-dir", required=True)
    generate.add_argument("--moose-dir", required=True)
    generate.add_argument("--executable", required=True)
    generate.add_argument("--output", required=True)
    generate.add_argument(
        "--include-disabled",
        action="store_true",
        help="allow gate generation for a disabled development case",
    )
    generate.set_defaults(handler=command_generate_gates)

    aggregate = subparsers.add_parser("aggregate", help="aggregate case-result JSON files")
    aggregate.add_argument("results", nargs="+")
    aggregate.add_argument("--manifest", required=True)
    aggregate.add_argument("--output")
    aggregate.set_defaults(handler=command_aggregate)

    run_check = subparsers.add_parser("run-check", help="run a bounded MOOSE --check-input")
    run_check.add_argument("--executable", required=True)
    run_check.add_argument("--case-root", required=True)
    run_check.add_argument("--input", required=True)
    run_check.add_argument("--wall-time", type=int, default=60)
    run_check.add_argument("--cpu-time", type=int, default=30)
    run_check.add_argument("--memory-mib", type=int, default=2048)
    run_check.add_argument("--output")
    run_check.set_defaults(handler=command_run_check)
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        raise SystemExit(args.handler(args))
    except (
        EvaluatorInfrastructureError,
        GateInfrastructureError,
        ValidationError,
        ValueError,
        KeyError,
        OSError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
