"""Shared submission validation and evaluator result helpers."""

from __future__ import annotations

from typing import Any

from ..comparison import MISSING, resolve_json_pointer
from ..contracts import (
    CaseContract,
    EvaluationContext,
    EvaluationSpec,
    ExternalGateResult,
    GateResult,
    RecordedArtifact,
    ResponseMode,
    SubmissionRecord,
)
from ..loader import (
    discover_submission_artifact_paths,
    resolve_inside,
    sha256_file,
    sha256_submission_content,
)


def automatic_gates(
    case: CaseContract,
    submission: SubmissionRecord,
    context: EvaluationContext,
) -> tuple[list[GateResult], list[RecordedArtifact]]:
    expected_response = (
        "response.json"
        if case.submission.response_mode == ResponseMode.STRUCTURED_JSON
        else "response.md"
    )
    expected_media_type = (
        "application/json"
        if case.submission.response_mode == ResponseMode.STRUCTURED_JSON
        else "text/markdown"
    )
    evidence: list[str] = []
    integrity_ok = (
        submission.case_id == case.case_id
        and submission.submission_sha256 == context.submission_sha256
    )
    response_required = case.submission.response_mode != ResponseMode.ARTIFACT
    if response_required and submission.response is None:
        integrity_ok = False
        evidence.append(f"missing:{expected_response}")
    if submission.response is not None:
        response_path = resolve_inside(context.submission_root, submission.response.path)
        response_ok = (
            submission.response.path == expected_response
            and submission.response.media_type == expected_media_type
            and response_path.is_file()
            and response_path.stat().st_size == submission.response.size_bytes
            and sha256_file(response_path) == submission.response.sha256
        )
        integrity_ok = integrity_ok and response_ok
        if not response_ok:
            evidence.append(f"invalid_response:{submission.response.path}")

    required = {(item.role, item.path) for item in case.submission.required_artifacts}
    supplied = {(item.role, item.path) for item in submission.artifacts}
    integrity_ok = (
        integrity_ok
        and required == supplied
        and len(submission.artifacts) <= case.submission.maximum_artifacts
    )
    try:
        discovered_paths = set(discover_submission_artifact_paths(context.submission_root))
    except (OSError, ValueError) as exc:
        integrity_ok = False
        discovered_paths = set()
        evidence.append(f"artifact_discovery_failed:{exc}")
    recorded_artifact_paths = {
        item.path for item in submission.artifacts if item.path.startswith("artifacts/")
    }
    if discovered_paths != recorded_artifact_paths:
        integrity_ok = False
        evidence.append("recorded_artifacts_do_not_match_discovered_files")
    verified: list[RecordedArtifact] = []
    for artifact in submission.artifacts:
        path = resolve_inside(context.submission_root, artifact.path)
        valid = (
            path.is_file()
            and path.stat().st_size == artifact.size_bytes
            and sha256_file(path) == artifact.sha256
        )
        integrity_ok = integrity_ok and valid
        if valid:
            verified.append(artifact)
        else:
            evidence.append(f"invalid_artifact:{artifact.path}")
    try:
        content_hash = sha256_submission_content(
            context.submission_root,
            submission.response,
            submission.artifacts,
        )
    except (OSError, ValueError):
        integrity_ok = False
    else:
        integrity_ok = integrity_ok and content_hash == submission.submission_sha256

    usage = submission.usage
    budget = case.budget
    budget_ok = (
        usage.wall_time_seconds <= budget.wall_time_seconds
        and usage.cpu_seconds <= budget.cpu_seconds
        and usage.memory_mib <= budget.memory_mib
        and usage.validation_attempts <= budget.validation_attempts
        and usage.execution_attempts <= budget.execution_attempts
    )
    return [
        GateResult(
            id="submission_integrity",
            passed=integrity_ok,
            detail=(
                "runner-owned response and artifacts passed integrity checks"
                if integrity_ok
                else "runner-owned response or artifact integrity validation failed"
            ),
            evidence=evidence,
        ),
        GateResult(
            id="resource_budget",
            passed=budget_ok,
            detail=(
                "runner-measured usage remains within the public budget"
                if budget_ok
                else "runner-measured usage exceeds the public budget"
            ),
        ),
    ], verified


def contract_score(
    case: CaseContract,
    response,
    submission: SubmissionRecord,
    *,
    artifacts_verified: bool,
) -> tuple[float, dict]:
    document = response.model_dump(mode="json")
    required_claim_results = [
        resolve_json_pointer(document, pointer) is not MISSING
        for pointer in case.submission.required_claim_paths
    ]
    required_claim_score = (
        sum(required_claim_results) / len(required_claim_results) if required_claim_results else 1.0
    )

    known_evidence_ids = {item.id for item in case.evidence_sources}
    known_evidence_ids.update(item.id for item in case.artifacts)
    known_evidence_ids.update(item.role for item in submission.artifacts)
    supplied_evidence_ids = {item.source_id for item in response.evidence}
    evidence_ok = supplied_evidence_ids <= known_evidence_ids
    if case.submission.evidence_required:
        evidence_ok = evidence_ok and bool(response.evidence)

    supplied_artifacts = {(item.role, item.path) for item in submission.artifacts}
    required_artifacts = {(item.role, item.path) for item in case.submission.required_artifacts}
    artifact_ok = (
        artifacts_verified
        and required_artifacts <= supplied_artifacts
        and len(submission.artifacts) <= case.submission.maximum_artifacts
    )
    score = 40.0 + 30 * required_claim_score
    score += 15 * float(evidence_ok)
    score += 15 * float(artifact_ok)
    return round(score, 4), {
        "runner_identity": True,
        "required_claim_fraction": round(required_claim_score, 4),
        "evidence_references_valid": evidence_ok,
        "artifact_contract_valid": artifact_ok,
    }


def evaluation_gates(
    evaluation: EvaluationSpec,
    external_gates: list[ExternalGateResult],
    context: EvaluationContext,
    *,
    document: dict[str, Any] | None = None,
) -> list[GateResult]:
    external_ids = [item.gate_id for item in external_gates]
    if len(external_ids) != len(set(external_ids)):
        raise ValueError("external gate result IDs must be unique")
    expected_external_ids = {gate.id for gate in evaluation.hard_gates if gate.kind == "external"}
    unexpected = set(external_ids) - expected_external_ids
    if unexpected:
        raise ValueError("unexpected external gate results: " + ", ".join(sorted(unexpected)))

    external_by_id = {item.gate_id: item for item in external_gates}
    results = []
    for gate in evaluation.hard_gates:
        if gate.kind == "field_equals":
            if document is None:
                raise ValueError("field_equals gates require a structured response")
            actual = resolve_json_pointer(document, gate.json_pointer or "")
            results.append(
                GateResult(
                    id=gate.id,
                    passed=actual is not MISSING and actual == gate.expected,
                    detail=gate.description,
                    stage=gate.stage,
                )
            )
            continue
        result = external_by_id.get(gate.id)
        provenance_matches = bool(
            result
            and result.schema_version == "2.0"
            and result.benchmark_id == context.benchmark_id
            and result.benchmark_version == context.benchmark_version
            and result.case_id == evaluation.case_id
            and result.submission_sha256 == context.submission_sha256
        )
        results.append(
            GateResult(
                id=gate.id,
                passed=bool(result and provenance_matches and result.passed),
                detail=(
                    result.detail
                    if provenance_matches
                    else (
                        "external gate provenance does not match this submission"
                        if result
                        else "required external gate result missing"
                    )
                ),
                evidence=result.evidence if provenance_matches else [],
                stage=gate.stage,
            )
        )
    return results
