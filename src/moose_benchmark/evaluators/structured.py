"""Deterministic evaluator for transitional structured responses."""

from __future__ import annotations

import json
from typing import Any

from ..comparison import compare, resolve_json_pointer
from ..contracts import (
    CaseContract,
    CaseKind,
    CaseResult,
    EvaluationContext,
    EvaluationSpec,
    ExternalGateResult,
    StructuredResponse,
    SubmissionRecord,
)
from ..loader import resolve_inside
from ..scoring import calculate_case_score
from .common import automatic_gates, contract_score, evaluation_gates


def _load_response(
    submission: SubmissionRecord,
    context: EvaluationContext,
) -> StructuredResponse:
    if submission.response is None:
        raise ValueError("structured submission is missing response.json")
    path = resolve_inside(context.submission_root, submission.response.path)
    return StructuredResponse.model_validate(json.loads(path.read_text(encoding="utf-8")))


def _score_criteria(document: dict[str, Any], criteria: list) -> tuple[float, list[dict]]:
    total = 0.0
    details = []
    for criterion in criteria:
        if criterion.json_pointer is None or criterion.comparator is None:
            raise ValueError(f"structured criterion is incomplete: {criterion.id}")
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


class StructuredClaimEvaluator:
    def evaluate(
        self,
        case: CaseContract,
        evaluation: EvaluationSpec,
        submission: SubmissionRecord,
        external_gates: list[ExternalGateResult],
        context: EvaluationContext,
        *,
        llm_client=None,
    ) -> CaseResult:
        del llm_client
        if evaluation.case_id != case.case_id or submission.case_id != case.case_id:
            raise ValueError("case, evaluation, and submission identities must match")
        if evaluation.evaluator != "structured_claim_v2":
            raise ValueError("structured evaluator received an incompatible specification")
        if case.case_kind == CaseKind.INTEGRATED_WORKFLOW:
            invalid_stages = [
                gate.id for gate in evaluation.hard_gates if gate.stage not in case.required_stages
            ]
            if invalid_stages:
                raise ValueError(
                    "integrated hard gates require valid workflow stages: "
                    + ", ".join(invalid_stages)
                )

        response = _load_response(submission, context)
        document = response.model_dump(mode="json")
        capability, capability_details = _score_criteria(document, evaluation.capability_criteria)
        evidence, evidence_details = _score_criteria(document, evaluation.evidence_criteria)
        automatic, _verified = automatic_gates(case, submission, context)
        contract, contract_details = contract_score(
            case,
            response,
            submission,
            artifacts_verified=automatic[0].passed,
        )
        gates = [
            *automatic,
            *evaluation_gates(
                evaluation,
                external_gates,
                context,
                document=document,
            ),
        ]
        score = calculate_case_score(
            capability,
            evidence,
            contract,
            [item.model_dump(mode="json") for item in gates],
            scoring_profile=case.scoring_profile,
        )
        first_failed_stage = None
        if case.case_kind == CaseKind.INTEGRATED_WORKFLOW:
            first_failed_stage = next(
                (item.stage for item in gates if not item.passed and item.stage is not None),
                None,
            )
        return _case_result(
            case,
            evaluation,
            submission,
            context,
            score,
            capability_details,
            evidence_details,
            contract_details,
            first_failed_stage,
        )


def _case_result(
    case: CaseContract,
    evaluation: EvaluationSpec,
    submission: SubmissionRecord,
    context: EvaluationContext,
    score: dict,
    capability_details: list[dict],
    evidence_details: list[dict],
    contract_details: dict,
    first_failed_stage: str | None,
) -> CaseResult:
    return CaseResult.model_validate(
        {
            "schema_version": "2.0",
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
            "run_record_sha256": context.run_record_sha256,
            "submitted_artifacts": submission.artifacts,
            **score,
            "criterion_details": {
                "capability": capability_details,
                "evidence": evidence_details,
                "contract": contract_details,
            },
            "evaluator_provenance": None,
            "first_failed_stage": first_failed_stage,
        }
    )
