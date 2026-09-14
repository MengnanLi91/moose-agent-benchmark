"""Safe YAML/JSON loading and manifest resolution."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, TypeVar

import yaml
from pydantic import BaseModel

from .contracts import BenchmarkManifest, CaseContract, EvaluationSpec, SubmissionEnvelope

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


def load_submission(path: str | Path) -> SubmissionEnvelope:
    return load_model(path, SubmissionEnvelope)


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


def case_bundle_paths(manifest_path: str | Path, case_id: str) -> tuple[Path, Path]:
    manifest_path = Path(manifest_path).resolve()
    manifest = load_manifest(manifest_path)
    try:
        ref = next(item for item in manifest.cases if item.case_id == case_id and item.enabled)
    except StopIteration as exc:
        raise KeyError(f"enabled case not found in manifest: {case_id}") from exc
    root = manifest_path.parent
    return (
        resolve_inside(root, ref.public_case),
        resolve_inside(root, ref.private_evaluation),
    )
