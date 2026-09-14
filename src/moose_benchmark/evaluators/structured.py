"""Deterministic evaluator for structured benchmark claims."""

from __future__ import annotations

from typing import Any

from ..comparison import MISSING, compare, resolve_json_pointer
from ..contracts import (
    CaseContract,
    CaseKind,
    CaseResult,
    EvaluationContext,
    EvaluationSpec,
    ExternalGateResult,
    SubmissionEnvelope,
)
from ..loader import resolve_inside, sha256_file
from ..scoring import calculate_case_score


def _score_criteria(document: dict[str, Any], criteria: list) -> tuple[float, list[dict]]:
    total = 0.0
    details = []
    for criterion in criteria:
        actual = resolve_json_pointer(document, criterion.json_pointer)
        fraction, reason = compare(
            actual,
            criterion.expected,
            criterion.comparator,
            absolute_tolerance=criterion.absolute_tolerance,
            relative_tolerance=criterion.relative_tolerance,
        )
        contribution = criterion.weight * fraction
        total += contribution
        details.append(
            {
                "id": criterion.id,
                "score_fraction": round(fraction, 4),
                "weight": criterion.weight,
                "weighted_contribution": round(contribution, 4),
                "reason": reason,
            }
        )
    return round(100 * total, 4), details


def _contract_score(
    case: CaseContract,
    submission: SubmissionEnvelope,
    *,
    artifacts_verified: bool,
    verified_artifact_roles: set[str],
) -> tuple[float, dict]:
    submission_data = submission.model_dump(mode="json")
    required_claim_results = [
        resolve_json_pointer(submission_data, pointer) is not MISSING
        for pointer in case.submission.required_claim_paths
    ]
    required_claim_score = (
        sum(required_claim_results) / len(required_claim_results) if required_claim_results else 1.0
    )

    known_evidence_ids = {item.id for item in case.evidence_sources}
    known_evidence_ids.update(item.id for item in case.artifacts)
    known_evidence_ids.update(verified_artifact_roles)
    supplied_evidence_ids = {item.source_id for item in submission.evidence}
    evidence_ok = supplied_evidence_ids <= known_evidence_ids
    if case.submission.evidence_required:
        evidence_ok = evidence_ok and bool(submission.evidence)

    source_hashes = {
        item.id: item.sha256
        for item in [*case.artifacts, *case.evidence_sources]
        if item.sha256 is not None
    }
    source_hashes.update(
        {
            item.role: item.sha256
            for item in submission.artifacts
            if item.role in verified_artifact_roles
        }
    )
    evidence_hashes_ok = all(
        claim.artifact_sha256 is None or source_hashes.get(claim.source_id) == claim.artifact_sha256
        for claim in submission.evidence
    )
    evidence_ok = evidence_ok and evidence_hashes_ok

    artifact_roles = {item.role for item in submission.artifacts}
    artifact_ok = (
        artifacts_verified
        and len(submission.artifacts) <= case.submission.maximum_artifacts
        and set(case.submission.required_artifact_roles) <= artifact_roles
    )
    if not case.submission.artifacts_allowed:
        artifact_ok = artifact_ok and not submission.artifacts

    score = 40.0
    score += 30 * required_claim_score
    score += 15 * float(evidence_ok)
    score += 15 * float(artifact_ok)
    return round(score, 4), {
        "identity": True,
        "required_claim_fraction": round(required_claim_score, 4),
        "evidence_references_valid": evidence_ok,
        "evidence_hashes_valid": evidence_hashes_ok,
        "artifact_contract_valid": artifact_ok,
    }


def _automatic_gates(
    case: CaseContract,
    submission: SubmissionEnvelope,
    context: EvaluationContext,
) -> tuple[list[dict], set[str]]:
    artifact_roles = {item.role for item in submission.artifacts}
    artifact_policy_passed = case.submission.artifacts_allowed or not submission.artifacts
    artifact_policy_passed = (
        artifact_policy_passed
        and len(submission.artifacts) <= case.submission.maximum_artifacts
        and set(case.submission.required_artifact_roles) <= artifact_roles
    )

    verified_roles: set[str] = set()
    artifact_evidence: list[str] = []
    if artifact_policy_passed:
        for artifact in submission.artifacts:
            try:
                path = resolve_inside(context.artifact_root, artifact.path)
                if not path.is_file():
                    artifact_evidence.append(f"missing:{artifact.path}")
                    artifact_policy_passed = False
                    continue
                if sha256_file(path) != artifact.sha256:
                    artifact_evidence.append(f"hash_mismatch:{artifact.path}")
                    artifact_policy_passed = False
                    continue
                verified_roles.add(artifact.role)
            except (OSError, ValueError) as exc:
                artifact_evidence.append(f"invalid:{artifact.path}:{exc}")
                artifact_policy_passed = False

    usage = submission.usage
    budget = case.budget
    usage_passed = (
        usage.wall_time_seconds <= budget.wall_time_seconds
        and usage.cpu_seconds <= budget.cpu_seconds
        and usage.validation_attempts <= budget.validation_attempts
        and usage.execution_attempts <= budget.execution_attempts
    )
    return [
        {
            "id": "artifact_policy",
            "passed": artifact_policy_passed,
            "detail": (
                "submitted artifacts follow the public case contract"
                if artifact_policy_passed
                else "submission includes prohibited, excess, missing, or unverified artifacts"
            ),
            "evidence": artifact_evidence,
            "stage": None,
        },
        {
            "id": "declared_usage_budget",
            "passed": usage_passed,
            "detail": (
                "declared usage remains within the public case budget"
                if usage_passed
                else "declared usage exceeds the public case budget"
            ),
            "evidence": [],
            "stage": None,
        },
    ], verified_roles


class StructuredClaimEvaluator:
    def evaluate(
        self,
        case: CaseContract,
        evaluation: EvaluationSpec,
        submission: SubmissionEnvelope,
        external_gates: list[ExternalGateResult],
        context: EvaluationContext,
    ) -> CaseResult:
        if evaluation.case_id != case.case_id:
            raise ValueError("evaluation case_id does not match the public case")
        if (
            submission.case_id != case.case_id
            or submission.track != case.track
            or submission.subcategory != case.subcategory
        ):
            raise ValueError("submission identity does not match the selected case")
        if case.case_kind == CaseKind.INTEGRATED_WORKFLOW:
            invalid_stages = [
                gate.id for gate in evaluation.hard_gates if gate.stage not in case.required_stages
            ]
            if invalid_stages:
                raise ValueError(
                    "integrated hard gates require valid workflow stages: "
                    + ", ".join(invalid_stages)
                )

        document = submission.model_dump(mode="json")
        capability, capability_details = _score_criteria(document, evaluation.capability_criteria)
        evidence, evidence_details = _score_criteria(document, evaluation.evidence_criteria)

        gate_results, verified_artifact_roles = _automatic_gates(case, submission, context)
        contract, contract_details = _contract_score(
            case,
            submission,
            artifacts_verified=gate_results[0]["passed"],
            verified_artifact_roles=verified_artifact_roles,
        )

        external_ids = [item.gate_id for item in external_gates]
        if len(external_ids) != len(set(external_ids)):
            raise ValueError("external gate result IDs must be unique")
        expected_external_ids = {
            gate.id for gate in evaluation.hard_gates if gate.kind == "external"
        }
        unexpected_external_ids = set(external_ids) - expected_external_ids
        if unexpected_external_ids:
            raise ValueError(
                "unexpected external gate results: " + ", ".join(sorted(unexpected_external_ids))
            )

        external_by_id = {item.gate_id: item for item in external_gates}
        for gate in evaluation.hard_gates:
            if gate.kind == "field_equals":
                actual = resolve_json_pointer(document, gate.json_pointer or "")
                passed = actual is not MISSING and actual == gate.expected
                gate_results.append(
                    {
                        "id": gate.id,
                        "passed": passed,
                        "detail": gate.description,
                        "evidence": [],
                        "stage": gate.stage,
                    }
                )
            else:
                result = external_by_id.get(gate.id)
                provenance_matches = bool(
                    result
                    and result.benchmark_id == context.benchmark_id
                    and result.benchmark_version == context.benchmark_version
                    and result.case_id == case.case_id
                    and result.submission_sha256 == context.submission_sha256
                )
                gate_results.append(
                    {
                        "id": gate.id,
                        "passed": bool(result and provenance_matches and result.passed),
                        "detail": (
                            result.detail
                            if provenance_matches
                            else (
                                "external gate provenance does not match this submission"
                                if result
                                else "required external gate result missing"
                            )
                        ),
                        "evidence": result.evidence if provenance_matches else [],
                        "stage": gate.stage,
                    }
                )

        score = calculate_case_score(capability, evidence, contract, gate_results)
        first_failed_stage = None
        if case.case_kind == CaseKind.INTEGRATED_WORKFLOW:
            first_failed_stage = next(
                (
                    item["stage"]
                    for item in gate_results
                    if not item["passed"] and item["stage"] is not None
                ),
                None,
            )
        return CaseResult.model_validate(
            {
                "schema_version": "1.0",
                "benchmark_id": context.benchmark_id,
                "benchmark_version": context.benchmark_version,
                "evaluator": evaluation.evaluator,
                "case_id": case.case_id,
                "case_kind": case.case_kind.value,
                "track": case.track.value if case.track else None,
                "subcategory": case.subcategory,
                "difficulty": case.difficulty.value,
                "base_problem_id": case.base_problem_id,
                "physics_domains": case.physics_domains,
                "submission_sha256": context.submission_sha256,
                "submitted_artifacts": submission.artifacts,
                **score,
                "criterion_details": {
                    "capability": capability_details,
                    "evidence": evidence_details,
                    "contract": contract_details,
                },
                "first_failed_stage": first_failed_stage,
            }
        )
