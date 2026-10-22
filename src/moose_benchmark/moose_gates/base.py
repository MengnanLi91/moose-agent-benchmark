"""Workspace, provenance, and command helpers for protected MOOSE gates."""

from __future__ import annotations

import os
import shutil
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from ..contracts import (
    EvaluationContext,
    ExternalGateResult,
    MmsExecutionMeasurement,
    SubmissionRecord,
)
from ..loader import resolve_inside, sha256_file, sha256_submission_content
from ..runner import RunLimits, RunResult, run_command
from .config import MmsGateConfig, MooseGateConfig
from .errors import GateInfrastructureError


@dataclass
class GateWorkspace:
    root: Path
    reference_artifact: bytes
    candidate_path: Path


@dataclass(frozen=True)
class GateTools:
    moose_dir: Path
    executable: Path
    hit: Path


def _verify_submission_files(
    submission_root: Path,
    submission: SubmissionRecord,
    expected_artifact_path: str,
) -> Path:
    if len(submission.artifacts) != 1:
        raise ValueError("gate generation requires exactly one recorded artifact")
    artifact = submission.artifacts[0]
    if artifact.path != expected_artifact_path:
        raise ValueError(
            f"recorded artifact path {artifact.path!r} does not match {expected_artifact_path!r}"
        )
    unresolved_candidate = submission_root / artifact.path
    if unresolved_candidate.is_symlink():
        raise ValueError(f"submission artifact is a symlink: {unresolved_candidate}")
    candidate = resolve_inside(submission_root, artifact.path)
    if not candidate.is_file():
        raise ValueError(f"submission artifact is not a regular file: {candidate}")
    if candidate.stat().st_size != artifact.size_bytes or sha256_file(candidate) != artifact.sha256:
        raise ValueError("submission artifact does not match its runner-owned record")
    if submission.response is not None:
        unresolved_response = submission_root / submission.response.path
        if unresolved_response.is_symlink():
            raise ValueError(f"submission response is a symlink: {unresolved_response}")
        response = resolve_inside(submission_root, submission.response.path)
        if (
            not response.is_file()
            or response.stat().st_size != submission.response.size_bytes
            or sha256_file(response) != submission.response.sha256
        ):
            raise ValueError("submission response does not match its runner-owned record")
    content_hash = sha256_submission_content(
        submission_root,
        submission.response,
        submission.artifacts,
    )
    if content_hash != submission.submission_sha256:
        raise ValueError("submission hash does not match recorded content")
    return candidate


@contextmanager
def prepare_workspace(
    private_case_root: Path,
    submission_root: Path,
    submission: SubmissionRecord,
    expected_artifact_path: str,
    config: MooseGateConfig,
) -> Iterator[GateWorkspace]:
    fixture = resolve_inside(private_case_root, config.fixture_dir)
    if not fixture.is_dir():
        raise GateInfrastructureError(f"private fixture directory does not exist: {fixture}")
    candidate = _verify_submission_files(
        submission_root.resolve(),
        submission,
        expected_artifact_path,
    )
    with tempfile.TemporaryDirectory(prefix=f"{config.case_id}-") as directory:
        root = Path(directory) / "fixture"
        shutil.copytree(fixture, root)
        overlay = resolve_inside(root, config.overlay_path)
        if not overlay.is_file() or overlay.is_symlink():
            raise GateInfrastructureError(f"fixture overlay target is invalid: {overlay}")
        reference_artifact = overlay.read_bytes()
        overlay.write_bytes(candidate.read_bytes())
        yield GateWorkspace(
            root=root,
            reference_artifact=reference_artifact,
            candidate_path=overlay,
        )


def verify_tools(
    moose_dir: Path,
    executable: Path,
    config: MooseGateConfig | MmsGateConfig,
) -> GateTools:
    moose_dir = moose_dir.resolve()
    executable = executable.resolve()
    if not moose_dir.is_dir():
        raise GateInfrastructureError(f"MOOSE checkout does not exist: {moose_dir}")
    if executable != moose_dir and moose_dir not in executable.parents:
        raise GateInfrastructureError("MOOSE executable must be inside the selected checkout")
    if not executable.is_file() or not os.access(executable, os.X_OK):
        raise GateInfrastructureError(f"MOOSE executable is not runnable: {executable}")
    if (
        config.expected_executable_sha256 is not None
        and sha256_file(executable) != config.expected_executable_sha256
    ):
        raise GateInfrastructureError("MOOSE executable hash does not match gate configuration")

    git = shutil.which("git")
    if git is None:
        raise GateInfrastructureError("git is required to verify the MOOSE revision")
    result = run_command(
        [str(Path(git).resolve()), "-C", str(moose_dir), "rev-parse", "HEAD"],
        cwd=moose_dir,
        limits=RunLimits(
            wall_time_seconds=30,
            cpu_seconds=10,
            memory_mib=512,
            max_output_bytes=1024 * 1024,
            max_processes=4,
        ),
    )
    if result.exit_code != 0 or result.timed_out or result.output_limit_exceeded:
        detail = result.stderr.strip() or result.stdout.strip()
        raise GateInfrastructureError(f"could not verify MOOSE revision: {detail}")
    if result.stdout.strip() != config.expected_moose_revision:
        raise GateInfrastructureError(
            "MOOSE revision does not match gate configuration: "
            f"{result.stdout.strip()} != {config.expected_moose_revision}"
        )
    hit = moose_dir / "framework/contrib/hit/hit"
    if not hit.is_file() or not os.access(hit, os.X_OK):
        raise GateInfrastructureError(f"HIT executable is not runnable: {hit}")
    return GateTools(moose_dir=moose_dir, executable=executable, hit=hit)


_ENVIRONMENT_ALLOWLIST = (
    "PATH",
    "HOME",
    "TMPDIR",
    "LD_LIBRARY_PATH",
    "DYLD_LIBRARY_PATH",
    "PETSC_DIR",
    "PETSC_ARCH",
    "LIBMESH_DIR",
    "WASP_DIR",
    "CC",
    "CXX",
    "METHOD",
    "MOOSE_JOBS",
    "FI_PROVIDER",
    "FI_TCP_IFACE",
    "FI_SOCKETS_IFACE",
)


def _safe_environment(tools: GateTools) -> dict[str, str]:
    environment = {name: os.environ[name] for name in _ENVIRONMENT_ALLOWLIST if name in os.environ}
    environment["MOOSE_DIR"] = str(tools.moose_dir)
    return environment


def safe_environment(tools: GateTools) -> dict[str, str]:
    return _safe_environment(tools)


def run_configured_command(
    config: MooseGateConfig,
    command_name: str,
    workspace: GateWorkspace,
    tools: GateTools,
) -> RunResult:
    try:
        command = config.commands[command_name]
    except KeyError as exc:
        raise GateInfrastructureError(
            f"gate configuration has no {command_name!r} command"
        ) from exc
    values = {
        "workspace": str(workspace.root),
        "moose_dir": str(tools.moose_dir),
        "executable": str(tools.executable),
        "input": str(resolve_inside(workspace.root, config.input_path)),
    }
    try:
        argv = [argument.format_map(values) for argument in command.argv]
    except KeyError as exc:
        raise GateInfrastructureError(f"unknown gate command placeholder: {exc}") from exc
    command_path = Path(argv[0])
    if not command_path.is_absolute():
        located = shutil.which(argv[0], path=os.environ.get("PATH"))
        if located is None:
            raise GateInfrastructureError(f"gate command executable was not found: {argv[0]}")
        argv[0] = str(Path(located).resolve())
    cwd = workspace.root if command.cwd == "." else resolve_inside(workspace.root, command.cwd)
    if not cwd.is_dir():
        raise GateInfrastructureError(f"gate command working directory does not exist: {cwd}")
    limits = RunLimits(
        wall_time_seconds=config.limits.wall_time_seconds,
        cpu_seconds=config.limits.cpu_seconds,
        memory_mib=config.limits.memory_mib,
        max_output_bytes=config.limits.max_output_bytes,
        max_processes=config.limits.max_processes,
    )
    try:
        result = run_command(
            argv,
            cwd=cwd,
            limits=limits,
            environment=_safe_environment(tools),
        )
    except (OSError, ValueError) as exc:
        raise GateInfrastructureError(
            f"could not start gate command {command_name}: {exc}"
        ) from exc
    if not result.process_limit_enforced:
        raise GateInfrastructureError("process-count enforcement is unavailable")
    return result


def command_succeeded(result: RunResult) -> bool:
    return bool(
        result.exit_code == 0
        and not result.timed_out
        and not result.output_limit_exceeded
        and not result.process_limit_exceeded
    )


def external_gate_result(
    context: EvaluationContext,
    submission: SubmissionRecord,
    gate_id: str,
    passed: bool,
    detail: str,
    evidence: list[str] | None = None,
    mms_measurement: MmsExecutionMeasurement | None = None,
) -> ExternalGateResult:
    if submission.submission_sha256 != context.submission_sha256:
        raise ValueError("evaluation context does not match the submission record")
    return ExternalGateResult(
        schema_version="2.0",
        benchmark_id=context.benchmark_id,
        benchmark_version=context.benchmark_version,
        case_id=submission.case_id,
        submission_sha256=submission.submission_sha256,
        gate_id=gate_id,
        passed=passed,
        detail=detail,
        evidence=evidence or [],
        mms_measurement=mms_measurement,
    )


def validate_gate_results(
    config: MooseGateConfig | MmsGateConfig,
    results: list[ExternalGateResult],
) -> list[ExternalGateResult]:
    actual = [result.gate_id for result in results]
    if len(actual) != len(set(actual)):
        raise GateInfrastructureError("gate runner produced duplicate gate IDs")
    if set(actual) != set(config.required_gates):
        missing = sorted(set(config.required_gates) - set(actual))
        unexpected = sorted(set(actual) - set(config.required_gates))
        raise GateInfrastructureError(
            f"gate runner/config mismatch; missing={missing}, unexpected={unexpected}"
        )
    by_id = {result.gate_id: result for result in results}
    return [by_id[gate_id] for gate_id in config.required_gates]
