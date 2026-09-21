import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

from moose_benchmark.cli import main

ROOT = Path(__file__).resolve().parents[1]


class CatalogCliTests(unittest.TestCase):
    def test_catalog_validate_exits_successfully(self):
        output = StringIO()
        with redirect_stdout(output), self.assertRaises(SystemExit) as raised:
            main(["catalog", "validate", "--strict", "--repo-root", str(ROOT)])
        self.assertEqual(raised.exception.code, 0)
        self.assertIn("validated 32 catalog case", output.getvalue())

    def test_catalog_report_writes_json(self):
        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "report.json"
            with self.assertRaises(SystemExit) as raised:
                main(
                    [
                        "catalog",
                        "report",
                        "--format",
                        "json",
                        "--output",
                        str(output_path),
                        "--repo-root",
                        str(ROOT),
                    ]
                )
            self.assertEqual(raised.exception.code, 0)
            report = json.loads(output_path.read_text(encoding="utf-8"))
        self.assertEqual(report["totals"]["cataloged"], 32)
        self.assertEqual(report["track_counts"]["DIAG"]["implemented"], 1)

    def test_catalog_validate_returns_one_for_invalid_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            errors = StringIO()
            with redirect_stderr(errors), self.assertRaises(SystemExit) as raised:
                main(["catalog", "validate", "--repo-root", directory])
        self.assertEqual(raised.exception.code, 1)
        self.assertIn("ERROR:", errors.getvalue())


if __name__ == "__main__":
    unittest.main()
