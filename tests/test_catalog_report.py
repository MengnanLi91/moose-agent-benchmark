import json
import shutil
import tempfile
import unittest
from pathlib import Path

from moose_benchmark.catalog.loader import load_coverage_config
from moose_benchmark.catalog.report import build_catalog_report, format_catalog_report
from moose_benchmark.catalog.validator import validate_catalog

ROOT = Path(__file__).resolve().parents[1]


class CatalogReportTests(unittest.TestCase):
    def build_repository_report(self):
        validation = validate_catalog(ROOT)
        self.assertEqual(validation.errors, [])
        coverage = load_coverage_config(ROOT / "catalog/coverage.yaml")
        return build_catalog_report(validation, coverage)

    def test_repository_counts(self):
        report = self.build_repository_report()
        self.assertEqual(report["target_total"], 120)
        self.assertEqual(report["totals"]["cataloged"], 32)
        self.assertEqual(report["totals"]["atomic"], 32)
        self.assertEqual(report["totals"]["implemented"], 1)
        self.assertEqual(report["totals"]["complete"], 0)
        self.assertEqual(report["status_counts"]["planned"], 31)
        self.assertTrue(all(values["cataloged"] == 8 for values in report["track_counts"].values()))
        self.assertTrue(
            all(values["cataloged"] == 2 for values in report["subcategory_counts"].values())
        )
        self.assertEqual(report["subcategory_counts"]["D1"]["implemented"], 1)

    def test_json_report_is_deterministic(self):
        first = json.dumps(self.build_repository_report(), sort_keys=True)
        second = json.dumps(self.build_repository_report(), sort_keys=True)
        self.assertEqual(first, second)

    def test_text_report_contains_progress_categories(self):
        text = format_catalog_report(self.build_repository_report())
        self.assertIn("cataloged / implemented / complete / target", text)
        self.assertIn("DIAG", text)
        self.assertIn("D1", text)

    def test_integrated_cases_are_reported_separately(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / "benchmark", root / "benchmark")
            shutil.copytree(ROOT / "catalog", root / "catalog")
            shutil.copy2(
                root / "catalog/templates/integrated-case-record.md",
                root / "catalog/cases/INTEGRATED-EXAMPLE-001.md",
            )
            validation = validate_catalog(root)
            self.assertEqual(validation.errors, [])
            coverage = load_coverage_config(root / "catalog/coverage.yaml")
            report = build_catalog_report(validation, coverage)
        self.assertEqual(report["totals"]["integrated"], 1)
        self.assertEqual(report["totals"]["atomic"], 32)
        self.assertEqual(report["track_counts"]["DIAG"]["cataloged"], 8)
        self.assertEqual(report["difficulty_counts"]["L4"]["cataloged"], 1)


if __name__ == "__main__":
    unittest.main()
