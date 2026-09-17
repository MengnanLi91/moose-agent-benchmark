"""Typed models for the human-facing benchmark catalog."""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import Field, model_validator

from ..contracts import (
    TRACK_SUBCATEGORIES,
    AtomicSubcategory,
    CaseKind,
    Difficulty,
    StrictModel,
    Track,
)


class CatalogStatus(StrEnum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    BLOCKED = "blocked"
    COMPLETE = "complete"


class CatalogPriority(StrEnum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    RELEASE_BLOCKER = "release_blocker"


class CatalogRecord(StrictModel):
    catalog_schema_version: Literal["1.0"]
    case_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    case_kind: CaseKind
    track: Track | None = None
    subcategory: AtomicSubcategory | None = None
    physics_domains: list[str] = Field(min_length=1)
    difficulty: Difficulty
    base_problem_id: str = Field(min_length=1)
    status: CatalogStatus
    priority: CatalogPriority = CatalogPriority.NORMAL
    owner: str | None = None
    reviewers: list[str] = Field(default_factory=list)
    source_type: str = Field(min_length=1)
    source_name: str = ""
    source_url: str = ""
    domain_review_complete: bool = False
    benchmark_review_complete: bool = False
    moose_validation_required: bool = False
    moose_validated: bool = False
    github_issue: str = ""
    github_pr: str = ""
    tags: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_record(self) -> CatalogRecord:
        if self.case_kind == CaseKind.ATOMIC:
            if self.track is None or self.subcategory is None:
                raise ValueError("atomic catalog records require track and subcategory")
            if self.subcategory not in TRACK_SUBCATEGORIES[self.track]:
                raise ValueError("subcategory must match the selected track")
        elif self.track is not None or self.subcategory is not None:
            raise ValueError(
                "integrated workflow catalog records must leave track and subcategory unset"
            )

        self.owner = self.owner.strip() if self.owner and self.owner.strip() else None
        for label, values in (
            ("physics domains", self.physics_domains),
            ("reviewers", self.reviewers),
            ("tags", self.tags),
        ):
            if len(values) != len(set(values)):
                raise ValueError(f"{label} must be unique")
        return self


class CoverageConfig(StrictModel):
    schema_version: Literal["1.0"]
    release: str = Field(min_length=1)
    track_targets: dict[Track, int]
    difficulty_targets: dict[Difficulty, int]

    @model_validator(mode="after")
    def validate_targets(self) -> CoverageConfig:
        if set(self.track_targets) != set(Track):
            raise ValueError("track_targets must define FORM, DIAG, REPAIR, and VERIFY")
        if set(self.difficulty_targets) != set(Difficulty):
            raise ValueError("difficulty_targets must define L1, L2, L3, and L4")
        if any(value <= 0 for value in self.track_targets.values()):
            raise ValueError("track targets must be positive")
        if any(value <= 0 for value in self.difficulty_targets.values()):
            raise ValueError("difficulty targets must be positive")
        track_total = sum(self.track_targets.values())
        difficulty_total = sum(self.difficulty_targets.values())
        if track_total != difficulty_total:
            raise ValueError(
                "track and difficulty targets must describe the same total number of cases"
            )
        return self
