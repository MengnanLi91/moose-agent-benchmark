"""Deterministic evaluator for manufactured-solution refinement claims."""

from __future__ import annotations

import json
import math
from typing import Any

from ..contracts import (
    CaseContract,
    CaseResult,
    EvaluationContext,
    EvaluationSpec,
    ExternalGateResult,
    MmsExecutionMeasurement,
    MmsReferenceData,
    MmsResponse,
    MmsTask,
    SubmissionRecord,
)
from ..loader import load_model, resolve_inside
from ..moose_gates.metrics import observed_orders, values_within_tolerance
from ..scoring import calculate_case_score
from .common import automatic_gates, contract_score, evaluation_gates


def _load_response(
    submission: SubmissionRecord,
    context: EvaluationContext,
) -> MmsResponse:
    if submission.response is None:
        raise ValueError("MMS submission is missing response.json")
    path = resolve_inside(context.submission_root, submission.response.path)
    return MmsResponse.model_validate(json.loads(path.read_text(encoding="utf-8")))


def _load_reference(
    evaluation: EvaluationSpec,
    context: EvaluationContext,
) -> MmsReferenceData:
    if evaluation.reference_data is None:
        raise ValueError("MMS evaluation is missing reference_data")
    path = resolve_inside(context.private_case_root, evaluation.reference_data)
    return load_model(path, MmsReferenceData)


def _load_measurement(
    external_gates: list[ExternalGateResult],
    context: EvaluationContext,
) -> MmsExecutionMeasurement | None:
    measurements = [
        gate.mms_measurement for gate in external_gates if gate.mms_measurement is not None
    ]
    if not measurements:
        return None
    if len(measurements) != 1:
        raise ValueError("MMS implementation scoring accepts one protected measurement")
    measurement = measurements[0]
    if (
        measurement.case_id != context.public_case_root.name
        or measurement.submission_sha256 != context.submission_sha256
    ):
        raise ValueError("protected MMS measurement provenance does not match the submission")
    return measurement


def _zero_details(criteria: list) -> list[dict[str, Any]]:
    return [
        {
            "id": criterion.id,
            "score_fraction": 0.0,
            "weight": criterion.weight,
            "weighted_contribution": 0.0,
        }
        for criterion in criteria
    ]


def _criterion_weights(criteria: list) -> dict[str, float]:
    return {criterion.id: criterion.weight for criterion in criteria}


def _fraction(results: list[bool]) -> float:
    return sum(results) / len(results) if results else 1.0


def _close(actual: float, expected: float, tolerance) -> bool:
    return values_within_tolerance(
        actual,
        expected,
        absolute=tolerance.absolute,
        relative=tolerance.relative,
    )


def _score_capability(
    response: MmsResponse,
    measurement: MmsExecutionMeasurement,
    reference: MmsReferenceData,
    evaluation: EvaluationSpec,
) -> tuple[float, list[dict[str, Any]]]:
    claim = response.claim
    norm_fraction = _fraction(
        [
            claim.norm == measurement.norm,
            claim.refinement_parameter == measurement.refinement_parameter,
        ]
    )
    reported_runs = {run.level: run for run in claim.runs}
    error_checks: list[bool] = []
    for expected_run in measurement.runs:
        actual_run = reported_runs.get(expected_run.level)
        for field, expected in expected_run.errors.items():
            actual = actual_run.errors.get(field) if actual_run else None
            error_checks.append(
                actual is not None and _close(actual, expected, reference.error_tolerance)
            )
    order_checks = [
        _close(actual, expected, reference.order_tolerance)
        for field, expected_values in measurement.observed_orders.items()
        for actual, expected in zip(
            claim.observed_orders.get(field, []),
            expected_values,
            strict=False,
        )
    ]
    expected_order_checks = [
        _close(
            claim.expected_order.get(field, math.nan),
            expected,
            reference.order_tolerance,
        )
        for field, expected in measurement.expected_order.items()
    ]
    regime_checks = [
        claim.asymptotic_regime.get(field) is expected
        for field, expected in measurement.asymptotic_regime.items()
    ]
    fractions = {
        "norm_and_refinement": norm_fraction,
        "error_sequence": _fraction(error_checks),
        "observed_orders": _fraction(order_checks),
        "asymptotic_assessment": _fraction([*expected_order_checks, *regime_checks]),
        "verdict": float(claim.verdict == measurement.verdict),
    }
    weights = _criterion_weights(evaluation.capability_criteria)
    details = [
        {
            "id": criterion_id,
            "score_fraction": round(fraction, 4),
            "weight": weights[criterion_id],
            "weighted_contribution": round(weights[criterion_id] * fraction, 4),
        }
        for criterion_id, fraction in fractions.items()
    ]
    score = 100 * sum(weights[item] * fraction for item, fraction in fractions.items())
    return round(score, 4), details


def _score_evidence(
    case: CaseContract,
    response: MmsResponse,
    measurement: MmsExecutionMeasurement,
    reference: MmsReferenceData,
    evaluation: EvaluationSpec,
    submission: SubmissionRecord,
) -> tuple[float, list[dict[str, Any]]]:
    claim = response.claim
    expected_runs = {run.level: run for run in measurement.runs}
    trace_checks: list[bool] = []
    for run in claim.runs:
        expected = expected_runs.get(run.level)
        trace_checks.extend(
            [
                expected is not None,
                bool(expected and math.isclose(run.parameter, expected.parameter)),
                bool(expected and run.controls == expected.controls),
            ]
        )

    arithmetic_checks: list[bool] = []
    parameters = [run.parameter for run in claim.runs]
    for field, reported in claim.observed_orders.items():
        try:
            recomputed = observed_orders(
                parameters,
                [run.errors[field] for run in claim.runs],
            )
        except (KeyError, ValueError):
            arithmetic_checks.extend([False] * 3)
            continue
        arithmetic_checks.extend(
            _close(actual, expected, reference.order_tolerance)
            for actual, expected in zip(reported, recomputed, strict=True)
        )

    expected_sources = {item.id for item in case.artifacts}
    expected_sources.update(item.role for item in submission.artifacts)
    supplied_sources = {item.source_id for item in response.evidence}
    source_fraction = (
        len(expected_sources & supplied_sources) / len(expected_sources)
        if expected_sources
        else 1.0
    )
    fractions = {
        "refinement_trace": _fraction(trace_checks),
        "arithmetic_consistency": _fraction(arithmetic_checks),
        "source_binding": source_fraction,
    }
    weights = _criterion_weights(evaluation.evidence_criteria)
    details = [
        {
            "id": criterion_id,
            "score_fraction": round(fraction, 4),
            "weight": weights[criterion_id],
            "weighted_contribution": round(weights[criterion_id] * fraction, 4),
        }
        for criterion_id, fraction in fractions.items()
    ]
    score = 100 * sum(weights[item] * fraction for item, fraction in fractions.items())
    return round(score, 4), details


def _failure_category(
    gates: list,
    capability_details: list[dict[str, Any]],
    evidence_details: list[dict[str, Any]],
) -> str | None:
    failed_gate_ids = {gate.id for gate in gates if not gate.passed}
    if "physics_conformance" in failed_gate_ids:
        return "input_construction"
    if "successful_moose_runs" in failed_gate_ids:
        return "execution"
    if "required_convergence" in failed_gate_ids:
        return "convergence_calculation"
    if failed_gate_ids & {
        "submission_integrity",
        "resource_budget",
        "complete_refinement_sequence",
        "resource_compliance",
    }:
        return "evidence_integrity"
    if failed_gate_ids & {"protected_error_oracle", "reported_values_match"}:
        return "error_calculation"

    capability_by_id = {item["id"]: item["score_fraction"] for item in capability_details}
    evidence_by_id = {item["id"]: item["score_fraction"] for item in evidence_details}
    if capability_by_id.get("error_sequence", 1.0) < 1.0:
        return "error_calculation"
    if (
        capability_by_id.get("observed_orders", 1.0) < 1.0
        or evidence_by_id.get("arithmetic_consistency", 1.0) < 1.0
    ):
        return "convergence_calculation"
    if (
        capability_by_id.get("asymptotic_assessment", 1.0) < 1.0
        or capability_by_id.get("verdict", 1.0) < 1.0
    ):
        return "interpretation"
    if any(item["score_fraction"] < 1.0 for item in evidence_details):
        return "evidence_integrity"
    return None


class MmsClaimEvaluator:
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
        if evaluation.evaluator != "mms_claim_v1":
            raise ValueError("MMS evaluator received an incompatible specification")
        if case.mms_task != MmsTask.IMPLEMENTATION:
            raise ValueError("MMS claim evaluator requires an implementation case")
        if case.verification_study is None:
            raise ValueError("MMS evaluator requires a verification_study")

        response = _load_response(submission, context)
        reference = _load_reference(evaluation, context)
        measurement = _load_measurement(external_gates, context)
        if measurement is None:
            capability = 0.0
            evidence = 0.0
            capability_details = _zero_details(evaluation.capability_criteria)
            evidence_details = _zero_details(evaluation.evidence_criteria)
        else:
            capability, capability_details = _score_capability(
                response,
                measurement,
                reference,
                evaluation,
            )
            evidence, evidence_details = _score_evidence(
                case,
                response,
                measurement,
                reference,
                evaluation,
                submission,
            )
        automatic, verified = automatic_gates(case, submission, context)
        contract, contract_details = contract_score(
            case,
            response,
            submission,
            artifacts_verified=len(verified) == len(submission.artifacts),
        )
        gates = [
            *automatic,
            *evaluation_gates(evaluation, external_gates, context),
        ]
        score = calculate_case_score(
            capability,
            evidence,
            contract,
            [item.model_dump(mode="json") for item in gates],
            scoring_profile=case.scoring_profile,
        )
        failure_category = _failure_category(gates, capability_details, evidence_details)
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
                "mms_task": case.mms_task.value,
                "verification_study": case.verification_study.study_type.value,
                "failure_category": failure_category,
                "first_failed_stage": None,
            }
        )
