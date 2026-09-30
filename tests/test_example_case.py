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
    load_submission_record,
    sha256_file,
)

from .fakes import ScriptedLLMClient

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "benchmark/manifest.yaml"

DIAG_FIXTURES = [
    (
        "D1-SOLVER-DTMIN-001",
        "D1-SOLVER-DTMIN-001",
        "D1-SOLVER-DTMIN-001-mutant-001",
    ),
    (
        "D2-THERMAL-REL-TOL-001",
        "D2-THERMAL-REL-TOL-001",
        "D2-THERMAL-REL-TOL-001-mutant-001",
    ),
    (
        "D3-PERIODIC-NODESET-001",
        "D3-PERIODIC-NODESET-001",
        "D3-PERIODIC-NODESET-001-mutant-001",
    ),
    (
        "D4-COUPLED-JACOBIAN-TEST-001",
        "D4-COUPLED-JACOBIAN-TEST-001",
        "D4-COUPLED-JACOBIAN-TEST-001-mutant-001",
    ),
]


def _external_gates(case_id, filename):
    path = ROOT / f"benchmark/private/cases/{case_id}/{filename}"
    return [ExternalGateResult.model_validate(item) for item in json.loads(path.read_text())]


def evaluate_case(case_id, submission_name, *, ratings=None, gate_filename=None):
    case_path, evaluation_path = case_bundle_paths(MANIFEST, case_id)
    case = load_case(case_path)
    evaluation = load_evaluation(evaluation_path)
    submission_root = ROOT / f"benchmark/example-submissions/{submission_name}"
    record_path = submission_root / "run-record.json"
    submission = load_submission_record(record_path)
    manifest = load_manifest(MANIFEST)
    context = EvaluationContext(
        benchmark_id=manifest.benchmark_id,
        benchmark_version=manifest.benchmark_version,
        submission_sha256=submission.submission_sha256,
        run_record_sha256=sha256_file(record_path),
        submission_root=submission_root,
        public_case_root=case_path.parent,
        private_case_root=evaluation_path.parent,
    )
    gates = _external_gates(case_id, gate_filename) if gate_filename else []
    client = None
    if evaluation.evaluator == "semantic_rubric_v1":
        selected = ratings or {criterion.id: "full" for criterion in evaluation.capability_criteria}
        client = ScriptedLLMClient(selected)
    result = get_evaluator(evaluation.evaluator).evaluate(
        case,
        evaluation,
        submission,
        gates,
        context,
        llm_client=client,
    )
    return result, client


class ExampleCaseTests(unittest.TestCase):
    def test_manifest_is_valid(self):
        self.assertEqual(validate_manifest(MANIFEST), [])

    def test_structured_diag_gold_passes_and_mutant_fails_claim(self):
        for case_id, gold_name, mutant_name in DIAG_FIXTURES:
            with self.subTest(case_id=case_id):
                gold, _client = evaluate_case(case_id, gold_name)
                mutant, _client = evaluate_case(case_id, mutant_name)
                self.assertEqual(gold.official_score, 100.0)
                self.assertTrue(gold.case_passed)
                self.assertTrue(mutant.gates_passed)
                self.assertFalse(mutant.case_passed)
                self.assertLess(mutant.official_score, 80.0)

    def test_f1_gold_passes_and_missing_expansion_mutant_fails(self):
        gold, client = evaluate_case(
            "F1-SOLID-DUCT-BOWING-001",
            "F1-SOLID-DUCT-BOWING-001",
        )
        mutant, _ = evaluate_case(
            "F1-SOLID-DUCT-BOWING-001",
            "F1-SOLID-DUCT-BOWING-001-mutant-001",
            ratings={
                "solved_and_prescribed_fields": "full",
                "governing_law_and_kinematics": "full",
                "elastic_constitutive_model": "full",
                "thermal_expansion_coupling": "none",
                "boundary_conditions": "full",
                "quantities_of_interest": "full",
            },
        )
        self.assertEqual(gold.official_score, 100.0)
        self.assertIn("Untrusted participant response", client.last_user_prompt)
        self.assertFalse(mutant.case_passed)
        self.assertEqual(mutant.official_score, 75.0)

    def test_f2_sign_mutant_fails(self):
        gold, _ = evaluate_case(
            "F2-THERMAL-REFLECTOR-001",
            "F2-THERMAL-REFLECTOR-001",
        )
        mutant, _ = evaluate_case(
            "F2-THERMAL-REFLECTOR-001",
            "F2-THERMAL-REFLECTOR-001-mutant-001",
            ratings={
                "conduction_volume": "full",
                "prescribed_flux_boundary": "full",
                "convection_boundary": "none",
                "essential_and_insulated_boundaries": "full",
                "complete_residual": "full",
            },
        )
        self.assertTrue(gold.case_passed)
        self.assertEqual(mutant.official_score, 75.0)
        self.assertFalse(mutant.case_passed)

    def test_f3_coupled_time_derivative_mutant_fails(self):
        gold, _ = evaluate_case(
            "F3-PHASEFIELD-SPLITCH-001",
            "F3-PHASEFIELD-SPLITCH-001",
        )
        mutant, _ = evaluate_case(
            "F3-PHASEFIELD-SPLITCH-001",
            "F3-PHASEFIELD-SPLITCH-001-mutant-001",
            ratings={
                "variable_roles": "full",
                "coupled_time_derivative": "none",
                "mobility_gradient": "full",
                "free_energy_relation": "full",
                "materials_and_couplings": "full",
            },
        )
        self.assertTrue(gold.case_passed)
        self.assertEqual(mutant.official_score, 65.0)
        self.assertFalse(mutant.case_passed)

    def test_f4_gold_passes_and_mutant_is_gated(self):
        gold, client = evaluate_case(
            "F4-POROUS-SOLUTE-001",
            "F4-POROUS-SOLUTE-001",
            gate_filename="external-gates.json",
        )
        mutant, _ = evaluate_case(
            "F4-POROUS-SOLUTE-001",
            "F4-POROUS-SOLUTE-001-mutant-001",
            ratings={
                "variables_and_mesh": "full",
                "porous_flow_configuration": "none",
                "material_properties": "full",
                "boundary_conditions": "full",
                "execution_and_outputs": "full",
            },
            gate_filename="external-gates-mutant-001.json",
        )
        self.assertTrue(gold.case_passed)
        self.assertIn("PorousFlowDictator", client.last_user_prompt)
        self.assertFalse(mutant.gates_passed)
        self.assertEqual(mutant.official_score, 0.0)


if __name__ == "__main__":
    unittest.main()
