"""Evaluator protocol."""

from __future__ import annotations

from typing import Protocol

from ..contracts import (
    CaseContract,
    CaseResult,
    EvaluationContext,
    EvaluationSpec,
    ExternalGateResult,
    SubmissionEnvelope,
)


class Evaluator(Protocol):
    def evaluate(
        self,
        case: CaseContract,
        evaluation: EvaluationSpec,
        submission: SubmissionEnvelope,
        external_gates: list[ExternalGateResult],
        context: EvaluationContext,
    ) -> CaseResult: ...
