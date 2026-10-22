"""Typed contracts shared by benchmark authors, participants, and evaluators."""

from __future__ import annotations

import math
from datetime import datetime
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


class ResponseMode(StrEnum):
    FREE_TEXT = "free_text"
    ARTIFACT = "artifact"
    STRUCTURED_JSON = "structured_json"


class ScoringProfile(StrEnum):
    FORM_CAPABILITY = "form_capability_v1"
    BALANCED = "balanced_v1"


class VerificationStudyType(StrEnum):
    SPATIAL = "spatial"
    TEMPORAL = "temporal"


class MmsTask(StrEnum):
    DERIVATION = "derivation"
    IMPLEMENTATION = "implementation"


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


class RequiredSubmissionArtifact(StrictModel):
    role: str
    path: str

    @model_validator(mode="after")
    def safe_path(self) -> RequiredSubmissionArtifact:
        self.path = validate_relative_path(self.path)
        return self


class SubmissionContract(StrictModel):
    response_mode: ResponseMode
    required_claim_paths: list[str] = Field(default_factory=list)
    evidence_required: bool = False
    required_artifacts: list[RequiredSubmissionArtifact] = Field(default_factory=list)
    maximum_artifacts: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def validate_artifact_policy(self) -> SubmissionContract:
        roles = [item.role for item in self.required_artifacts]
        paths = [item.path for item in self.required_artifacts]
        if len(roles) != len(set(roles)):
            raise ValueError("required artifact roles must be unique")
        if len(paths) != len(set(paths)):
            raise ValueError("required artifact paths must be unique")
        if len(self.required_artifacts) > self.maximum_artifacts:
            raise ValueError("maximum_artifacts cannot be smaller than required artifact roles")
        if len(self.required_claim_paths) != len(set(self.required_claim_paths)):
            raise ValueError("required claim paths must be unique")
        for pointer in self.required_claim_paths:
            validate_json_pointer(pointer)
        if self.response_mode != ResponseMode.STRUCTURED_JSON and (
            self.required_claim_paths or self.evidence_required
        ):
            raise ValueError(
                "claim paths and evidence requirements are valid only for structured_json"
            )
        if self.response_mode == ResponseMode.FREE_TEXT and self.maximum_artifacts:
            raise ValueError("free_text submissions cannot include artifacts")
        if self.response_mode == ResponseMode.ARTIFACT and not self.required_artifacts:
            raise ValueError("artifact submissions require at least one artifact")
        return self


class VerificationLevel(StrictModel):
    level: int = Field(ge=0)
    parameter: float = Field(gt=0)
    controls: dict[str, int | float | str]
    overrides: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_overrides(self) -> VerificationLevel:
        if any(not value.strip() or "\n" in value or "\r" in value for value in self.overrides):
            raise ValueError("verification overrides must be non-empty single-line arguments")
        return self


class VerificationStudy(StrictModel):
    method: Literal["mms"]
    study_type: VerificationStudyType
    norm: str = Field(min_length=1)
    refinement_parameter: Literal["mesh_h", "time_step"]
    permitted_overrides: list[str] = Field(min_length=1)
    levels: list[VerificationLevel] = Field(min_length=4, max_length=4)
    required_fields: list[str] = Field(min_length=1)
    expected_orders: dict[str, float]

    @model_validator(mode="after")
    def validate_study(self) -> VerificationStudy:
        if [item.level for item in self.levels] != list(range(4)):
            raise ValueError("verification levels must be ordered exactly as 0, 1, 2, 3")
        parameters = [item.parameter for item in self.levels]
        if any(left <= right for left, right in zip(parameters[:-1], parameters[1:], strict=True)):
            raise ValueError("verification parameters must decrease at every level")
        if len(self.required_fields) != len(set(self.required_fields)):
            raise ValueError("verification fields must be unique")
        if set(self.expected_orders) != set(self.required_fields):
            raise ValueError("expected_orders must define every required field exactly once")
        if any(not math.isfinite(order) or order <= 0 for order in self.expected_orders.values()):
            raise ValueError("expected_orders must be finite and positive")
        if len(self.permitted_overrides) != len(set(self.permitted_overrides)):
            raise ValueError("permitted_overrides must be unique")
        permitted = set(self.permitted_overrides)
        for level in self.levels:
            override_paths = [override.split("=", 1)[0] for override in level.overrides]
            if len(override_paths) != len(set(override_paths)):
                raise ValueError("verification override paths must be unique within a level")
            if set(override_paths) != permitted:
                raise ValueError(
                    "every verification level must set exactly the permitted overrides"
                )
        expected_parameter = (
            "mesh_h" if self.study_type == VerificationStudyType.SPATIAL else "time_step"
        )
        if self.refinement_parameter != expected_parameter:
            raise ValueError("refinement_parameter does not match the verification study type")
        return self


class MmsDerivationSpec(StrictModel):
    supplied: list[
        Literal[
            "governing_equations",
            "coefficients",
            "domain",
            "manufactured_fields",
        ]
    ] = Field(min_length=1)
    required_outputs: list[
        Literal[
            "derivatives_and_residual",
            "source_terms",
            "boundary_and_initial_data",
            "constraints_and_conventions",
        ]
    ] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_unique_items(self) -> MmsDerivationSpec:
        if len(self.supplied) != len(set(self.supplied)):
            raise ValueError("MMS derivation supplied items must be unique")
        if len(self.required_outputs) != len(set(self.required_outputs)):
            raise ValueError("MMS derivation outputs must be unique")
        if set(self.supplied) != {
            "governing_equations",
            "coefficients",
            "domain",
            "manufactured_fields",
        }:
            raise ValueError("MMS derivation cases must declare all supplied problem data")
        if set(self.required_outputs) != {
            "derivatives_and_residual",
            "source_terms",
            "boundary_and_initial_data",
            "constraints_and_conventions",
        }:
            raise ValueError("MMS derivation cases must declare all required output groups")
        return self


class CaseContract(StrictModel):
    schema_version: Literal["2.0"]
    case_id: str
    title: str
    case_kind: CaseKind
    track: Track | None = None
    subcategory: AtomicSubcategory | None = None
    difficulty: Difficulty
    scoring_profile: ScoringProfile
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
    mms_task: MmsTask | None = None
    mms_derivation: MmsDerivationSpec | None = None
    verification_study: VerificationStudy | None = None
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
            if self.track == Track.FORM and self.scoring_profile != ScoringProfile.FORM_CAPABILITY:
                raise ValueError("FORM cases require the form_capability_v1 scoring profile")
            if self.track != Track.FORM and self.scoring_profile != ScoringProfile.BALANCED:
                raise ValueError("non-FORM cases require the balanced_v1 scoring profile")
            if self.subcategory == "V1":
                if self.mms_task is None:
                    raise ValueError("V1 cases require mms_task")
                if self.mms_task == MmsTask.DERIVATION:
                    if self.mms_derivation is None or self.verification_study is not None:
                        raise ValueError(
                            "MMS derivation cases require mms_derivation and forbid "
                            "verification_study"
                        )
                    if (
                        self.submission.response_mode != ResponseMode.FREE_TEXT
                        or self.submission.required_artifacts
                    ):
                        raise ValueError(
                            "MMS derivation cases require response.md and no submitted artifacts"
                        )
                elif self.mms_derivation is not None or self.verification_study is None:
                    raise ValueError(
                        "MMS implementation cases require verification_study and forbid "
                        "mms_derivation"
                    )
                else:
                    required = self.submission.required_artifacts
                    if (
                        self.submission.response_mode != ResponseMode.STRUCTURED_JSON
                        or len(required) != 1
                        or required[0].role != "mms_moose_input"
                        or PurePosixPath(required[0].path).suffix != ".i"
                    ):
                        raise ValueError(
                            "MMS implementation cases require response.json and exactly one "
                            "mms_moose_input .i artifact"
                        )
            elif any(
                item is not None
                for item in (self.mms_task, self.mms_derivation, self.verification_study)
            ):
                raise ValueError("MMS task metadata is reserved for V1 cases")
        else:
            if self.track is not None or self.subcategory is not None:
                raise ValueError("integrated workflow cases must leave track and subcategory unset")
            if not self.required_stages:
                raise ValueError("integrated workflow cases require an ordered stage list")
            if self.scoring_profile != ScoringProfile.BALANCED:
                raise ValueError("integrated workflows require the balanced_v1 scoring profile")
            if any(
                item is not None
                for item in (self.mms_task, self.mms_derivation, self.verification_study)
            ):
                raise ValueError("integrated workflows cannot declare MMS task metadata")
        ids = [item.id for item in [*self.artifacts, *self.evidence_sources]]
        if len(ids) != len(set(ids)):
            raise ValueError("artifact and evidence IDs must be unique within a case")
        if len(self.physics_domains) != len(set(self.physics_domains)):
            raise ValueError("physics domains must be unique")
        if len(self.required_stages) != len(set(self.required_stages)):
            raise ValueError("required workflow stages must be unique")
        if self.track == Track.REPAIR:
            required = self.submission.required_artifacts
            if (
                len(required) != 1
                or required[0].role != "repaired_moose_input"
                or PurePosixPath(required[0].path).suffix != ".i"
            ):
                raise ValueError(
                    "REPAIR cases require exactly one repaired_moose_input .i artifact"
                )
        return self


class EvidenceClaim(StrictModel):
    source_id: str
    observation: str
    interpretation: str


class StructuredResponse(StrictModel):
    claim: dict[str, Any]
    evidence: list[EvidenceClaim]


class MmsRunClaim(StrictModel):
    level: int = Field(ge=0)
    parameter: float = Field(gt=0)
    controls: dict[str, int | float | str]
    errors: dict[str, float]

    @model_validator(mode="after")
    def validate_errors(self) -> MmsRunClaim:
        if not self.errors or any(
            not math.isfinite(value) or value <= 0 for value in self.errors.values()
        ):
            raise ValueError("MMS errors must be finite and positive")
        return self


class MmsClaim(StrictModel):
    norm: str = Field(min_length=1)
    refinement_parameter: Literal["mesh_h", "time_step"]
    runs: list[MmsRunClaim] = Field(min_length=4, max_length=4)
    observed_orders: dict[str, list[float]]
    expected_order: dict[str, float]
    asymptotic_regime: dict[str, bool]
    verdict: Literal["verified", "not_verified", "inconclusive"]
    interpretation: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_claim(self) -> MmsClaim:
        if [item.level for item in self.runs] != list(range(4)):
            raise ValueError("MMS runs must be ordered exactly as levels 0, 1, 2, 3")
        parameters = [item.parameter for item in self.runs]
        if any(left <= right for left, right in zip(parameters[:-1], parameters[1:], strict=True)):
            raise ValueError("MMS refinement parameters must strictly decrease")
        fields = set(self.runs[0].errors)
        if not fields or any(set(run.errors) != fields for run in self.runs):
            raise ValueError("every MMS run must report the same fields")
        if set(self.observed_orders) != fields:
            raise ValueError("observed_orders must define every reported field")
        if any(
            len(values) != 3 or any(not math.isfinite(value) for value in values)
            for values in self.observed_orders.values()
        ):
            raise ValueError("every MMS field must report three finite observed orders")
        if set(self.expected_order) != fields or set(self.asymptotic_regime) != fields:
            raise ValueError("expected_order and asymptotic_regime must define every field")
        if any(not math.isfinite(order) or order <= 0 for order in self.expected_order.values()):
            raise ValueError("expected_order values must be finite and positive")
        return self


class MmsResponse(StrictModel):
    claim: MmsClaim
    evidence: list[EvidenceClaim]


class MmsNumericTolerance(StrictModel):
    absolute: float = Field(default=1e-12, ge=0)
    relative: float = Field(default=1e-6, ge=0)


class MmsReferenceData(StrictModel):
    schema_version: Literal["1.0"]
    norm: str
    refinement_parameter: Literal["mesh_h", "time_step"]
    runs: list[MmsRunClaim] = Field(min_length=4, max_length=4)
    observed_orders: dict[str, list[float]]
    expected_order: dict[str, float]
    asymptotic_regime: dict[str, bool]
    verdict: Literal["verified", "not_verified", "inconclusive"]
    error_tolerance: MmsNumericTolerance = Field(default_factory=MmsNumericTolerance)
    order_tolerance: MmsNumericTolerance = Field(
        default_factory=lambda: MmsNumericTolerance(absolute=1e-8, relative=1e-6)
    )
    moose_revision: str
    executable_sha256: Sha256

    @model_validator(mode="after")
    def validate_reference(self) -> MmsReferenceData:
        MmsClaim(
            norm=self.norm,
            refinement_parameter=self.refinement_parameter,
            runs=self.runs,
            observed_orders=self.observed_orders,
            expected_order=self.expected_order,
            asymptotic_regime=self.asymptotic_regime,
            verdict=self.verdict,
            interpretation="reference",
        )
        return self


class MmsExecutionMeasurement(StrictModel):
    schema_version: Literal["1.0"]
    case_id: str
    submission_sha256: Sha256
    norm: str
    refinement_parameter: Literal["mesh_h", "time_step"]
    runs: list[MmsRunClaim] = Field(min_length=4, max_length=4)
    observed_orders: dict[str, list[float]]
    expected_order: dict[str, float]
    asymptotic_regime: dict[str, bool]
    verdict: Literal["verified", "not_verified", "inconclusive"]

    @model_validator(mode="after")
    def validate_measurement(self) -> MmsExecutionMeasurement:
        MmsClaim(
            norm=self.norm,
            refinement_parameter=self.refinement_parameter,
            runs=self.runs,
            observed_orders=self.observed_orders,
            expected_order=self.expected_order,
            asymptotic_regime=self.asymptotic_regime,
            verdict=self.verdict,
            interpretation="authoritative measurement",
        )
        return self


class RecordedResponse(StrictModel):
    path: str
    media_type: Literal["text/markdown", "application/json"]
    sha256: Sha256
    size_bytes: int = Field(ge=0)

    @model_validator(mode="after")
    def safe_path(self) -> RecordedResponse:
        self.path = validate_relative_path(self.path)
        return self


class RecordedArtifact(StrictModel):
    role: str
    path: str
    sha256: Sha256
    size_bytes: int = Field(ge=0)

    @model_validator(mode="after")
    def safe_path(self) -> RecordedArtifact:
        self.path = validate_relative_path(self.path)
        return self


class TokenUsage(StrictModel):
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    total_tokens: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def validate_total(self) -> TokenUsage:
        if self.total_tokens != self.input_tokens + self.output_tokens:
            raise ValueError("total_tokens must equal input_tokens plus output_tokens")
        return self


class UsageRecord(StrictModel):
    wall_time_seconds: float = Field(ge=0)
    cpu_seconds: float = Field(ge=0)
    memory_mib: float = Field(ge=0)
    validation_attempts: int = Field(ge=0)
    execution_attempts: int = Field(ge=0)
    tokens: TokenUsage | None = None


class ModelIdentity(StrictModel):
    provider: str = Field(min_length=1)
    model: str = Field(min_length=1)
    configuration: dict[str, Any] = Field(default_factory=dict)


class SubmissionRecord(StrictModel):
    schema_version: Literal["2.0"]
    case_id: str
    model: ModelIdentity
    started_at: datetime
    finished_at: datetime
    response: RecordedResponse | None
    artifacts: list[RecordedArtifact]
    usage: UsageRecord
    submission_sha256: Sha256

    @model_validator(mode="after")
    def validate_submission_shape(self) -> SubmissionRecord:
        if self.finished_at < self.started_at:
            raise ValueError("finished_at cannot precede started_at")
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
    weight: float = Field(gt=0, le=1)
    description: str | None = None
    json_pointer: str | None = None
    comparator: ComparatorName | None = None
    expected: Any = None
    absolute_tolerance: float | None = Field(default=None, ge=0)
    relative_tolerance: float | None = Field(default=None, ge=0)
    full_credit: str | None = None
    partial_credit: str | None = None
    common_errors: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_pointer(self) -> CriterionSpec:
        if self.json_pointer is not None:
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
    schema_version: Literal["2.0"]
    case_id: str
    evaluator: str = Field(min_length=1)
    reference_solution: str | None = None
    reference_data: str | None = None
    capability_criteria: list[CriterionSpec]
    evidence_criteria: list[CriterionSpec] = Field(default_factory=list)
    hard_gates: list[GateSpec] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_evaluation(self) -> EvaluationSpec:
        groups = [("capability", self.capability_criteria)]
        if self.evaluator in {
            "structured_claim_v2",
            "mms_claim_v1",
            "mms_derivation_v1",
        }:
            groups.append(("evidence", self.evidence_criteria))
        for label, criteria in groups:
            if not criteria:
                raise ValueError(f"{label} criteria cannot be empty")
            total = sum(item.weight for item in criteria)
            if abs(total - 1.0) > 1e-9:
                raise ValueError(f"{label} criterion weights must sum to 1.0, got {total}")
        if self.evaluator == "semantic_rubric_v1":
            if self.reference_solution is None:
                raise ValueError("semantic evaluators require reference_solution")
            self.reference_solution = validate_relative_path(self.reference_solution)
            if self.evidence_criteria:
                raise ValueError("semantic evaluators cannot declare evidence criteria")
            if any(
                item.full_credit is None
                or item.json_pointer is not None
                or item.comparator is not None
                for item in self.capability_criteria
            ):
                raise ValueError("semantic criteria require full_credit and no JSON comparator")
            if self.reference_data is not None:
                raise ValueError("semantic evaluators cannot declare reference_data")
        elif self.evaluator == "mms_derivation_v1":
            if self.reference_solution is None:
                raise ValueError("MMS derivation evaluators require reference_solution")
            self.reference_solution = validate_relative_path(self.reference_solution)
            if self.reference_data is not None:
                raise ValueError("MMS derivation evaluators cannot declare reference_data")
            criteria = [*self.capability_criteria, *self.evidence_criteria]
            if any(
                item.full_credit is None
                or item.json_pointer is not None
                or item.comparator is not None
                for item in criteria
            ):
                raise ValueError("MMS derivation criteria require semantic rubric text")
            expected_capability = {
                "derivatives_and_residual": 0.25,
                "source_terms": 0.35,
                "boundary_and_initial_data": 0.25,
                "constraints_and_conventions": 0.15,
            }
            expected_evidence = {
                "derivation_trace": 0.70,
                "notation_and_parameter_consistency": 0.30,
            }
            if {item.id: item.weight for item in self.capability_criteria} != expected_capability:
                raise ValueError("MMS derivation capability criteria use fixed IDs and weights")
            if {item.id: item.weight for item in self.evidence_criteria} != expected_evidence:
                raise ValueError("MMS derivation evidence criteria use fixed IDs and weights")
        elif self.evaluator == "structured_claim_v2":
            structured = [*self.capability_criteria, *self.evidence_criteria]
            if any(
                item.description is None or item.json_pointer is None or item.comparator is None
                for item in structured
            ):
                raise ValueError("structured criteria require description and JSON comparator")
            if self.reference_data is not None:
                raise ValueError("structured evaluators cannot declare reference_data")
        elif self.evaluator == "mms_claim_v1":
            if self.reference_data is None:
                raise ValueError("MMS evaluators require reference_data")
            self.reference_data = validate_relative_path(self.reference_data)
            expected_capability_ids = {
                "norm_and_refinement",
                "error_sequence",
                "observed_orders",
                "asymptotic_assessment",
                "verdict",
            }
            if {item.id for item in self.capability_criteria} != expected_capability_ids:
                raise ValueError("MMS capability criteria must use the standard criterion IDs")
            expected_weights = {
                "norm_and_refinement": 0.10,
                "error_sequence": 0.25,
                "observed_orders": 0.25,
                "asymptotic_assessment": 0.20,
                "verdict": 0.20,
            }
            actual_weights = {item.id: item.weight for item in self.capability_criteria}
            if any(
                abs(actual_weights[criterion_id] - weight) > 1e-9
                for criterion_id, weight in expected_weights.items()
            ):
                raise ValueError("MMS capability criteria must use the standard weights")
            expected_evidence_ids = {
                "refinement_trace",
                "arithmetic_consistency",
                "source_binding",
            }
            if {item.id for item in self.evidence_criteria} != expected_evidence_ids:
                raise ValueError("MMS evidence criteria must use the standard criterion IDs")
            if any(
                item.json_pointer is not None or item.comparator is not None
                for item in [*self.capability_criteria, *self.evidence_criteria]
            ):
                raise ValueError("MMS criteria are computed from the typed response")
        criterion_ids = [item.id for item in [*self.capability_criteria, *self.evidence_criteria]]
        if len(criterion_ids) != len(set(criterion_ids)):
            raise ValueError("criterion IDs must be unique")
        gate_ids = [item.id for item in self.hard_gates]
        if len(gate_ids) != len(set(gate_ids)):
            raise ValueError("hard gate IDs must be unique")
        reserved_gate_ids = {"submission_integrity", "resource_budget"}
        if reserved_gate_ids & set(gate_ids):
            raise ValueError("hard gate IDs cannot use automatic gate names")
        return self


class ExternalGateResult(StrictModel):
    schema_version: Literal["2.0"]
    benchmark_id: str
    benchmark_version: str
    case_id: str
    submission_sha256: Sha256
    gate_id: str
    passed: bool
    detail: str
    evidence: list[str] = Field(default_factory=list)
    mms_measurement: MmsExecutionMeasurement | None = None


class EvaluationContext(StrictModel):
    benchmark_id: str
    benchmark_version: str
    submission_sha256: Sha256
    run_record_sha256: Sha256
    submission_root: Path
    public_case_root: Path
    private_case_root: Path


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
    schema_version: Literal["2.0"]
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
    evidence: float | None = Field(default=None, ge=0, le=100)
    contract: float | None = Field(default=None, ge=0, le=100)


class ScoreWeights(StrictModel):
    capability: float = Field(ge=0, le=1)
    evidence: float = Field(ge=0, le=1)
    contract: float = Field(ge=0, le=1)

    @model_validator(mode="after")
    def validate_total(self) -> ScoreWeights:
        if abs(self.capability + self.evidence + self.contract - 1.0) > 1e-9:
            raise ValueError("score weights must sum to 1.0")
        return self


class EvaluatorProvenance(StrictModel):
    provider: str
    model: str
    configuration_sha256: Sha256
    request_sha256: Sha256
    response_sha256: Sha256


class CaseResult(StrictModel):
    schema_version: Literal["2.0"]
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
    run_record_sha256: Sha256
    submitted_artifacts: list[RecordedArtifact]
    scoring_profile: ScoringProfile
    score_weights: ScoreWeights
    component_scores: ComponentScores
    raw_score: float = Field(ge=0, le=100)
    official_score: float = Field(ge=0, le=100)
    gates_passed: bool
    case_passed: bool
    gate_results: list[GateResult]
    criterion_details: dict[str, Any]
    evaluator_provenance: EvaluatorProvenance | None = None
    mms_task: MmsTask | None = None
    verification_study: VerificationStudyType | None = None
    failure_category: (
        Literal[
            "equation_derivation",
            "boundary_initial_data",
            "constraints_conventions",
            "derivation_evidence",
            "input_construction",
            "execution",
            "evidence_integrity",
            "error_calculation",
            "convergence_calculation",
            "interpretation",
        ]
        | None
    ) = None
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
            if self.track == Track.FORM and self.scoring_profile != ScoringProfile.FORM_CAPABILITY:
                raise ValueError("FORM results require the form_capability_v1 scoring profile")
            if self.track != Track.FORM and self.scoring_profile != ScoringProfile.BALANCED:
                raise ValueError("non-FORM results require the balanced_v1 scoring profile")
            if self.subcategory == "V1":
                if self.mms_task is None:
                    raise ValueError("V1 results require mms_task")
                if self.mms_task == MmsTask.DERIVATION and self.verification_study is not None:
                    raise ValueError("MMS derivation results cannot report verification_study")
                if self.mms_task == MmsTask.IMPLEMENTATION and self.verification_study is None:
                    raise ValueError("MMS implementation results require verification_study")
            elif self.mms_task is not None or self.verification_study is not None:
                raise ValueError("MMS result metadata is reserved for V1 results")
        elif self.track is not None or self.subcategory is not None:
            raise ValueError("integrated results must leave track and subcategory null")
        elif self.scoring_profile != ScoringProfile.BALANCED:
            raise ValueError("integrated results require the balanced_v1 scoring profile")
        elif self.mms_task is not None or self.verification_study is not None:
            raise ValueError("integrated results cannot declare MMS result metadata")

        expected_official = self.raw_score if self.gates_passed else 0.0
        if abs(self.official_score - expected_official) > 1e-4:
            raise ValueError("official score is inconsistent with gate status")
        gate_ids = [item.id for item in self.gate_results]
        if len(gate_ids) != len(set(gate_ids)):
            raise ValueError("gate result IDs must be unique")
        if self.gates_passed != all(item.passed for item in self.gate_results):
            raise ValueError("gates_passed is inconsistent with gate results")
        if (
            self.evaluator
            in {
                "semantic_rubric_v1",
                "mms_derivation_v1",
            }
            and self.evaluator_provenance is None
        ):
            raise ValueError("semantic results require evaluator provenance")
        evidence = self.component_scores.evidence
        contract = self.component_scores.contract
        expected_weights = (
            (1.0, 0.0, 0.0)
            if self.scoring_profile == ScoringProfile.FORM_CAPABILITY
            else (0.7, 0.2, 0.1)
        )
        actual_weights = (
            self.score_weights.capability,
            self.score_weights.evidence,
            self.score_weights.contract,
        )
        if any(
            abs(actual - expected) > 1e-9
            for actual, expected in zip(actual_weights, expected_weights, strict=True)
        ):
            raise ValueError("score weights do not match the scoring profile")
        if self.scoring_profile == ScoringProfile.FORM_CAPABILITY and (
            evidence is not None or contract is not None
        ):
            raise ValueError("FORM capability results cannot report evidence or contract scores")
        if self.score_weights.evidence and evidence is None:
            raise ValueError("weighted evidence component cannot be null")
        if self.score_weights.contract and contract is None:
            raise ValueError("weighted contract component cannot be null")
        expected_raw = (
            self.score_weights.capability * self.component_scores.capability
            + self.score_weights.evidence * (evidence or 0.0)
            + self.score_weights.contract * (contract or 0.0)
        )
        if abs(self.raw_score - expected_raw) > 1e-4:
            raise ValueError("raw_score is inconsistent with score weights")
        expected_case_passed = self.gates_passed and self.component_scores.capability >= 80
        if self.scoring_profile == ScoringProfile.BALANCED:
            expected_case_passed = expected_case_passed and self.raw_score >= 80
        if self.case_passed != expected_case_passed:
            raise ValueError("case_passed is inconsistent with score thresholds")
        if self.case_passed and self.first_failed_stage is not None:
            raise ValueError("passing results cannot report a first failed stage")
        return self
