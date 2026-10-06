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
    if not math.isfinite(actual):
        return False
    difference = abs(actual - expected)
    scale = max(abs(actual), abs(expected))
    return difference <= max(tolerance.absolute, tolerance.relative * scale)


def contains_any(text: str, signatures: list[str]) -> bool:
    lowered = text.casefold()
    return any(signature.casefold() in lowered for signature in signatures)


def final_reported_time(text: str) -> float | None:
    matches = re.findall(r"Time Step\s+\d+,\s+time\s*=\s*([0-9.eE+-]+)", text)
    return float(matches[-1]) if matches else None
