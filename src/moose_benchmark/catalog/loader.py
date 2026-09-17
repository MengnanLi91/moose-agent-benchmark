"""Load catalog Markdown records and catalog configuration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .models import CatalogRecord, CoverageConfig


@dataclass(frozen=True)
class CatalogDocument:
    path: Path
    record: CatalogRecord
    body: str


def _parse_yaml(text: str, path: Path) -> Any:
    try:
        return yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ValueError(f"{path}: malformed YAML frontmatter: {exc}") from exc


def split_frontmatter(text: str, path: Path) -> tuple[dict[str, Any], str]:
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"{path}: Markdown record must start with YAML frontmatter")

    closing_index = next(
        (index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---"),
        None,
    )
    if closing_index is None:
        raise ValueError(f"{path}: YAML frontmatter is missing its closing delimiter")

    data = _parse_yaml("".join(lines[1:closing_index]), path)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: YAML frontmatter must contain a mapping")
    return data, "".join(lines[closing_index + 1 :])


def load_catalog_document(path: str | Path) -> CatalogDocument:
    resolved = Path(path).resolve()
    data, body = split_frontmatter(resolved.read_text(encoding="utf-8"), resolved)
    return CatalogDocument(
        path=resolved,
        record=CatalogRecord.model_validate(data),
        body=body,
    )


def catalog_record_paths(repo_root: str | Path) -> list[Path]:
    cases_dir = Path(repo_root).resolve() / "catalog/cases"
    if not cases_dir.is_dir():
        raise ValueError(f"catalog cases directory does not exist: {cases_dir}")
    return sorted(cases_dir.glob("*.md"))


def load_catalog_documents(repo_root: str | Path) -> list[CatalogDocument]:
    return [load_catalog_document(path) for path in catalog_record_paths(repo_root)]


def load_coverage_config(path: str | Path) -> CoverageConfig:
    resolved = Path(path).resolve()
    data = _parse_yaml(resolved.read_text(encoding="utf-8"), resolved)
    if not isinstance(data, dict):
        raise ValueError(f"{resolved}: coverage configuration must contain a mapping")
    return CoverageConfig.model_validate(data)
