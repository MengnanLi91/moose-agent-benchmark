"""Typed contracts shared by benchmark authors, participants, and evaluators."""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path, PurePosixPath
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Track(StrEnum):
    FORM = "FORM"
    DIAG = "DIAG"
    REPAIR = "REPAIR"
    VERIFY = "VERIFY"


class CaseKind(StrEnum):
    ATOMIC = "atomic"
    INTEGRATED_WORKFLOW = "integrated_workflow"


class Difficulty(StrEnum):
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"
    L4 = "L4"


AtomicSubcategory = Literal[
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
Sha256 = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]

TRACK_SUBCATEGORIES: dict[Track, set[str]] = {
    Track.FORM: {"F1", "F2", "F3", "F4"},
    Track.DIAG: {"D1", "D2", "D3", "D4"},
    Track.REPAIR: {"R1", "R2", "R3", "R4"},
    Track.VERIFY: {"V1", "V2", "V3", "V4"},
}


def validate_relative_path(value: str) -> str:
    path = PurePosixPath(value)
    if not value or value == "." or path.is_absolute() or ".." in path.parts:
        raise ValueError(f"path must remain inside its case directory: {value!r}")
    return value


def validate_json_pointer(value: str) -> str:
    if value and not value.startswith("/"):
        raise ValueError(f"JSON pointer must be empty or start with '/': {value}")
    return value


class TargetSpec(StrictModel):
    application: str
    version: str
    executable_hint: str | None = None


class ArtifactSpec(StrictModel):
    id: str
    path: str
    role: str
    mutable: bool = False
    required: bool = True
    sha256: Sha256 | None = None

    @model_validator(mode="after")
    def safe_path(self) -> ArtifactSpec:
        self.path = validate_relative_path(self.path)
        return self


class EvidenceSourceSpec(StrictModel):
    id: str
    path: str
    kind: str
    description: str
    sha256: Sha256 | None = None

    @model_validator(mode="after")
    def safe_path(self) -> EvidenceSourceSpec:
        self.path = validate_relative_path(self.path)
        return self


class StartingState(StrictModel):
    description: str
    supplied_truth: list[str] = Field(default_factory=list)
    excluded_from_scoring: list[str] = Field(default_factory=list)


class ActionPolicy(StrictModel):
    permitted: list[str]
    prohibited: list[str] = Field(default_factory=list)


class BudgetSpec(StrictModel):
    wall_time_seconds: int = Field(gt=0)
    cpu_seconds: int = Field(gt=0)
    memory_mib: int = Field(gt=0)
    validation_attempts: int = Field(ge=0)
    execution_attempts: int = Field(ge=0)


class SubmissionContract(StrictModel):
    required_claim_paths: list[str]
    evidence_required: bool = True
    artifacts_allowed: bool = False
    required_artifact_roles: list[str] = Field(default_factory=list)
    maximum_artifacts: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def validate_artifact_policy(self) -> SubmissionContract:
        if not self.artifacts_allowed and (
            self.required_artifact_roles or self.maximum_artifacts != 0
        ):
            raise ValueError(
                "artifact roles and maximum_artifacts must be empty when artifacts are prohibited"
            )
        if len(self.required_artifact_roles) != len(set(self.required_artifact_roles)):
            raise ValueError("required artifact roles must be unique")
        if len(self.required_artifact_roles) > self.maximum_artifacts:
            raise ValueError("maximum_artifacts cannot be smaller than required artifact roles")
        if len(self.required_claim_paths) != len(set(self.required_claim_paths)):
            raise ValueError("required claim paths must be unique")
        for pointer in self.required_claim_paths:
            validate_json_pointer(pointer)
        return self


class CaseContract(StrictModel):
    schema_version: Literal["1.0"]
    case_id: str
    title: str
    case_kind: CaseKind
    track: Track | None = None
    subcategory: AtomicSubcategory | None = None
    difficulty: Difficulty
    base_problem_id: str
    physics_domains: list[str] = Field(min_length=1)
    target: TargetSpec
    prompt_path: str
    prompt_sha256: Sha256 | None = None
    artifacts: list[ArtifactSpec]
    evidence_sources: list[EvidenceSourceSpec] = Field(default_factory=list)
    starting_state: StartingState
    actions: ActionPolicy
    budget: BudgetSpec
    submission: SubmissionContract
    required_stages: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_case_shape(self) -> CaseContract:
        self.prompt_path = validate_relative_path(self.prompt_path)
        if self.case_kind == CaseKind.ATOMIC:
            if self.track is None or self.subcategory is None:
                raise ValueError("atomic cases require track and subcategory")
            if self.subcategory not in TRACK_SUBCATEGORIES[self.track]:
                raise ValueError("subcategory must match the selected track")
            if self.required_stages:
                raise ValueError("atomic cases cannot declare integrated workflow stages")
        else:
            if self.track is not None or self.subcategory is not None:
                raise ValueError("integrated workflow cases must leave track and subcategory unset")
            if not self.required_stages:
                raise ValueError("integrated workflow cases require an ordered stage list")
        ids = [item.id for item in [*self.artifacts, *self.evidence_sources]]
        if len(ids) != len(set(ids)):
            raise ValueError("artifact and evidence IDs must be unique within a case")
        if len(self.physics_domains) != len(set(self.physics_domains)):
            raise ValueError("physics domains must be unique")
        if len(self.required_stages) != len(set(self.required_stages)):
            raise ValueError("required workflow stages must be unique")
        return self


class EvidenceClaim(StrictModel):
    source_id: str
    observation: str
    interpretation: str
    artifact_sha256: Sha256 | None = None


class SubmittedArtifact(StrictModel):
    role: str
    path: str
    sha256: Sha256

    @model_validator(mode="after")
    def safe_path(self) -> SubmittedArtifact:
        self.path = validate_relative_path(self.path)
        return self


class UsageRecord(StrictModel):
    wall_time_seconds: float = Field(ge=0)
    cpu_seconds: float = Field(ge=0)
    validation_attempts: int = Field(ge=0)
    execution_attempts: int = Field(ge=0)


class SubmissionEnvelope(StrictModel):
    schema_version: Literal["1.0"]
    case_id: str
    track: Track | None
    subcategory: AtomicSubcategory | None
    claim: dict[str, Any]
    evidence: list[EvidenceClaim]
    artifacts: list[SubmittedArtifact]
    confidence: float = Field(ge=0, le=1)
    limitations: list[str]
    usage: UsageRecord

    @model_validator(mode="after")
    def validate_submission_shape(self) -> SubmissionEnvelope:
        if (self.track is None) != (self.subcategory is None):
            raise ValueError("track and subcategory must either both be set or both be null")
        if self.track is not None and self.subcategory not in TRACK_SUBCATEGORIES[self.track]:
            raise ValueError("submission subcategory must match its track")
        paths = [item.path for item in self.artifacts]
        roles = [item.role for item in self.artifacts]
        if len(paths) != len(set(paths)):
            raise ValueError("submitted artifact paths must be unique")
        if len(roles) != len(set(roles)):
            raise ValueError("submitted artifact roles must be unique")
        return self


ComparatorName = Literal[
    "exact",
    "normalized_exact",
    "contains",
    "numeric_tolerance",
    "set_f1",
    "sequence_lcs",
    "json_subset",
]


class CriterionSpec(StrictModel):
    id: str
    description: str
    json_pointer: str
    comparator: ComparatorName
    expected: Any
    weight: float = Field(gt=0, le=1)
    absolute_tolerance: float | None = Field(default=None, ge=0)
    relative_tolerance: float | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_pointer(self) -> CriterionSpec:
        self.json_pointer = validate_json_pointer(self.json_pointer)
        return self


class GateSpec(StrictModel):
    id: str
    description: str
    kind: Literal["field_equals", "external"]
    json_pointer: str | None = None
    expected: Any = None
    stage: str | None = None

    @model_validator(mode="after")
    def validate_gate(self) -> GateSpec:
        if self.kind == "field_equals" and self.json_pointer is None:
            raise ValueError("field_equals gates require json_pointer")
        if self.kind == "external" and (self.json_pointer is not None or self.expected is not None):
            raise ValueError("external gates cannot declare json_pointer or expected")
        return self


class EvaluationSpec(StrictModel):
    schema_version: Literal["1.0"]
    case_id: str
    evaluator: str = Field(min_length=1)
    capability_criteria: list[CriterionSpec]
    evidence_criteria: list[CriterionSpec]
    hard_gates: list[GateSpec] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_evaluation(self) -> EvaluationSpec:
        for label, criteria in (
            ("capability", self.capability_criteria),
            ("evidence", self.evidence_criteria),
        ):
            if not criteria:
                raise ValueError(f"{label} criteria cannot be empty")
            total = sum(item.weight for item in criteria)
            if abs(total - 1.0) > 1e-9:
                raise ValueError(f"{label} criterion weights must sum to 1.0, got {total}")
        criterion_ids = [item.id for item in [*self.capability_criteria, *self.evidence_criteria]]
        if len(criterion_ids) != len(set(criterion_ids)):
            raise ValueError("criterion IDs must be unique")
        gate_ids = [item.id for item in self.hard_gates]
        if len(gate_ids) != len(set(gate_ids)):
            raise ValueError("hard gate IDs must be unique")
        reserved_gate_ids = {"artifact_policy", "declared_usage_budget"}
        if reserved_gate_ids & set(gate_ids):
            raise ValueError("hard gate IDs cannot use automatic gate names")
        return self


class ExternalGateResult(StrictModel):
    benchmark_id: str
    benchmark_version: str
    case_id: str
    submission_sha256: Sha256
    gate_id: str
    passed: bool
    detail: str
    evidence: list[str] = Field(default_factory=list)


class EvaluationContext(StrictModel):
    benchmark_id: str
    benchmark_version: str
    submission_sha256: Sha256
    artifact_root: Path


class ManifestCaseRef(StrictModel):
    case_id: str
    public_case: str
    private_evaluation: str
    split: Literal["development", "validation", "test"]
    enabled: bool = True

    @model_validator(mode="after")
    def safe_paths(self) -> ManifestCaseRef:
        self.public_case = validate_relative_path(self.public_case)
        self.private_evaluation = validate_relative_path(self.private_evaluation)
        return self


class BenchmarkManifest(StrictModel):
    schema_version: Literal["1.0"]
    benchmark_id: str
    benchmark_version: str
    required_atomic_subcategories: list[AtomicSubcategory]
    cases: list[ManifestCaseRef]

    @model_validator(mode="after")
    def validate_manifest(self) -> BenchmarkManifest:
        ids = [item.case_id for item in self.cases]
        if len(ids) != len(set(ids)):
            raise ValueError("manifest case IDs must be unique")
        if not self.required_atomic_subcategories:
            raise ValueError("required_atomic_subcategories cannot be empty")
        if len(self.required_atomic_subcategories) != len(set(self.required_atomic_subcategories)):
            raise ValueError("required_atomic_subcategories must be unique")
        return self


class GateResult(StrictModel):
    id: str
    passed: bool
    detail: str
    evidence: list[str] = Field(default_factory=list)
    stage: str | None = None


class ComponentScores(StrictModel):
    capability: float = Field(ge=0, le=100)
    evidence: float = Field(ge=0, le=100)
    contract: float = Field(ge=0, le=100)


class CaseResult(StrictModel):
    schema_version: Literal["1.0"]
    benchmark_id: str
    benchmark_version: str
    evaluator: str
    case_id: str
    case_kind: CaseKind
    track: Track | None
    subcategory: AtomicSubcategory | None
    difficulty: Difficulty
    base_problem_id: str
    physics_domains: list[str] = Field(min_length=1)
    submission_sha256: Sha256
    submitted_artifacts: list[SubmittedArtifact]
    component_scores: ComponentScores
    raw_score: float = Field(ge=0, le=100)
    official_score: float = Field(ge=0, le=100)
    gates_passed: bool
    case_passed: bool
    gate_results: list[GateResult]
    criterion_details: dict[str, Any]
    first_failed_stage: str | None = None

    @model_validator(mode="after")
    def validate_result(self) -> CaseResult:
        if self.case_kind == CaseKind.ATOMIC:
            if self.track is None or self.subcategory is None:
                raise ValueError("atomic results require track and subcategory")
            if self.subcategory not in TRACK_SUBCATEGORIES[self.track]:
                raise ValueError("result subcategory must match its track")
            if self.first_failed_stage is not None:
                raise ValueError("atomic results cannot report an integrated failure stage")
        elif self.track is not None or self.subcategory is not None:
            raise ValueError("integrated results must leave track and subcategory null")

        expected_official = self.raw_score if self.gates_passed else 0.0
        if abs(self.official_score - expected_official) > 1e-4:
            raise ValueError("official score is inconsistent with gate status")
        gate_ids = [item.id for item in self.gate_results]
        if len(gate_ids) != len(set(gate_ids)):
            raise ValueError("gate result IDs must be unique")
        if self.gates_passed != all(item.passed for item in self.gate_results):
            raise ValueError("gates_passed is inconsistent with gate results")
        expected_case_passed = (
            self.gates_passed and self.component_scores.capability >= 80 and self.raw_score >= 80
        )
        if self.case_passed != expected_case_passed:
            raise ValueError("case_passed is inconsistent with score thresholds")
        if self.case_passed and self.first_failed_stage is not None:
            raise ValueError("passing results cannot report a first failed stage")
        return self
