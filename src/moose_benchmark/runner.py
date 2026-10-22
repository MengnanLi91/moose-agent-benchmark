"""Bounded, shell-free execution support for MOOSE check-input and smoke runs."""

from __future__ import annotations

import ctypes
import os
import platform
import resource
import signal
import subprocess
import tempfile
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from .contracts import (
    CaseContract,
    ModelIdentity,
    RecordedArtifact,
    RecordedResponse,
    ResponseMode,
    SubmissionRecord,
    UsageRecord,
)
from .loader import (
    discover_submission_artifact_paths,
    resolve_inside,
    sha256_file,
    sha256_submission_content,
)


@dataclass(frozen=True)
class RunLimits:
    wall_time_seconds: int
    cpu_seconds: int
    memory_mib: int
    max_output_bytes: int = 10 * 1024 * 1024
    max_processes: int = 32

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
    output_limit_exceeded: bool
    process_limit_exceeded: bool
    process_limit_enforced: bool

    def to_dict(self) -> dict:
        return asdict(self)


def _memory_limit_supported() -> bool:
    return platform.system() == "Linux" and hasattr(resource, "RLIMIT_AS")


def _darwin_child_pids(pid: int) -> list[int] | None:
    try:
        libproc = ctypes.CDLL("/usr/lib/libproc.dylib")
        proc_listchildpids = libproc.proc_listchildpids
    except (AttributeError, OSError):
        return None
    proc_listchildpids.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_int]
    proc_listchildpids.restype = ctypes.c_int
    required_bytes = proc_listchildpids(pid, None, 0)
    if required_bytes < 0:
        return None
    capacity = max(1, required_bytes // ctypes.sizeof(ctypes.c_int))
    child_pids = (ctypes.c_int * capacity)()
    count = proc_listchildpids(pid, child_pids, ctypes.sizeof(child_pids))
    if count < 0:
        return None
    return [child_pids[index] for index in range(count)]


def _process_limit_supported() -> bool:
    if platform.system() == "Linux" and Path("/proc").is_dir():
        return True
    if platform.system() == "Darwin":
        return _darwin_child_pids(os.getpid()) is not None
    if not Path("/bin/ps").is_file():
        return False
    try:
        completed = subprocess.run(
            ["/bin/ps", "-axo", "pgid="],
            check=False,
            capture_output=True,
            timeout=2,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return completed.returncode == 0


def _linux_process_count(pid: int) -> int:
    pending = [pid]
    descendants: set[int] = set()
    while pending:
        current = pending.pop()
        children_path = Path(f"/proc/{current}/task/{current}/children")
        try:
            children = [int(value) for value in children_path.read_text().split()]
        except (FileNotFoundError, PermissionError, ProcessLookupError):
            continue
        for child in children:
            if child not in descendants:
                descendants.add(child)
                pending.append(child)
    return 1 + len(descendants)


def _darwin_process_count(pid: int) -> int:
    pending = [pid]
    descendants: set[int] = set()
    while pending:
        children = _darwin_child_pids(pending.pop())
        if children is None:
            return 0
        for child in children:
            if child not in descendants:
                descendants.add(child)
                pending.append(child)
    return 1 + len(descendants)


def _process_count(pid: int) -> int:
    if platform.system() == "Linux" and Path("/proc").is_dir():
        return _linux_process_count(pid)
    if platform.system() == "Darwin":
        return _darwin_process_count(pid)
    try:
        completed = subprocess.run(
            ["/bin/ps", "-axo", "pgid="],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return 0
    if completed.returncode != 0:
        return 0
    try:
        process_group = str(os.getpgid(pid))
    except ProcessLookupError:
        return 0
    return sum(line.strip() == process_group for line in completed.stdout.splitlines())


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
    process_limit_enforced = _process_limit_supported()
    timed_out = False
    output_limit_exceeded = False
    process_limit_exceeded = False
    with tempfile.TemporaryFile() as stdout_stream, tempfile.TemporaryFile() as stderr_stream:
        process = subprocess.Popen(
            argv,
            cwd=cwd,
            env=environment if environment is not None else {"PATH": os.environ.get("PATH", "")},
            stdout=stdout_stream,
            stderr=stderr_stream,
            start_new_session=True,
            preexec_fn=_resource_limiter(limits),
        )
        while process.poll() is None:
            elapsed = time.monotonic() - started
            output_size = (
                os.fstat(stdout_stream.fileno()).st_size + os.fstat(stderr_stream.fileno()).st_size
            )
            timed_out = elapsed >= limits.wall_time_seconds
            output_limit_exceeded = output_size > limits.max_output_bytes
            process_limit_exceeded = (
                process_limit_enforced and _process_count(process.pid) > limits.max_processes
            )
            if timed_out or output_limit_exceeded or process_limit_exceeded:
                break
            time.sleep(0.02)

        if process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except PermissionError:
                try:
                    process.kill()
                except ProcessLookupError:
                    pass
            except ProcessLookupError:
                pass
        process.wait()
        output_size = (
            os.fstat(stdout_stream.fileno()).st_size + os.fstat(stderr_stream.fileno()).st_size
        )
        output_limit_exceeded = output_limit_exceeded or output_size > limits.max_output_bytes
        stdout_stream.seek(0)
        stderr_stream.seek(0)
        stdout = stdout_stream.read(limits.max_output_bytes).decode("utf-8", errors="replace")
        remaining_bytes = max(0, limits.max_output_bytes - len(stdout.encode("utf-8")))
        stderr = stderr_stream.read(remaining_bytes).decode("utf-8", errors="replace")

    return RunResult(
        argv=argv,
        exit_code=None if timed_out else process.returncode,
        timed_out=timed_out,
        wall_time_seconds=round(time.monotonic() - started, 4),
        stdout=stdout,
        stderr=stderr,
        memory_limit_enforced=memory_limit_enforced,
        output_limit_exceeded=output_limit_exceeded,
        process_limit_exceeded=process_limit_exceeded,
        process_limit_enforced=process_limit_enforced,
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


def build_submission_record(
    case: CaseContract,
    submission_root: Path,
    *,
    model: ModelIdentity,
    started_at: datetime,
    finished_at: datetime,
    usage: UsageRecord,
) -> SubmissionRecord:
    submission_root = submission_root.resolve()
    if not submission_root.is_dir():
        raise ValueError(f"submission directory does not exist: {submission_root}")

    response_name = (
        "response.json"
        if case.submission.response_mode == ResponseMode.STRUCTURED_JSON
        else "response.md"
    )
    response_path = resolve_inside(submission_root, response_name)
    response = None
    if response_path.is_file():
        response = RecordedResponse(
            path=response_name,
            media_type=(
                "application/json"
                if case.submission.response_mode == ResponseMode.STRUCTURED_JSON
                else "text/markdown"
            ),
            sha256=sha256_file(response_path),
            size_bytes=response_path.stat().st_size,
        )
    elif case.submission.response_mode != ResponseMode.ARTIFACT:
        raise ValueError(f"required response does not exist: {response_path}")

    artifacts = []
    artifact_roles = {
        required.path: required.role for required in case.submission.required_artifacts
    }
    discovered_paths = discover_submission_artifact_paths(submission_root)
    unexpected_paths = set(discovered_paths) - set(artifact_roles)
    if unexpected_paths:
        raise ValueError("undeclared submission artifacts: " + ", ".join(sorted(unexpected_paths)))
    for required in case.submission.required_artifacts:
        path = resolve_inside(submission_root, required.path)
        if not path.is_file():
            raise ValueError(f"required submission artifact does not exist: {path}")
        artifacts.append(
            RecordedArtifact(
                role=required.role,
                path=required.path,
                sha256=sha256_file(path),
                size_bytes=path.stat().st_size,
            )
        )
    submission_sha256 = sha256_submission_content(submission_root, response, artifacts)
    return SubmissionRecord(
        schema_version="2.0",
        case_id=case.case_id,
        model=model,
        started_at=started_at,
        finished_at=finished_at,
        response=response,
        artifacts=artifacts,
        usage=usage,
        submission_sha256=submission_sha256,
    )
