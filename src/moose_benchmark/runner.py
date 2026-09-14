"""Bounded, shell-free execution support for MOOSE check-input and smoke runs."""

from __future__ import annotations

import os
import platform
import resource
import signal
import subprocess
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from .loader import resolve_inside


@dataclass(frozen=True)
class RunLimits:
    wall_time_seconds: int
    cpu_seconds: int
    memory_mib: int

    def __post_init__(self) -> None:
        for name, value in asdict(self).items():
            if value <= 0:
                raise ValueError(f"{name} must be positive")


@dataclass(frozen=True)
class RunResult:
    argv: list[str]
    exit_code: int | None
    timed_out: bool
    wall_time_seconds: float
    stdout: str
    stderr: str
    memory_limit_enforced: bool

    def to_dict(self) -> dict:
        return asdict(self)


def _memory_limit_supported() -> bool:
    return platform.system() == "Linux" and hasattr(resource, "RLIMIT_AS")


def _resource_limiter(limits: RunLimits):
    def apply() -> None:
        resource.setrlimit(resource.RLIMIT_CPU, (limits.cpu_seconds, limits.cpu_seconds))
        if _memory_limit_supported():
            memory_bytes = limits.memory_mib * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))

    return apply


def run_command(
    argv: list[str],
    *,
    cwd: Path,
    limits: RunLimits,
    environment: dict[str, str] | None = None,
) -> RunResult:
    if not argv:
        raise ValueError("argv cannot be empty")
    executable = Path(argv[0])
    if not executable.is_absolute():
        raise ValueError("the executable must be an absolute path")
    if not executable.is_file() or not os.access(executable, os.X_OK):
        raise ValueError(f"executable is not runnable: {executable}")
    cwd = cwd.resolve()
    if not cwd.is_dir():
        raise ValueError(f"working directory does not exist: {cwd}")

    started = time.monotonic()
    memory_limit_enforced = _memory_limit_supported()
    process = subprocess.Popen(
        argv,
        cwd=cwd,
        env=environment if environment is not None else {"PATH": os.environ.get("PATH", "")},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
        preexec_fn=_resource_limiter(limits),
    )
    try:
        stdout, stderr = process.communicate(timeout=limits.wall_time_seconds)
        return RunResult(
            argv=argv,
            exit_code=process.returncode,
            timed_out=False,
            wall_time_seconds=round(time.monotonic() - started, 4),
            stdout=stdout,
            stderr=stderr,
            memory_limit_enforced=memory_limit_enforced,
        )
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        stdout, stderr = process.communicate()
        return RunResult(
            argv=argv,
            exit_code=None,
            timed_out=True,
            wall_time_seconds=round(time.monotonic() - started, 4),
            stdout=stdout,
            stderr=stderr,
            memory_limit_enforced=memory_limit_enforced,
        )


def run_moose_check(
    executable: Path,
    case_root: Path,
    input_path: str,
    limits: RunLimits,
) -> RunResult:
    executable = executable.resolve()
    if not executable.is_file() or not os.access(executable, os.X_OK):
        raise ValueError(f"MOOSE executable is not executable: {executable}")
    case_root = case_root.resolve()
    input_file = resolve_inside(case_root, input_path)
    if not input_file.is_file():
        raise ValueError(f"MOOSE input does not exist: {input_file}")
    return run_command(
        [str(executable), "-i", str(input_file), "--check-input"],
        cwd=case_root,
        limits=limits,
        environment={
            "PATH": os.environ.get("PATH", ""),
            "LD_LIBRARY_PATH": os.environ.get("LD_LIBRARY_PATH", ""),
        },
    )
