"""Evaluator registry."""

from __future__ import annotations

from .semantic import SemanticRubricEvaluator
from .structured import StructuredClaimEvaluator

_EVALUATORS = {
    "semantic_rubric_v1": SemanticRubricEvaluator(),
    "structured_claim_v2": StructuredClaimEvaluator(),
}


def get_evaluator(name: str):
    try:
        return _EVALUATORS[name]
    except KeyError as exc:
        raise KeyError(f"unknown evaluator: {name}") from exc


__all__ = ["get_evaluator"]
