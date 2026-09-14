import unittest
from pathlib import Path

from pydantic import ValidationError

from moose_benchmark.contracts import (
    ArtifactSpec,
    EvaluationSpec,
    SubmittedArtifact,
)
from moose_benchmark.loader import load_case

ROOT = Path(__file__).resolve().parents[1]


class ContractTests(unittest.TestCase):
    def test_example_and_templates_validate(self):
        paths = [
            ROOT / "benchmark/public/cases/DIAG-THERMAL-SCHEMA-001/case.yaml",
            ROOT / "templates/atomic-case/case.yaml",
            ROOT / "templates/integrated-workflow-case/case.yaml",
        ]
        for path in paths:
            with self.subTest(path=path):
                self.assertEqual(load_case(path).schema_version, "1.0")

    def test_artifact_path_traversal_is_rejected(self):
        with self.assertRaises(ValidationError):
            ArtifactSpec(id="bad", path="../secret", role="input")

    def test_absolute_artifact_path_is_rejected(self):
        with self.assertRaises(ValidationError):
            ArtifactSpec(id="bad", path="/tmp/secret", role="input")

    def test_submitted_artifact_requires_a_sha256(self):
        with self.assertRaises(ValidationError):
            SubmittedArtifact(role="result", path="result.csv", sha256="not-a-hash")

    def test_evaluation_rejects_duplicate_gate_ids(self):
        data = {
            "schema_version": "1.0",
            "case_id": "CASE",
            "evaluator": "structured_claim_v1",
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


if __name__ == "__main__":
    unittest.main()
