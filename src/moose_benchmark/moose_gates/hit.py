"""Shell-free integration with MOOSE's pinned HIT command."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from ..runner import RunLimits, run_command
from .errors import GateInfrastructureError


@dataclass(frozen=True)
class HitDiff:
    changed_paths: set[str]
    output: str


class HitTool:
    """Invoke the HIT binary built with the selected MOOSE checkout."""

    def __init__(self, moose_dir: Path):
        self.moose_dir = moose_dir.resolve()
        self.executable = self.moose_dir / "framework/contrib/hit/hit"
        if not self.executable.is_file():
            raise GateInfrastructureError(f"HIT executable does not exist: {self.executable}")

    @staticmethod
    def _limits() -> RunLimits:
        return RunLimits(
            wall_time_seconds=30,
            cpu_seconds=20,
            memory_mib=512,
            max_output_bytes=2 * 1024 * 1024,
            max_processes=4,
        )

    def _run(
        self,
        argv: list[str],
        *,
        cwd: Path,
        allowed_exit_codes: set[int] | None = None,
    ) -> str:
        result = run_command(
            [str(self.executable), *argv],
            cwd=cwd,
            limits=self._limits(),
        )
        if result.timed_out or result.output_limit_exceeded or result.process_limit_exceeded:
            raise GateInfrastructureError("HIT command exceeded evaluator limits")
        allowed = allowed_exit_codes or {0}
        if result.exit_code not in allowed:
            detail = result.stderr.strip() or result.stdout.strip()
            raise GateInfrastructureError(f"HIT command failed: {detail}")
        return result.stdout

    def diff(self, left: Path, right: Path) -> HitDiff:
        output = self._run(
            ["diff", str(left.resolve()), str(right.resolve())],
            cwd=left.parent,
            allowed_exit_codes={0, 1},
        )
        return HitDiff(changed_paths=parse_hit_diff_paths(output), output=output)

    def find(self, pattern: str, input_path: Path) -> dict[str, str]:
        output = self._run(
            ["find", pattern, str(input_path.resolve())],
            cwd=input_path.parent,
            allowed_exit_codes={0, 1},
        )
        return parse_hit_find(output)


_DIFFERING_PATH = re.compile(r"^\s*(\S+)\s+\([^)]*:\d+\)\s+has differing values$")
_SECTION_LINE = re.compile(r"^\s*\[([^\]]*)\]\s*$")
_PARAMETER_LINE = re.compile(r"^\s*([A-Za-z0-9_.:+-]+)\s*=")


def _rendered_parameter_paths(lines: list[str]) -> set[str]:
    paths: set[str] = set()
    stack: list[str] = []
    for line in lines:
        section = _SECTION_LINE.match(line)
        if section:
            name = section.group(1)
            if name:
                stack.append(name)
            elif stack:
                stack.pop()
            continue
        parameter = _PARAMETER_LINE.match(line)
        if parameter:
            paths.add("/".join([*stack, parameter.group(1)]))
    return paths


def parse_hit_diff_paths(output: str) -> set[str]:
    """Return order- and comment-insensitive leaf paths reported by ``hit diff``."""

    changed: set[str] = set()
    lines = output.splitlines()
    rendered: list[str] = []
    in_rendered_section = False
    for line in lines:
        if line.startswith("Parameters removed left -> right:") or line.startswith(
            "Parameters added left -> right:"
        ):
            if rendered:
                changed.update(_rendered_parameter_paths(rendered))
                rendered = []
            in_rendered_section = True
            continue
        if line.startswith("Parameters with differing values:"):
            if rendered:
                changed.update(_rendered_parameter_paths(rendered))
                rendered = []
            in_rendered_section = False
            continue
        differing = _DIFFERING_PATH.match(line)
        if differing:
            changed.add(differing.group(1))
            continue
        if in_rendered_section:
            rendered.append(line)
    if rendered:
        changed.update(_rendered_parameter_paths(rendered))
    return changed


_FIND_LINE = re.compile(r"^.+?:\d+\s+(\S+)\s+=\s+(.*)$")


def parse_hit_find(output: str) -> dict[str, str]:
    """Parse path/value records emitted by ``hit find``."""

    values: dict[str, str] = {}
    for line in output.splitlines():
        match = _FIND_LINE.match(line)
        if match:
            values[match.group(1)] = match.group(2).strip()
    return values
