"""Command-line interface for validating, scoring, and aggregating benchmark cases."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

from pydantic import BaseModel, TypeAdapter, ValidationError

from .contracts import CaseResult, EvaluationContext, ExternalGateResult
from .evaluators import get_evaluator
from .loader import (
    case_bundle_paths,
    load_case,
    load_evaluation,
    load_manifest,
    load_submission,
    resolve_inside,
    sha256_file,
    sha256_model,
)
from .runner import RunLimits, run_moose_check
from .scoring import aggregate_results


def _write_json(data: BaseModel | dict, output: str | None) -> None:
    if isinstance(data, BaseModel):
        data = data.model_dump(mode="json")
    text = json.dumps(data, indent=2, sort_keys=True) + "\n"
    if output:
        target = Path(output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


def validate_manifest(manifest_path: str | Path) -> list[str]:
    manifest_path = Path(manifest_path).resolve()
    manifest = load_manifest(manifest_path)
    errors: list[str] = []
    root = manifest_path.parent
    base_problem_splits: dict[str, set[str]] = defaultdict(set)
    for ref in manifest.cases:
        if not ref.enabled:
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
    errors = validate_manifest(args.manifest)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    manifest = load_manifest(args.manifest)
    enabled = sum(item.enabled for item in manifest.cases)
    print(f"validated {enabled} enabled case(s) in {manifest.benchmark_id}")
    return 0


def command_score(args: argparse.Namespace) -> int:
    errors = validate_manifest(args.manifest)
    if errors:
        raise ValueError("manifest validation failed: " + "; ".join(errors))
    manifest = load_manifest(args.manifest)
    case_path, evaluation_path = case_bundle_paths(args.manifest, args.case_id)
    case = load_case(case_path)
    evaluation = load_evaluation(evaluation_path)
    submission = load_submission(args.submission)
    external_gates = _load_external_gates(
        args.external_gates,
        private_case_root=evaluation_path.parent,
    )
    evaluator = get_evaluator(evaluation.evaluator)
    artifact_root = (
        Path(args.artifact_root).resolve()
        if args.artifact_root
        else Path(args.submission).resolve().parent
    )
    context = EvaluationContext(
        benchmark_id=manifest.benchmark_id,
        benchmark_version=manifest.benchmark_version,
        submission_sha256=sha256_model(submission),
        artifact_root=artifact_root,
    )
    result = evaluator.evaluate(case, evaluation, submission, external_gates, context)
    _write_json(result, args.output)
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
    return 0 if result.exit_code == 0 and not result.timed_out else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="moose-benchmark")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="validate a benchmark manifest")
    validate.add_argument("manifest")
    validate.set_defaults(handler=command_validate)

    score = subparsers.add_parser("score", help="score one submission")
    score.add_argument("--manifest", required=True)
    score.add_argument("--case-id", required=True)
    score.add_argument("--submission", required=True)
    score.add_argument(
        "--external-gates",
        help="evaluator-only gate file relative to the private case directory",
    )
    score.add_argument(
        "--artifact-root",
        help="root for submitted artifact paths (defaults to the submission directory)",
    )
    score.add_argument("--output")
    score.set_defaults(handler=command_score)

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
    except (ValidationError, ValueError, KeyError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
