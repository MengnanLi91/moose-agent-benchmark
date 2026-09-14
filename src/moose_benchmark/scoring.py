"""Gated atomic scoring and suite-level macro-aggregation."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from .contracts import CaseResult

ATOMIC_SUBCATEGORIES = [
    "F1",
    "F2",
    "F3",
    "F4",
    "D1",
    "D2",
    "D3",
    "D4",
    "R1",
    "R2",
    "R3",
    "R4",
    "V1",
    "V2",
    "V3",
    "V4",
]


def calculate_case_score(
    capability: float,
    evidence: float,
    contract: float,
    gate_results: list[dict[str, Any]],
    *,
    case_pass_threshold: float = 80.0,
    capability_pass_threshold: float = 80.0,
) -> dict[str, Any]:
    for name, value in (
        ("capability", capability),
        ("evidence", evidence),
        ("contract", contract),
    ):
        if not 0 <= value <= 100:
            raise ValueError(f"{name} must be in [0, 100], got {value}")
    raw_score = 0.70 * capability + 0.20 * evidence + 0.10 * contract
    gates_passed = all(bool(item["passed"]) for item in gate_results)
    official_score = raw_score if gates_passed else 0.0
    case_passed = (
        gates_passed
        and capability >= capability_pass_threshold
        and raw_score >= case_pass_threshold
    )
    return {
        "component_scores": {
            "capability": round(capability, 4),
            "evidence": round(evidence, 4),
            "contract": round(contract, 4),
        },
        "raw_score": round(raw_score, 4),
        "official_score": round(official_score, 4),
        "gates_passed": gates_passed,
        "case_passed": case_passed,
        "gate_results": gate_results,
    }


def _mean(values: list[float]) -> float:
    return sum(values) / len(values)


def aggregate_results(
    results: list[CaseResult | dict[str, Any]],
    *,
    required_atomic_subcategories: list[str] | None = None,
    benchmark_id: str | None = None,
    benchmark_version: str | None = None,
) -> dict[str, Any]:
    """Aggregate case-result JSON without allowing case-count imbalance to dominate."""
    validated = [
        item if isinstance(item, CaseResult) else CaseResult.model_validate(item)
        for item in results
    ]
    case_ids = [item.case_id for item in validated]
    if len(case_ids) != len(set(case_ids)):
        raise ValueError("aggregate inputs must contain one result per case_id")

    benchmark_ids = {item.benchmark_id for item in validated}
    benchmark_versions = {item.benchmark_version for item in validated}
    if len(benchmark_ids) > 1 or len(benchmark_versions) > 1:
        raise ValueError("aggregate inputs must belong to one benchmark version")
    if benchmark_id is not None and benchmark_ids and benchmark_ids != {benchmark_id}:
        raise ValueError("result benchmark_id does not match the selected manifest")
    if (
        benchmark_version is not None
        and benchmark_versions
        and benchmark_versions != {benchmark_version}
    ):
        raise ValueError("result benchmark_version does not match the selected manifest")

    results = [item.model_dump(mode="json") for item in validated]
    atomic = [item for item in results if item["case_kind"] == "atomic"]
    integrated_cases = [item for item in results if item["case_kind"] == "integrated_workflow"]

    by_subcategory: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in atomic:
        by_subcategory[item["subcategory"]].append(item)

    subcategory_scores = {
        key: round(_mean([case["official_score"] for case in cases]), 4)
        for key, cases in sorted(by_subcategory.items())
    }
    subcategory_pass_rates = {
        key: round(_mean([float(case["case_passed"]) for case in cases]), 4)
        for key, cases in sorted(by_subcategory.items())
    }

    track_members = {
        "FORM": ["F1", "F2", "F3", "F4"],
        "DIAG": ["D1", "D2", "D3", "D4"],
        "REPAIR": ["R1", "R2", "R3", "R4"],
        "VERIFY": ["V1", "V2", "V3", "V4"],
    }
    track_scores: dict[str, float] = {}
    for track, members in track_members.items():
        represented = [subcategory_scores[item] for item in members if item in subcategory_scores]
        if represented:
            track_scores[track] = round(_mean(represented), 4)

    represented_scores = list(subcategory_scores.values())
    atomic_capability_score = round(_mean(represented_scores), 4) if represented_scores else None
    represented_pass_rates = list(subcategory_pass_rates.values())
    atomic_pass_rate = round(_mean(represented_pass_rates), 4) if represented_pass_rates else None

    domain_cells: dict[tuple[str, str], list[float]] = defaultdict(list)
    for item in atomic:
        for domain in item["physics_domains"]:
            domain_cells[(domain, item["subcategory"])].append(item["official_score"])
    domain_to_cells: dict[str, list[float]] = defaultdict(list)
    for (domain, _subcategory), values in domain_cells.items():
        domain_to_cells[domain].append(_mean(values))
    domain_scores = {
        domain: round(_mean(cell_scores), 4)
        for domain, cell_scores in sorted(domain_to_cells.items())
    }
    domain_generalization_score = (
        round(_mean(list(domain_scores.values())), 4) if domain_scores else None
    )

    complete_integrated_cases = sum(bool(item["case_passed"]) for item in integrated_cases)
    integrated_workflow_completion_rate = (
        round(complete_integrated_cases / len(integrated_cases), 4) if integrated_cases else None
    )
    first_failed_stage_counts = Counter(
        item["first_failed_stage"] or "unreported"
        for item in integrated_cases
        if not item["case_passed"]
    )
    required_subcategories = (
        required_atomic_subcategories
        if required_atomic_subcategories is not None
        else ATOMIC_SUBCATEGORIES
    )
    return {
        "benchmark_id": next(iter(benchmark_ids), benchmark_id),
        "benchmark_version": next(iter(benchmark_versions), benchmark_version),
        "atomic_case_count": len(atomic),
        "integrated_workflow_case_count": len(integrated_cases),
        "subcategory_scores": subcategory_scores,
        "subcategory_pass_rates": subcategory_pass_rates,
        "track_scores": track_scores,
        "atomic_capability_score": atomic_capability_score,
        "atomic_pass_rate": atomic_pass_rate,
        "domain_scores": domain_scores,
        "domain_generalization_score": domain_generalization_score,
        "integrated_workflow_completion_rate": integrated_workflow_completion_rate,
        "integrated_first_failed_stage_counts": dict(sorted(first_failed_stage_counts.items())),
        "represented_subcategories": sorted(subcategory_scores),
        "missing_subcategories": [
            item for item in required_subcategories if item not in subcategory_scores
        ],
        "full_atomic_coverage": set(subcategory_scores) == set(required_subcategories),
    }
