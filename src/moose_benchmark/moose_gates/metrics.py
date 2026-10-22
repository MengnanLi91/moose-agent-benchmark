"""Deterministic parsing and comparison helpers for protected outputs."""

from __future__ import annotations

import csv
import math
import re
from pathlib import Path

from .config import NumericTolerance
from .errors import GateInfrastructureError


def read_csv_rows(path: Path) -> list[dict[str, float]]:
    if not path.is_file():
        raise GateInfrastructureError(f"expected CSV output does not exist: {path}")
    with path.open(newline="", encoding="utf-8") as stream:
        rows = [
            {key: float(value) for key, value in row.items() if key and value not in (None, "")}
            for row in csv.DictReader(stream)
        ]
    if not rows:
        raise GateInfrastructureError(f"CSV output has no data rows: {path}")
    return rows


def within_tolerance(actual: float, expected: float, tolerance: NumericTolerance) -> bool:
    return values_within_tolerance(
        actual,
        expected,
        absolute=tolerance.absolute,
        relative=tolerance.relative,
    )


def values_within_tolerance(
    actual: float,
    expected: float,
    *,
    absolute: float,
    relative: float,
) -> bool:
    if not math.isfinite(actual):
        return False
    difference = abs(actual - expected)
    scale = max(abs(actual), abs(expected))
    return difference <= max(absolute, relative * scale)


def observed_orders(parameters: list[float], errors: list[float]) -> list[float]:
    if len(parameters) != len(errors) or len(parameters) < 2:
        raise ValueError("observed-order inputs must have equal lengths of at least two")
    if any(not math.isfinite(value) or value <= 0 for value in [*parameters, *errors]):
        raise ValueError("observed-order inputs must be finite and positive")
    orders = []
    for left_error, right_error, left_parameter, right_parameter in zip(
        errors[:-1],
        errors[1:],
        parameters[:-1],
        parameters[1:],
        strict=True,
    ):
        if left_parameter <= right_parameter:
            raise ValueError("refinement parameters must strictly decrease")
        orders.append(
            math.log(left_error / right_error) / math.log(left_parameter / right_parameter)
        )
    return orders


def classify_mms_verdict(
    orders: dict[str, list[float]],
    expected_orders: dict[str, float],
    *,
    acceptance_band: float = 0.2,
) -> tuple[dict[str, bool], str]:
    if set(orders) != set(expected_orders) or any(
        len(values) < 2 or any(not math.isfinite(value) for value in values)
        for values in orders.values()
    ):
        return {}, "inconclusive"
    assessments = {
        field: all(abs(order - expected_orders[field]) <= acceptance_band for order in values[-2:])
        for field, values in orders.items()
    }
    verdict = "verified" if all(assessments.values()) else "not_verified"
    return assessments, verdict


def contains_any(text: str, signatures: list[str]) -> bool:
    lowered = text.casefold()
    return any(signature.casefold() in lowered for signature in signatures)


def final_reported_time(text: str) -> float | None:
    matches = re.findall(r"Time Step\s+\d+,\s+time\s*=\s*([0-9.eE+-]+)", text)
    return float(matches[-1]) if matches else None
