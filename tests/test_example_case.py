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


def external_gates(filename="external-gates.json", case_id="DIAG-THERMAL-SCHEMA-001"):
    path = ROOT / f"benchmark/private/cases/{case_id}/{filename}"
    return [ExternalGateResult.model_validate(item) for item in json.loads(path.read_text())]


def evaluation_context(submission):
    manifest = load_manifest(MANIFEST)
    return EvaluationContext(
        benchmark_id=manifest.benchmark_id,
        benchmark_version=manifest.benchmark_version,
        submission_sha256=sha256_model(submission),
        artifact_root=ROOT / "benchmark/example-submissions",
    )


def evaluate_case(case_id, submission_filename, gate_filename=None):
    case_path, evaluation_path = case_bundle_paths(MANIFEST, case_id)
    case = load_case(case_path)
    evaluation = load_evaluation(evaluation_path)
    submission = load_submission(ROOT / f"benchmark/example-submissions/{submission_filename}")
    gates = external_gates(gate_filename, case_id=case_id) if gate_filename is not None else []
    return get_evaluator(evaluation.evaluator).evaluate(
        case,
        evaluation,
        submission,
        gates,
        evaluation_context(submission),
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

    def test_f1_duct_bowing_gold_passes_and_missing_expansion_mutant_fails(self):
        gold = evaluate_case(
            "F1-SOLID-DUCT-BOWING-001",
            "F1-SOLID-DUCT-BOWING-001.json",
        )
        mutant = evaluate_case(
            "F1-SOLID-DUCT-BOWING-001",
            "F1-SOLID-DUCT-BOWING-001-mutant-001.json",
        )
        self.assertEqual(gold.official_score, 100.0)
        self.assertTrue(gold.case_passed)
        self.assertFalse(mutant.case_passed)
        self.assertLess(mutant.component_scores.capability, 80.0)
        self.assertLess(mutant.official_score, 80.0)

    def test_f2_reflector_gold_passes_and_sign_mutant_fails(self):
        gold = evaluate_case(
            "F2-THERMAL-REFLECTOR-001",
            "F2-THERMAL-REFLECTOR-001.json",
        )
        mutant = evaluate_case(
            "F2-THERMAL-REFLECTOR-001",
            "F2-THERMAL-REFLECTOR-001-mutant-001.json",
        )
        self.assertEqual(gold.official_score, 100.0)
        self.assertTrue(gold.case_passed)
        self.assertTrue(mutant.gates_passed)
        self.assertFalse(mutant.case_passed)
        self.assertLess(mutant.official_score, 80.0)

    def test_f3_split_ch_gold_passes_and_time_derivative_mutant_fails(self):
        gold = evaluate_case(
            "F3-PHASEFIELD-SPLITCH-001",
            "F3-PHASEFIELD-SPLITCH-001.json",
        )
        mutant = evaluate_case(
            "F3-PHASEFIELD-SPLITCH-001",
            "F3-PHASEFIELD-SPLITCH-001-mutant-001.json",
        )
        self.assertEqual(gold.official_score, 100.0)
        self.assertTrue(gold.case_passed)
        self.assertTrue(mutant.gates_passed)
        self.assertFalse(mutant.case_passed)
        self.assertLess(mutant.component_scores.capability, 80.0)
        self.assertLess(mutant.official_score, 80.0)

    def test_f4_porous_solute_gold_passes_and_wiring_mutant_is_gated(self):
        gold = evaluate_case(
            "F4-POROUS-SOLUTE-001",
            "F4-POROUS-SOLUTE-001.json",
            "external-gates.json",
        )
        mutant = evaluate_case(
            "F4-POROUS-SOLUTE-001",
            "F4-POROUS-SOLUTE-001-mutant-001.json",
            "external-gates-mutant-001.json",
        )
        self.assertEqual(gold.official_score, 100.0)
        self.assertTrue(gold.case_passed)
        self.assertFalse(mutant.gates_passed)
        self.assertFalse(mutant.case_passed)
        self.assertEqual(mutant.official_score, 0.0)
        gate_results = {gate.id: gate.passed for gate in mutant.gate_results}
        self.assertTrue(gate_results["input_validation"])
        self.assertFalse(gate_results["semantic_preservation"])


if __name__ == "__main__":
    unittest.main()
