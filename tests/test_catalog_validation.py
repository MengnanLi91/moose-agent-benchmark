import shutil
import tempfile
import unittest
from pathlib import Path

import yaml

from moose_benchmark.catalog.validator import validate_catalog

ROOT = Path(__file__).resolve().parents[1]


class CatalogValidationTests(unittest.TestCase):
    def copy_repository_data(self) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        shutil.copytree(ROOT / "benchmark", root / "benchmark")
        shutil.copytree(ROOT / "catalog", root / "catalog")
        return root

    def record_path(self, root: Path) -> Path:
        return root / "catalog/cases/DIAG-THERMAL-SCHEMA-001.md"

    def case_path(self, root: Path) -> Path:
        return root / "benchmark/public/cases/DIAG-THERMAL-SCHEMA-001/case.yaml"

    def test_repository_catalog_passes_strict_validation(self):
        result = validate_catalog(ROOT, strict=True)
        self.assertEqual(result.errors, [])
        self.assertTrue(result.readiness["DIAG-THERMAL-SCHEMA-001"].implemented)

    def test_catalog_title_mismatch_fails(self):
        root = self.copy_repository_data()
        path = self.record_path(root)
        text = path.read_text(encoding="utf-8").replace(
            "title: Classify an unregistered MOOSE object failure",
            "title: Different title",
            1,
        )
        path.write_text(text, encoding="utf-8")
        result = validate_catalog(root)
        self.assertTrue(any("catalog title" in error for error in result.errors))

    def test_physics_domain_order_is_not_significant(self):
        root = self.copy_repository_data()
        record_path = self.record_path(root)
        record_text = record_path.read_text(encoding="utf-8").replace(
            "  - thermal_energy_transport\n",
            "  - thermal_energy_transport\n  - coupled_mechanics\n",
            1,
        )
        record_path.write_text(record_text, encoding="utf-8")

        case_path = self.case_path(root)
        case_data = yaml.safe_load(case_path.read_text(encoding="utf-8"))
        case_data["physics_domains"] = [
            "coupled_mechanics",
            "thermal_energy_transport",
        ]
        case_path.write_text(
            yaml.safe_dump(case_data, sort_keys=False),
            encoding="utf-8",
        )
        self.assertEqual(validate_catalog(root).errors, [])

    def test_complete_case_requires_reviews_and_reviewer(self):
        root = self.copy_repository_data()
        path = self.record_path(root)
        text = path.read_text(encoding="utf-8").replace(
            "status: in_progress",
            "status: complete",
            1,
        )
        path.write_text(text, encoding="utf-8")
        errors = validate_catalog(root).errors
        self.assertTrue(any("at least one reviewer" in error for error in errors))
        self.assertTrue(any("domain review" in error for error in errors))
        self.assertTrue(any("benchmark-design review" in error for error in errors))

    def test_required_moose_validation_blocks_completion(self):
        root = self.copy_repository_data()
        path = self.record_path(root)
        text = path.read_text(encoding="utf-8")
        text = text.replace("status: in_progress", "status: complete", 1)
        text = text.replace("reviewers: []", "reviewers:\n  - reviewer", 1)
        text = text.replace("domain_review_complete: false", "domain_review_complete: true", 1)
        text = text.replace(
            "benchmark_review_complete: false",
            "benchmark_review_complete: true",
            1,
        )
        text = text.replace(
            "moose_validation_required: false",
            "moose_validation_required: true",
            1,
        )
        path.write_text(text, encoding="utf-8")
        errors = validate_catalog(root).errors
        self.assertEqual(
            [error for error in errors if "complete case is missing" in error],
            ["DIAG-THERMAL-SCHEMA-001: complete case is missing MOOSE validation"],
        )

    def test_review_case_requires_mutant_fixture(self):
        root = self.copy_repository_data()
        path = self.record_path(root)
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "status: in_progress",
                "status: review",
                1,
            ),
            encoding="utf-8",
        )
        mutant = root / "benchmark/example-submissions/DIAG-THERMAL-SCHEMA-001-mutant.json"
        mutant.unlink()
        errors = validate_catalog(root).errors
        self.assertTrue(any("missing mutant submission fixture" in error for error in errors))

    def test_strict_mode_requires_catalog_record(self):
        root = self.copy_repository_data()
        self.record_path(root).unlink()
        errors = validate_catalog(root, strict=True).errors
        self.assertTrue(any("manifest case has no catalog record" in error for error in errors))
        self.assertTrue(any("public case has no catalog record" in error for error in errors))

    def test_filename_must_match_case_id(self):
        root = self.copy_repository_data()
        self.record_path(root).rename(root / "catalog/cases/WRONG.md")
        errors = validate_catalog(root).errors
        self.assertTrue(any("filename must match case_id" in error for error in errors))

    def test_duplicate_case_id_fails(self):
        root = self.copy_repository_data()
        shutil.copy2(self.record_path(root), root / "catalog/cases/DUPLICATE.md")
        errors = validate_catalog(root).errors
        self.assertTrue(any("duplicate catalog case_id" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
