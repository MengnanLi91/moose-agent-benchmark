"""CI assertion for the development gold and mutant result pair."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


if len(sys.argv) != 3:
    raise SystemExit("usage: assert_example_scores.py GOLD_RESULT MUTANT_RESULT")

gold = load(sys.argv[1])
mutant = load(sys.argv[2])
if not gold["case_passed"] or gold["official_score"] != 100.0:
    raise SystemExit(f"gold submission did not receive the expected score: {gold}")
if not mutant["gates_passed"]:
    raise SystemExit(f"designated mutant failed because of a gate, not its claim: {mutant}")
if mutant["case_passed"] or mutant["official_score"] >= 80.0:
    raise SystemExit(f"designated mutant was not rejected: {mutant}")

print("gold accepted and designated mutant rejected")
