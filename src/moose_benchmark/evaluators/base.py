"""Evaluator protocol."""

from __future__ import annotations

from typing import Protocol

from ..contracts import (
    CaseContract,
    CaseResult,
    EvaluationContext,
    EvaluationSpec,
    ExternalGateResult,
    SubmissionRecord,
)
from ..llm import LLMClient


class Evaluator(Protocol):
    def evaluate(
        self,
        case: CaseContract,
        evaluation: EvaluationSpec,
        submission: SubmissionRecord,
        external_gates: list[ExternalGateResult],
        context: EvaluationContext,
        *,
        llm_client: LLMClient | None = None,
    ) -> CaseResult: ...
