"""Protected MOOSE gate generation API."""

from .base import prepare_workspace, verify_tools
from .cases import generate_case_gates
from .config import MmsGateConfig, MooseGateConfig, load_gate_config
from .errors import GateInfrastructureError
from .mms import (
    build_reference_data,
    generate_mms_gates,
    reference_data_matches,
    run_mms_study,
    write_validation_artifacts,
)

__all__ = [
    "GateInfrastructureError",
    "MmsGateConfig",
    "MooseGateConfig",
    "build_reference_data",
    "generate_case_gates",
    "generate_mms_gates",
    "load_gate_config",
    "prepare_workspace",
    "reference_data_matches",
    "run_mms_study",
    "verify_tools",
    "write_validation_artifacts",
]
