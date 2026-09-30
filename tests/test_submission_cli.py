import json
import shutil
import tempfile
import unittest
from pathlib import Path

from moose_benchmark.cli import main

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "benchmark/manifest.yaml"


class SubmissionCliTests(unittest.TestCase):
    def test_record_and_score_structured_submission(self):
        source = ROOT / "benchmark/example-submissions/D1-SOLVER-DTMIN-001/response.json"
        with tempfile.TemporaryDirectory() as directory:
            submission_root = Path(directory) / "submission"
            submission_root.mkdir()
            shutil.copy2(source, submission_root / "response.json")
            with self.assertRaises(SystemExit) as recorded:
                main(
                    [
                        "record-submission",
                        "--manifest",
                        str(MANIFEST),
                        "--case-id",
                        "D1-SOLVER-DTMIN-001",
                        "--submission-dir",
                        str(submission_root),
                        "--model-provider",
                        "fixture",
                        "--model",
                        "cli-test",
                    ]
                )
            self.assertEqual(recorded.exception.code, 0)
            self.assertTrue((submission_root / "run-record.json").is_file())

            output = Path(directory) / "result.json"
            with self.assertRaises(SystemExit) as scored:
                main(
                    [
                        "score",
                        "--manifest",
                        str(MANIFEST),
                        "--case-id",
                        "D1-SOLVER-DTMIN-001",
                        "--submission-dir",
                        str(submission_root),
                        "--output",
                        str(output),
                    ]
                )
            self.assertEqual(scored.exception.code, 0)
            result = json.loads(output.read_text(encoding="utf-8"))
        self.assertTrue(result["case_passed"])
        self.assertEqual(result["schema_version"], "2.0")

    def test_record_rejects_undeclared_artifact(self):
        source = ROOT / "benchmark/example-submissions/F1-SOLID-DUCT-BOWING-001/response.md"
        with tempfile.TemporaryDirectory() as directory:
            submission_root = Path(directory) / "submission"
            artifact_root = submission_root / "artifacts"
            artifact_root.mkdir(parents=True)
            shutil.copy2(source, submission_root / "response.md")
            (artifact_root / "unexpected.txt").write_text("not allowed", encoding="utf-8")

            with self.assertRaises(SystemExit) as recorded:
                main(
                    [
                        "record-submission",
                        "--manifest",
                        str(MANIFEST),
                        "--case-id",
                        "F1-SOLID-DUCT-BOWING-001",
                        "--submission-dir",
                        str(submission_root),
                        "--model-provider",
                        "fixture",
                        "--model",
                        "cli-test",
                    ]
                )
            self.assertEqual(recorded.exception.code, 2)
            self.assertFalse((submission_root / "run-record.json").exists())

    def test_score_detects_content_tampering_after_recording(self):
        source = ROOT / "benchmark/example-submissions/D1-SOLVER-DTMIN-001/response.json"
        with tempfile.TemporaryDirectory() as directory:
            submission_root = Path(directory) / "submission"
            submission_root.mkdir()
            shutil.copy2(source, submission_root / "response.json")
            with self.assertRaises(SystemExit) as recorded:
                main(
                    [
                        "record-submission",
                        "--manifest",
                        str(MANIFEST),
                        "--case-id",
                        "D1-SOLVER-DTMIN-001",
                        "--submission-dir",
                        str(submission_root),
                        "--model-provider",
                        "fixture",
                        "--model",
                        "cli-test",
                    ]
                )
            self.assertEqual(recorded.exception.code, 0)
            response = json.loads((submission_root / "response.json").read_text(encoding="utf-8"))
            response["claim"]["terminal_symptom"] = "tampered"
            (submission_root / "response.json").write_text(
                json.dumps(response),
                encoding="utf-8",
            )

            output = Path(directory) / "result.json"
            with self.assertRaises(SystemExit) as scored:
                main(
                    [
                        "score",
                        "--manifest",
                        str(MANIFEST),
                        "--case-id",
                        "D1-SOLVER-DTMIN-001",
                        "--submission-dir",
                        str(submission_root),
                        "--output",
                        str(output),
                    ]
                )
            self.assertEqual(scored.exception.code, 0)
            result = json.loads(output.read_text(encoding="utf-8"))
            self.assertFalse(result["gates_passed"])
            self.assertEqual(result["official_score"], 0.0)
