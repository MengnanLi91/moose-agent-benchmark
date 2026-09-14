"""Deterministic comparators used by the starter structured evaluator."""

from __future__ import annotations

import math
import re
from collections.abc import Mapping, Sequence
from typing import Any


class MissingValue:
    pass


MISSING = MissingValue()


def resolve_json_pointer(document: Any, pointer: str) -> Any:
    if pointer == "":
        return document
    if not pointer.startswith("/"):
        raise ValueError(f"JSON pointer must start with '/': {pointer}")
    current = document
    for raw_token in pointer[1:].split("/"):
        token = raw_token.replace("~1", "/").replace("~0", "~")
        if isinstance(current, Mapping):
            if token not in current:
                return MISSING
            current = current[token]
        elif isinstance(current, Sequence) and not isinstance(current, (str, bytes)):
            if not token.isdigit():
                return MISSING
            try:
                current = current[int(token)]
            except (ValueError, IndexError):
                return MISSING
        else:
            return MISSING
    return current


def _normalized(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value).strip()).casefold()


def _set_f1(actual: Any, expected: Any) -> float:
    if not isinstance(actual, Sequence) or isinstance(actual, (str, bytes)):
        return 0.0
    if not isinstance(expected, Sequence) or isinstance(expected, (str, bytes)):
        return 0.0
    actual_set = {_normalized(item) for item in actual}
    expected_set = {_normalized(item) for item in expected}
    if not actual_set and not expected_set:
        return 1.0
    if not actual_set or not expected_set:
        return 0.0
    overlap = len(actual_set & expected_set)
    precision = overlap / len(actual_set)
    recall = overlap / len(expected_set)
    return 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)


def _lcs_length(left: list[str], right: list[str]) -> int:
    row = [0] * (len(right) + 1)
    for left_item in left:
        previous = 0
        for index, right_item in enumerate(right, start=1):
            saved = row[index]
            if left_item == right_item:
                row[index] = previous + 1
            else:
                row[index] = max(row[index], row[index - 1])
            previous = saved
    return row[-1]


def _sequence_lcs(actual: Any, expected: Any) -> float:
    if not isinstance(actual, Sequence) or isinstance(actual, (str, bytes)):
        return 0.0
    if not isinstance(expected, Sequence) or isinstance(expected, (str, bytes)):
        return 0.0
    actual_items = [_normalized(item) for item in actual]
    expected_items = [_normalized(item) for item in expected]
    if not actual_items and not expected_items:
        return 1.0
    if not actual_items or not expected_items:
        return 0.0
    lcs = _lcs_length(actual_items, expected_items)
    return 2 * lcs / (len(actual_items) + len(expected_items))


def _json_subset_score(actual: Any, expected: Any) -> tuple[int, int]:
    if isinstance(expected, Mapping):
        if not isinstance(actual, Mapping):
            return 0, max(1, len(expected))
        if not expected:
            return 1, 1
        matched = total = 0
        for key, expected_value in expected.items():
            if key not in actual:
                total += 1
                continue
            child_matched, child_total = _json_subset_score(actual[key], expected_value)
            matched += child_matched
            total += child_total
        return matched, max(total, 1)
    if isinstance(expected, list):
        return (1, 1) if actual == expected else (0, 1)
    return (1, 1) if actual == expected else (0, 1)


def compare(
    actual: Any,
    expected: Any,
    comparator: str,
    *,
    absolute_tolerance: float | None = None,
    relative_tolerance: float | None = None,
) -> tuple[float, str]:
    """Return a score in [0, 1] and a short machine-readable explanation."""
    if actual is MISSING:
        return 0.0, "missing_json_pointer"
    if comparator == "exact":
        score = float(actual == expected)
    elif comparator == "normalized_exact":
        score = float(_normalized(actual) == _normalized(expected))
    elif comparator == "contains":
        if isinstance(actual, str):
            score = float(_normalized(expected) in _normalized(actual))
        elif isinstance(actual, Sequence):
            score = float(expected in actual)
        else:
            score = 0.0
    elif comparator == "numeric_tolerance":
        try:
            actual_number = float(actual)
            expected_number = float(expected)
        except (TypeError, ValueError):
            return 0.0, "not_numeric"
        absolute = absolute_tolerance or 0.0
        relative = relative_tolerance or 0.0
        tolerance = absolute + relative * abs(expected_number)
        score = float(
            math.isfinite(actual_number) and abs(actual_number - expected_number) <= tolerance
        )
    elif comparator == "set_f1":
        score = _set_f1(actual, expected)
    elif comparator == "sequence_lcs":
        score = _sequence_lcs(actual, expected)
    elif comparator == "json_subset":
        matched, total = _json_subset_score(actual, expected)
        score = matched / total
    else:
        raise ValueError(f"unsupported comparator: {comparator}")
    return score, "matched" if score == 1.0 else "partial_or_mismatch"
