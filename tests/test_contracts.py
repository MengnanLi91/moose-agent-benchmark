import json
import unittest
from pathlib import Path

from pydantic import ValidationError

from moose_benchmark.contracts import (
    ArtifactSpec,
    CaseContract,
    EvaluationSpec,
    MmsResponse,
    RecordedArtifact,
)
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

    def test_repair_contract_rejects_source_submission(self):
        case = load_case(ROOT / "benchmark/public/cases/R2-COUPLED-VARIABLE-WIRING-001/case.yaml")
        data = case.model_dump(mode="json")
        data["submission"]["required_artifacts"][0]["path"] = "artifacts/solution.C"
        data["submission"]["required_artifacts"][0]["role"] = "repaired_cpp_source"
        with self.assertRaises(ValidationError):
            CaseContract.model_validate(data)

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

    def test_v1_case_requires_an_ordered_declared_refinement_study(self):
        path = ROOT / "benchmark/public/cases/V1-POROUS-DARCY-MMS-001/case.yaml"
        data = load_case(path).model_dump(mode="json")
        invalid_cases = []

        missing_study = dict(data)
        missing_study["verification_study"] = None
        invalid_cases.append(missing_study)

        duplicate_level = json.loads(json.dumps(data))
        duplicate_level["verification_study"]["levels"][2]["level"] = 1
        invalid_cases.append(duplicate_level)

        unordered_parameters = json.loads(json.dumps(data))
        unordered_parameters["verification_study"]["levels"][2]["parameter"] = 0.125
        invalid_cases.append(unordered_parameters)

        undeclared_override = json.loads(json.dumps(data))
        undeclared_override["verification_study"]["levels"][0]["overrides"].append(
            "Executioner/dt=0.1"
        )
        invalid_cases.append(undeclared_override)

        for invalid in invalid_cases:
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValidationError):
                    CaseContract.model_validate(invalid)

    def test_mms_response_rejects_invalid_error_and_order_sequences(self):
        path = ROOT / "benchmark/example-submissions/" "V1-POROUS-DARCY-MMS-001/response.json"
        response = json.loads(path.read_text(encoding="utf-8"))
        invalid_responses = []

        zero_error = json.loads(json.dumps(response))
        zero_error["claim"]["runs"][0]["errors"]["p"] = 0
        invalid_responses.append(zero_error)

        nonfinite_error = json.loads(json.dumps(response))
        nonfinite_error["claim"]["runs"][0]["errors"]["p"] = float("nan")
        invalid_responses.append(nonfinite_error)

        missing_level = json.loads(json.dumps(response))
        missing_level["claim"]["runs"].pop()
        invalid_responses.append(missing_level)

        duplicate_level = json.loads(json.dumps(response))
        duplicate_level["claim"]["runs"][2]["level"] = 1
        invalid_responses.append(duplicate_level)

        unordered_parameters = json.loads(json.dumps(response))
        unordered_parameters["claim"]["runs"][2]["parameter"] = 0.125
        invalid_responses.append(unordered_parameters)

        for invalid in invalid_responses:
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValidationError):
                    MmsResponse.model_validate(invalid)

    def test_v1_derivation_and_implementation_submission_shapes_are_distinct(self):
        derivation = load_case(
            ROOT / "benchmark/public/cases/" "V1-DIFFUSION-STEADY-DIRICHLET-MMS-001/case.yaml"
        )
        implementation = load_case(
            ROOT / "benchmark/public/cases/V1-POROUS-DARCY-MMS-001/case.yaml"
        )

        self.assertEqual(derivation.mms_task.value, "derivation")
        self.assertEqual(derivation.submission.response_mode.value, "free_text")
        self.assertIsNotNone(derivation.mms_derivation)
        self.assertIsNone(derivation.verification_study)

        self.assertEqual(implementation.mms_task.value, "implementation")
        self.assertEqual(implementation.submission.response_mode.value, "structured_json")
        self.assertEqual(
            implementation.submission.required_artifacts[0].role,
            "mms_moose_input",
        )
        self.assertIsNotNone(implementation.verification_study)

    def test_v1_derivation_requires_all_declared_problem_and_output_groups(self):
        path = ROOT / "benchmark/public/cases/" "V1-DIFFUSION-STEADY-DIRICHLET-MMS-001/case.yaml"
        data = load_case(path).model_dump(mode="json")
        for key in ("supplied", "required_outputs"):
            invalid = json.loads(json.dumps(data))
            invalid["mms_derivation"][key].pop()
            with self.subTest(key=key), self.assertRaises(ValidationError):
                CaseContract.model_validate(invalid)


if __name__ == "__main__":
    unittest.main()
