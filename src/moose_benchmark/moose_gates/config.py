"""Typed private configuration for protected MOOSE gates."""

from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from ..contracts import StrictModel, validate_relative_path


class GateRunLimits(StrictModel):
    wall_time_seconds: int = Field(gt=0)
    cpu_seconds: int = Field(gt=0)
    memory_mib: int = Field(gt=0)
    max_output_bytes: int = Field(default=10 * 1024 * 1024, gt=0)
    max_processes: int = Field(default=32, gt=0)


class NumericTolerance(StrictModel):
    absolute: float = Field(ge=0)
    relative: float = Field(ge=0)


class GateCommand(StrictModel):
    argv: list[str] = Field(min_length=1)
    cwd: str = "."

    @model_validator(mode="after")
    def validate_cwd(self) -> GateCommand:
        if self.cwd != ".":
            self.cwd = validate_relative_path(self.cwd)
        return self


class MetricExpectation(StrictModel):
    column: str
    row: int = -1
    expected: float
    tolerance: NumericTolerance


class MetricEquality(StrictModel):
    left_column: str
    right_column: str
    row: int = -1
    tolerance: NumericTolerance


class MooseGateConfig(StrictModel):
    schema_version: Literal["1.0"]
    case_id: str
    case_type: Literal[
        "r1_periodic_sideset",
        "r2_coupled_variable_wiring",
        "r3_fieldsplit_partition",
        "r4_lagrange_transient",
    ]
    fixture_dir: str
    overlay_path: str
    input_path: str
    expected_moose_revision: str
    expected_executable_sha256: str | None = None
    authorized_hit_paths: list[str] = Field(default_factory=list)
    coupling_path: str | None = None
    coupling_variable: str | None = None
    required_gates: list[str] = Field(min_length=1)
    commands: dict[str, GateCommand]
    failure_signatures: list[str] = Field(default_factory=list)
    success_signatures: list[str] = Field(default_factory=list)
    csv_path: str | None = None
    metric_expectations: dict[str, MetricExpectation] = Field(default_factory=dict)
    metric_equalities: dict[str, MetricEquality] = Field(default_factory=dict)
    accepted_ranges: dict[str, tuple[float, float]] = Field(default_factory=dict)
    partition_variables: dict[str, list[str]] = Field(default_factory=dict)
    partition_children: dict[str, list[str]] = Field(default_factory=dict)
    minimum_progress_time: float | None = None
    minimum_final_time: float | None = None
    limits: GateRunLimits

    @model_validator(mode="after")
    def validate_paths_and_case_shape(self) -> MooseGateConfig:
        self.fixture_dir = validate_relative_path(self.fixture_dir)
        self.overlay_path = validate_relative_path(self.overlay_path)
        self.input_path = validate_relative_path(self.input_path)
        if self.csv_path is not None:
            self.csv_path = validate_relative_path(self.csv_path)
        if len(self.required_gates) != len(set(self.required_gates)):
            raise ValueError("required_gates must be unique")
        for lower, upper in self.accepted_ranges.values():
            if lower > upper:
                raise ValueError("accepted range lower bound cannot exceed upper bound")
        if not self.authorized_hit_paths:
            raise ValueError("input cases require authorized_hit_paths")
        if self.case_type == "r2_coupled_variable_wiring" and (
            not self.coupling_path or not self.coupling_variable
        ):
            raise ValueError("R2 requires coupling_path and coupling_variable")
        return self
