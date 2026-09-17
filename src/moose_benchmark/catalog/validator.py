"""Validate catalog records against benchmark files and workflow policy."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from ..contracts import BenchmarkManifest, CaseContract, ManifestCaseRef
from ..loader import (
    load_case,
    load_evaluation,
    load_manifest,
    load_submission,
    resolve_inside,
)
from .loader import CatalogDocument, catalog_record_paths, load_catalog_document
from .models import CatalogRecord, CatalogStatus


@dataclass
class CaseReadiness:
    public_contract_valid: bool = False
    private_evaluation_valid: bool = False
    manifest_registered: bool = False
    gold_submission_valid: bool = False
    mutant_submission_count: int = 0
    implementation_missing: list[str] = field(default_factory=list)
    completion_missing: list[str] = field(default_factory=list)

    @property
    def implemented(self) -> bool:
        return self.public_contract_valid

    @property
    def complete(self) -> bool:
        return not self.completion_missing


@dataclass
class CatalogValidationResult:
    documents: list[CatalogDocument] = field(default_factory=list)
    readiness: dict[str, CaseReadiness] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


def _identity_errors(record: CatalogRecord, case: CaseContract) -> list[str]:
    errors: list[str] = []
    for field_name in (
        "case_id",
        "title",
        "case_kind",
        "track",
        "subcategory",
        "difficulty",
        "base_problem_id",
    ):
        catalog_value = getattr(record, field_name)
        case_value = getattr(case, field_name)
        if catalog_value != case_value:
            errors.append(
                f"{record.case_id}: catalog {field_name}={catalog_value!s} "
                f"does not match case.yaml {field_name}={case_value!s}"
            )
    if set(record.physics_domains) != set(case.physics_domains):
        errors.append(f"{record.case_id}: catalog physics_domains do not match case.yaml")
    return errors


def _load_manifest_context(
    repo_root: Path,
    result: CatalogValidationResult,
) -> tuple[BenchmarkManifest | None, dict[str, ManifestCaseRef]]:
    manifest_path = repo_root / "benchmark/manifest.yaml"
    try:
        manifest = load_manifest(manifest_path)
    except Exception as exc:
        result.errors.append(f"{manifest_path}: {exc}")
        return None, {}
    return manifest, {ref.case_id: ref for ref in manifest.cases}


def _machine_paths(
    repo_root: Path,
    case_id: str,
    ref: ManifestCaseRef | None,
) -> tuple[Path, Path]:
    benchmark_root = repo_root / "benchmark"
    if ref is not None:
        return (
            resolve_inside(benchmark_root, ref.public_case),
            resolve_inside(benchmark_root, ref.private_evaluation),
        )
    return (
        benchmark_root / f"public/cases/{case_id}/case.yaml",
        benchmark_root / f"private/cases/{case_id}/evaluation.yaml",
    )


def _valid_submission(path: Path, case_id: str, errors: list[str]) -> bool:
    if not path.is_file():
        return False
    try:
        submission = load_submission(path)
    except Exception as exc:
        errors.append(f"{case_id}: invalid submission fixture {path}: {exc}")
        return False
    if submission.case_id != case_id:
        errors.append(f"{case_id}: submission fixture has case_id {submission.case_id}")
        return False
    return True


def _mutant_paths(repo_root: Path, case_id: str) -> list[Path]:
    fixture_dir = repo_root / "benchmark/example-submissions"
    prefix = f"{case_id}-mutant"
    return sorted(path for path in fixture_dir.glob("*.json") if path.stem.startswith(prefix))


def _validate_machine_record(
    repo_root: Path,
    document: CatalogDocument,
    ref: ManifestCaseRef | None,
    result: CatalogValidationResult,
) -> CaseReadiness:
    record = document.record
    readiness = CaseReadiness(manifest_registered=ref is not None)
    case_path, evaluation_path = _machine_paths(repo_root, record.case_id, ref)

    if case_path.is_file():
        try:
            case = load_case(case_path)
            readiness.public_contract_valid = True
            result.errors.extend(_identity_errors(record, case))
        except Exception as exc:
            result.errors.append(f"{record.case_id}: invalid public contract: {exc}")
    elif ref is not None:
        result.errors.append(f"{record.case_id}: manifest public contract is missing: {case_path}")

    if evaluation_path.is_file():
        try:
            evaluation = load_evaluation(evaluation_path)
            readiness.private_evaluation_valid = evaluation.case_id == record.case_id
            if not readiness.private_evaluation_valid:
                result.errors.append(
                    f"{record.case_id}: private evaluation has case_id {evaluation.case_id}"
                )
        except Exception as exc:
            result.errors.append(f"{record.case_id}: invalid private evaluation: {exc}")
    elif ref is not None:
        result.errors.append(
            f"{record.case_id}: manifest private evaluation is missing: {evaluation_path}"
        )

    fixture_dir = repo_root / "benchmark/example-submissions"
    readiness.gold_submission_valid = _valid_submission(
        fixture_dir / f"{record.case_id}.json",
        record.case_id,
        result.errors,
    )
    readiness.mutant_submission_count = sum(
        _valid_submission(path, record.case_id, result.errors)
        for path in _mutant_paths(repo_root, record.case_id)
    )
    return readiness


def _apply_workflow_policy(
    record: CatalogRecord,
    readiness: CaseReadiness,
    errors: list[str],
) -> None:
    checks = (
        (readiness.public_contract_valid, "public contract"),
        (readiness.private_evaluation_valid, "private evaluation"),
        (readiness.manifest_registered, "manifest registration"),
        (readiness.gold_submission_valid, "gold submission fixture"),
        (readiness.mutant_submission_count > 0, "mutant submission fixture"),
    )
    readiness.implementation_missing = [label for passed, label in checks if not passed]
    readiness.completion_missing = list(readiness.implementation_missing)
    if not record.domain_review_complete:
        readiness.completion_missing.append("domain review")
    if not record.benchmark_review_complete:
        readiness.completion_missing.append("benchmark-design review")
    if record.moose_validation_required and not record.moose_validated:
        readiness.completion_missing.append("MOOSE validation")

    if record.status in {CatalogStatus.REVIEW, CatalogStatus.COMPLETE}:
        if record.owner is None:
            errors.append(f"{record.case_id}: {record.status} cases require an owner")
        for missing in readiness.implementation_missing:
            errors.append(f"{record.case_id}: {record.status} case is missing {missing}")
    if record.status == CatalogStatus.COMPLETE:
        if not record.reviewers:
            errors.append(f"{record.case_id}: complete cases require at least one reviewer")
        for missing in readiness.completion_missing:
            if missing not in readiness.implementation_missing:
                errors.append(f"{record.case_id}: complete case is missing {missing}")


def validate_catalog(
    repo_root: str | Path,
    *,
    strict: bool = False,
) -> CatalogValidationResult:
    root = Path(repo_root).resolve()
    result = CatalogValidationResult()
    _, manifest_refs = _load_manifest_context(root, result)

    try:
        paths = catalog_record_paths(root)
    except Exception as exc:
        result.errors.append(str(exc))
        return result

    records_by_id: dict[str, CatalogDocument] = {}
    for path in paths:
        try:
            document = load_catalog_document(path)
        except Exception as exc:
            result.errors.append(str(exc))
            continue
        record = document.record
        if path.stem != record.case_id:
            result.errors.append(f"{path}: filename must match case_id {record.case_id}")
        if record.case_id in records_by_id:
            result.errors.append(f"duplicate catalog case_id: {record.case_id}")
            continue
        records_by_id[record.case_id] = document
        result.documents.append(document)

    for case_id, document in sorted(records_by_id.items()):
        readiness = _validate_machine_record(
            root,
            document,
            manifest_refs.get(case_id),
            result,
        )
        _apply_workflow_policy(document.record, readiness, result.errors)
        result.readiness[case_id] = readiness

    if strict:
        catalog_ids = set(records_by_id)
        for case_id in sorted(set(manifest_refs) - catalog_ids):
            result.errors.append(f"{case_id}: manifest case has no catalog record")
        public_root = root / "benchmark/public/cases"
        public_ids = {path.parent.name for path in public_root.glob("*/case.yaml")}
        for case_id in sorted(public_ids - catalog_ids):
            result.errors.append(f"{case_id}: public case has no catalog record")

    result.errors.sort()
    return result
