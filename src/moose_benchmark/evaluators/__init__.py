"""Evaluator registry."""

from __future__ import annotations

from .structured import StructuredClaimEvaluator

_EVALUATORS = {"structured_claim_v1": StructuredClaimEvaluator()}


def get_evaluator(name: str):
    try:
        return _EVALUATORS[name]
    except KeyError as exc:
        raise KeyError(f"unknown evaluator: {name}") from exc


__all__ = ["get_evaluator"]
