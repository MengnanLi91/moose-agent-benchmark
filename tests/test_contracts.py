import unittest
from pathlib import Path

from pydantic import ValidationError

from moose_benchmark.contracts import ArtifactSpec, EvaluationSpec, RecordedArtifact
from moose_benchmark.loader import load_case, load_evaluation, load_submission_record

ROOT = Path(__file__).resolve().parents[1]


class ContractTests(unittest.TestCase):
    def test_example_and_templates_validate_as_v2(self):
        paths = [
            ROOT / "benchmark/public/cases/D1-SOLVER-DTMIN-001/case.yaml",
            ROOT / "templates/atomic-case/case.yaml",
            ROOT / "templates/integrated-workflow-case/case.yaml",
        ]
        for path in paths:
            with self.subTest(path=path):
                self.assertEqual(load_case(path).schema_version, "2.0")
        evaluations = [
            ROOT / "templates/atomic-case/private-evaluation.yaml",
            ROOT / "templates/integrated-workflow-case/private-evaluation.yaml",
        ]
        for path in evaluations:
            with self.subTest(path=path):
                self.assertEqual(load_evaluation(path).schema_version, "2.0")

    def test_v1_submission_record_is_rejected(self):
        path = ROOT / "benchmark/example-submissions/D1-SOLVER-DTMIN-001/run-record.json"
        data = path.read_text(encoding="utf-8").replace(
            '"schema_version": "2.0"',
            '"schema_version": "1.0"',
            1,
        )
        import json

        from moose_benchmark.contracts import SubmissionRecord

        with self.assertRaises(ValidationError):
            SubmissionRecord.model_validate(json.loads(data))

    def test_artifact_path_traversal_is_rejected(self):
        with self.assertRaises(ValidationError):
            ArtifactSpec(id="bad", path="../secret", role="input")

    def test_absolute_artifact_path_is_rejected(self):
        with self.assertRaises(ValidationError):
            ArtifactSpec(id="bad", path="/tmp/secret", role="input")

    def test_recorded_artifact_requires_hash_and_size(self):
        with self.assertRaises(ValidationError):
            RecordedArtifact(
                role="result",
                path="result.csv",
                sha256="not-a-hash",
                size_bytes=1,
            )

    def test_fixture_run_record_loads(self):
        record = load_submission_record(
            ROOT / "benchmark/example-submissions/F1-SOLID-DUCT-BOWING-001/run-record.json"
        )
        self.assertEqual(record.schema_version, "2.0")
        self.assertEqual(record.model.provider, "fixture")

    def test_evaluation_rejects_duplicate_gate_ids(self):
        data = {
            "schema_version": "2.0",
            "case_id": "CASE",
            "evaluator": "structured_claim_v2",
            "capability_criteria": [
                {
                    "id": "capability",
                    "description": "capability",
                    "json_pointer": "/claim/value",
                    "comparator": "exact",
                    "expected": True,
                    "weight": 1.0,
                }
            ],
            "evidence_criteria": [
                {
                    "id": "evidence",
                    "description": "evidence",
                    "json_pointer": "/evidence/0/source_id",
                    "comparator": "exact",
                    "expected": "source",
                    "weight": 1.0,
                }
            ],
            "hard_gates": [
                {"id": "duplicate", "description": "one", "kind": "external"},
                {"id": "duplicate", "description": "two", "kind": "external"},
            ],
        }
        with self.assertRaises(ValidationError):
            EvaluationSpec.model_validate(data)

    def test_semantic_evaluation_requires_reference_solution(self):
        with self.assertRaises(ValidationError):
            EvaluationSpec.model_validate(
                {
                    "schema_version": "2.0",
                    "case_id": "CASE",
                    "evaluator": "semantic_rubric_v1",
                    "capability_criteria": [
                        {"id": "criterion", "weight": 1.0, "full_credit": "Correct"}
                    ],
                }
            )


if __name__ == "__main__":
    unittest.main()
