"""Safe YAML/JSON loading and manifest resolution."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, TypeVar

import yaml
from pydantic import BaseModel

from .contracts import (
    BenchmarkManifest,
    CaseContract,
    EvaluationSpec,
    RecordedArtifact,
    RecordedResponse,
    SubmissionRecord,
)

ModelT = TypeVar("ModelT", bound=BaseModel)


def _load_data(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        return json.loads(text)
    if path.suffix.lower() in {".yaml", ".yml"}:
        return yaml.safe_load(text)
    raise ValueError(f"unsupported data file: {path}")


def load_model(path: str | Path, model: type[ModelT]) -> ModelT:
    resolved = Path(path).resolve()
    return model.model_validate(_load_data(resolved))


def load_manifest(path: str | Path) -> BenchmarkManifest:
    return load_model(path, BenchmarkManifest)


def load_case(path: str | Path) -> CaseContract:
    return load_model(path, CaseContract)


def load_evaluation(path: str | Path) -> EvaluationSpec:
    return load_model(path, EvaluationSpec)


def load_submission_record(path: str | Path) -> SubmissionRecord:
    return load_model(path, SubmissionRecord)


def resolve_inside(root: Path, relative_path: str) -> Path:
    root = root.resolve()
    candidate = (root / relative_path).resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError(f"path escapes root {root}: {relative_path}")
    return candidate


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_model(model: BaseModel) -> str:
    payload = json.dumps(
        model.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def discover_submission_artifact_paths(submission_root: Path) -> list[str]:
    submission_root = submission_root.resolve()
    artifact_root = resolve_inside(submission_root, "artifacts")
    if not artifact_root.exists():
        return []
    if not artifact_root.is_dir():
        raise ValueError("submission artifacts path must be a directory")

    paths = []
    for path in artifact_root.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"submission artifacts cannot contain symlinks: {path}")
        resolved = path.resolve()
        if resolved != submission_root and submission_root not in resolved.parents:
            raise ValueError(f"artifact path escapes submission root: {path}")
        if path.is_file():
            paths.append(path.relative_to(submission_root).as_posix())
        elif not path.is_dir():
            raise ValueError(f"unsupported artifact path: {path}")
    return sorted(paths)


def _update_content_hash(digest: Any, label: str, content: bytes) -> None:
    label_bytes = label.encode("utf-8")
    digest.update(len(label_bytes).to_bytes(8, "big"))
    digest.update(label_bytes)
    digest.update(len(content).to_bytes(8, "big"))
    digest.update(content)


def sha256_submission_content(
    submission_root: Path,
    response: RecordedResponse | None,
    artifacts: list[RecordedArtifact],
) -> str:
    submission_root = submission_root.resolve()
    digest = hashlib.sha256(b"moose-agent-benchmark-submission-v2\0")
    if response is None:
        _update_content_hash(digest, "response", b"")
    else:
        _update_content_hash(digest, "response-path", response.path.encode("utf-8"))
        response_path = resolve_inside(submission_root, response.path)
        _update_content_hash(digest, "response-content", response_path.read_bytes())
    for artifact in sorted(artifacts, key=lambda value: (value.role, value.path)):
        _update_content_hash(digest, "artifact-role", artifact.role.encode("utf-8"))
        _update_content_hash(digest, "artifact-path", artifact.path.encode("utf-8"))
        artifact_path = resolve_inside(submission_root, artifact.path)
        _update_content_hash(digest, "artifact-content", artifact_path.read_bytes())
    return digest.hexdigest()


def case_bundle_paths(
    manifest_path: str | Path,
    case_id: str,
    *,
    include_disabled: bool = False,
) -> tuple[Path, Path]:
    manifest_path = Path(manifest_path).resolve()
    manifest = load_manifest(manifest_path)
    try:
        ref = next(
            item
            for item in manifest.cases
            if item.case_id == case_id and (item.enabled or include_disabled)
        )
    except StopIteration as exc:
        qualifier = "case" if include_disabled else "enabled case"
        raise KeyError(f"{qualifier} not found in manifest: {case_id}") from exc
    root = manifest_path.parent
    return (
        resolve_inside(root, ref.public_case),
        resolve_inside(root, ref.private_evaluation),
    )
