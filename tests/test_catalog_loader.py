import tempfile
import unittest
from pathlib import Path

from pydantic import ValidationError

from moose_benchmark.catalog.loader import (
    load_catalog_document,
    load_coverage_config,
)
from moose_benchmark.catalog.models import CatalogRecord

ROOT = Path(__file__).resolve().parents[1]


class CatalogLoaderTests(unittest.TestCase):
    def test_repository_record_and_templates_load(self):
        paths = [
            ROOT / "catalog/cases/DIAG-THERMAL-SCHEMA-001.md",
            ROOT / "catalog/templates/atomic-case-record.md",
            ROOT / "catalog/templates/integrated-case-record.md",
        ]
        for path in paths:
            with self.subTest(path=path):
                document = load_catalog_document(path)
                self.assertEqual(document.record.catalog_schema_version, "1.0")
                self.assertTrue(document.body.strip())

    def test_missing_frontmatter_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "CASE.md"
            path.write_text("# No frontmatter\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "must start"):
                load_catalog_document(path)

    def test_malformed_frontmatter_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "CASE.md"
            path.write_text("---\ncase_id: [\n---\n# Broken\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "malformed YAML"):
                load_catalog_document(path)

    def test_atomic_subcategory_must_match_track(self):
        document = load_catalog_document(ROOT / "catalog/cases/DIAG-THERMAL-SCHEMA-001.md")
        data = document.record.model_dump(mode="json")
        data["track"] = "FORM"
        with self.assertRaisesRegex(ValidationError, "subcategory must match"):
            CatalogRecord.model_validate(data)

    def test_integrated_record_requires_null_track_and_subcategory(self):
        document = load_catalog_document(ROOT / "catalog/templates/integrated-case-record.md")
        data = document.record.model_dump(mode="json")
        data["track"] = "FORM"
        with self.assertRaisesRegex(ValidationError, "must leave track"):
            CatalogRecord.model_validate(data)

    def test_coverage_configuration_has_matching_totals(self):
        coverage = load_coverage_config(ROOT / "catalog/coverage.yaml")
        self.assertEqual(sum(coverage.track_targets.values()), 120)
        self.assertEqual(
            sum(coverage.track_targets.values()),
            sum(coverage.difficulty_targets.values()),
        )


if __name__ == "__main__":
    unittest.main()
