import json
import unittest
from pathlib import Path

from moose_benchmark.cli import validate_manifest
from moose_benchmark.contracts import EvaluationContext, ExternalGateResult
from moose_benchmark.evaluators import get_evaluator
from moose_benchmark.loader import (
    case_bundle_paths,
    load_case,
    load_evaluation,
    load_manifest,
    load_submission,
    sha256_model,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "benchmark/manifest.yaml"


def external_gates(filename="external-gates.json"):
    path = ROOT / f"benchmark/private/cases/DIAG-THERMAL-SCHEMA-001/{filename}"
    return [ExternalGateResult.model_validate(item) for item in json.loads(path.read_text())]


def evaluation_context(submission):
    manifest = load_manifest(MANIFEST)
    return EvaluationContext(
        benchmark_id=manifest.benchmark_id,
        benchmark_version=manifest.benchmark_version,
        submission_sha256=sha256_model(submission),
        artifact_root=ROOT / "benchmark/example-submissions",
    )


class ExampleCaseTests(unittest.TestCase):
    def test_manifest_is_valid(self):
        self.assertEqual(validate_manifest(MANIFEST), [])

    def test_gold_submission_passes(self):
        case_path, evaluation_path = case_bundle_paths(MANIFEST, "DIAG-THERMAL-SCHEMA-001")
        case = load_case(case_path)
        evaluation = load_evaluation(evaluation_path)
        submission = load_submission(
            ROOT / "benchmark/example-submissions/DIAG-THERMAL-SCHEMA-001.json"
        )
        result = get_evaluator(evaluation.evaluator).evaluate(
            case,
            evaluation,
            submission,
            external_gates(),
            evaluation_context(submission),
        )
        self.assertEqual(result.official_score, 100.0)
        self.assertTrue(result.case_passed)

    def test_designated_mutant_fails(self):
        case_path, evaluation_path = case_bundle_paths(MANIFEST, "DIAG-THERMAL-SCHEMA-001")
        case = load_case(case_path)
        evaluation = load_evaluation(evaluation_path)
        submission = load_submission(
            ROOT / "benchmark/example-submissions/DIAG-THERMAL-SCHEMA-001-mutant.json"
        )
        result = get_evaluator(evaluation.evaluator).evaluate(
            case,
            evaluation,
            submission,
            external_gates("external-gates-mutant.json"),
            evaluation_context(submission),
        )
        self.assertFalse(result.case_passed)
        self.assertLess(result.official_score, 80.0)

    def test_missing_external_gate_result_zeroes_official_score(self):
        case_path, evaluation_path = case_bundle_paths(MANIFEST, "DIAG-THERMAL-SCHEMA-001")
        case = load_case(case_path)
        evaluation = load_evaluation(evaluation_path)
        submission = load_submission(
            ROOT / "benchmark/example-submissions/DIAG-THERMAL-SCHEMA-001.json"
        )
        result = get_evaluator(evaluation.evaluator).evaluate(
            case,
            evaluation,
            submission,
            [],
            evaluation_context(submission),
        )
        self.assertEqual(result.raw_score, 100.0)
        self.assertEqual(result.official_score, 0.0)
        self.assertFalse(result.case_passed)

    def test_submission_identity_mismatch_is_rejected(self):
        case_path, evaluation_path = case_bundle_paths(MANIFEST, "DIAG-THERMAL-SCHEMA-001")
        case = load_case(case_path)
        evaluation = load_evaluation(evaluation_path)
        submission = load_submission(
            ROOT / "benchmark/example-submissions/DIAG-THERMAL-SCHEMA-001.json"
        )
        data = submission.model_dump(mode="json")
        data["case_id"] = "OTHER-CASE"
        mismatched = type(submission).model_validate(data)
        with self.assertRaisesRegex(ValueError, "identity"):
            get_evaluator(evaluation.evaluator).evaluate(
                case,
                evaluation,
                mismatched,
                external_gates(),
                evaluation_context(mismatched),
            )


if __name__ == "__main__":
    unittest.main()
