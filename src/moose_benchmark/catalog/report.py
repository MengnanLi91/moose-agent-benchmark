"""Build deterministic catalog development reports."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from ..contracts import TRACK_SUBCATEGORIES, Difficulty, Track
from .models import CatalogStatus, CoverageConfig
from .validator import CatalogValidationResult


def _progress(target: int | None = None) -> dict[str, int]:
    values = {"cataloged": 0, "implemented": 0, "complete": 0}
    if target is not None:
        return {"target": target, **values}
    return values


def _increment(progress: dict[str, int], implemented: bool, complete: bool) -> None:
    progress["cataloged"] += 1
    if implemented:
        progress["implemented"] += 1
    if complete:
        progress["complete"] += 1


def _all_subcategories() -> list[str]:
    return [subcategory for track in Track for subcategory in sorted(TRACK_SUBCATEGORIES[track])]


def build_catalog_report(
    validation: CatalogValidationResult,
    coverage: CoverageConfig,
) -> dict[str, Any]:
    status_counts = {status.value: 0 for status in CatalogStatus}
    track_counts = {track.value: _progress(coverage.track_targets[track]) for track in Track}
    subcategory_counts = {subcategory: _progress() for subcategory in _all_subcategories()}
    difficulty_counts = {
        difficulty.value: _progress(coverage.difficulty_targets[difficulty])
        for difficulty in Difficulty
    }
    domain_counts: defaultdict[str, dict[str, int]] = defaultdict(_progress)
    integrated = _progress()
    missing_owners: list[str] = []
    blocked: list[str] = []
    ready_for_review: list[str] = []
    readiness_gaps: dict[str, list[str]] = {}

    implemented_total = 0
    complete_total = 0
    atomic_total = 0
    for document in sorted(validation.documents, key=lambda item: item.record.case_id):
        record = document.record
        readiness = validation.readiness[record.case_id]
        implemented = readiness.implemented
        complete = record.status == CatalogStatus.COMPLETE and readiness.complete
        implemented_total += int(implemented)
        complete_total += int(complete)
        status_counts[record.status.value] += 1
        for domain in record.physics_domains:
            _increment(domain_counts[domain], implemented, complete)

        if record.track is None:
            _increment(integrated, implemented, complete)
        else:
            atomic_total += 1
            _increment(difficulty_counts[record.difficulty.value], implemented, complete)
            _increment(track_counts[record.track.value], implemented, complete)
            _increment(subcategory_counts[record.subcategory], implemented, complete)
        if record.owner is None and record.status != CatalogStatus.COMPLETE:
            missing_owners.append(record.case_id)
        if record.status == CatalogStatus.BLOCKED:
            blocked.append(record.case_id)
        if record.status == CatalogStatus.REVIEW:
            ready_for_review.append(record.case_id)
        if readiness.completion_missing:
            readiness_gaps[record.case_id] = list(readiness.completion_missing)

    return {
        "release": coverage.release,
        "target_total": sum(coverage.track_targets.values()),
        "totals": {
            "cataloged": len(validation.documents),
            "implemented": implemented_total,
            "complete": complete_total,
            "atomic": atomic_total,
            "integrated": integrated["cataloged"],
        },
        "status_counts": status_counts,
        "track_counts": track_counts,
        "subcategory_counts": subcategory_counts,
        "difficulty_counts": difficulty_counts,
        "physics_domain_counts": dict(sorted(domain_counts.items())),
        "integrated_counts": integrated,
        "missing_owners": sorted(missing_owners),
        "blocked": sorted(blocked),
        "ready_for_review": sorted(ready_for_review),
        "readiness_gaps": dict(sorted(readiness_gaps.items())),
    }


def format_catalog_report(report: dict[str, Any]) -> str:
    totals = report["totals"]
    lines = [
        "MOOSE Agent Benchmark Development Status",
        "",
        f"Release: {report['release']}",
        f"Target atomic cases: {report['target_total']}",
        (
            "Catalog totals: "
            f"{totals['cataloged']} cataloged, "
            f"{totals['implemented']} implemented, "
            f"{totals['complete']} complete"
        ),
        f"Integrated cases: {totals['integrated']}",
        "",
        "Status",
    ]
    for status in CatalogStatus:
        lines.append(f"  {status.value:<15} {report['status_counts'][status.value]:>4}")

    lines.extend(["", "Tracks (cataloged / implemented / complete / target)"])
    for track in Track:
        values = report["track_counts"][track.value]
        lines.append(
            f"  {track.value:<8} "
            f"{values['cataloged']:>3} / {values['implemented']:>3} / "
            f"{values['complete']:>3} / {values['target']:>3}"
        )

    lines.extend(["", "Atomic subcategories (cataloged / implemented / complete)"])
    for subcategory in _all_subcategories():
        values = report["subcategory_counts"][subcategory]
        lines.append(
            f"  {subcategory:<3} "
            f"{values['cataloged']:>3} / {values['implemented']:>3} / "
            f"{values['complete']:>3}"
        )

    lines.extend(
        [
            "",
            f"Missing owners: {len(report['missing_owners'])}",
            f"Ready for review: {len(report['ready_for_review'])}",
            f"Blocked: {len(report['blocked'])}",
        ]
    )
    return "\n".join(lines) + "\n"
