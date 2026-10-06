import json
import shutil
import tempfile
import unittest
from pathlib import Path

from moose_benchmark.cli import main, validate_manifest
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

REPAIR_FIXTURES = {
    "R1-DIFFUSION-PERIODIC-SIDESET-001": 2,
    "R2-COUPLED-VARIABLE-WIRING-001": 4,
    "R3-FLUID-FIELDSPLIT-VARS-001": 3,
    "R4-PHASEFIELD-LAGRANGE-TRANSIENT-001": 3,
}


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

    def test_repair_gold_passes_and_required_mutants_are_gated(self):
        for case_id, mutant_count in REPAIR_FIXTURES.items():
            with self.subTest(case_id=case_id, variant="gold"):
                gold, _ = evaluate_case(
                    case_id,
                    case_id,
                    gate_filename="external-gates-gold.json",
                )
                self.assertEqual(gold.official_score, 100.0)
                self.assertTrue(gold.case_passed)
                self.assertTrue(all(gate.passed for gate in gold.gate_results))
            for index in range(1, mutant_count + 1):
                with self.subTest(case_id=case_id, variant=index):
                    mutant, _ = evaluate_case(
                        case_id,
                        f"{case_id}-mutant-{index:03d}",
                        gate_filename=f"external-gates-mutant-{index:03d}.json",
                    )
                    self.assertEqual(mutant.official_score, 0.0)
                    self.assertFalse(mutant.case_passed)

    def test_repair_wrong_structured_identifier_reduces_raw_score(self):
        case_id = "R1-DIFFUSION-PERIODIC-SIDESET-001"
        source = ROOT / f"benchmark/example-submissions/{case_id}"
        with tempfile.TemporaryDirectory() as directory:
            submission_root = Path(directory) / case_id
            shutil.copytree(source, submission_root)
            response_path = submission_root / "response.json"
            response = json.loads(response_path.read_text(encoding="utf-8"))
            response["claim"]["repair_class"] = "wrong_repair"
            response_path.write_text(json.dumps(response), encoding="utf-8")
            with self.assertRaises(SystemExit) as recorded:
                main(
                    [
                        "record-submission",
                        "--manifest",
                        str(MANIFEST),
                        "--case-id",
                        case_id,
                        "--submission-dir",
                        str(submission_root),
                        "--model-provider",
                        "fixture",
                        "--model",
                        "wrong-identifier",
                    ]
                )
            self.assertEqual(recorded.exception.code, 0)
            result = self._evaluate_with_passing_external_gates(case_id, submission_root)
        self.assertTrue(result.gates_passed)
        self.assertLess(result.raw_score, 100.0)

    def test_repair_external_gate_provenance_mismatch_fails_closed(self):
        case_id = "R1-DIFFUSION-PERIODIC-SIDESET-001"
        case_path, evaluation_path = case_bundle_paths(MANIFEST, case_id)
        case = load_case(case_path)
        evaluation = load_evaluation(evaluation_path)
        submission_root = ROOT / f"benchmark/example-submissions/{case_id}"
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
        gates = _external_gates(case_id, "external-gates-gold.json")
        gates[0] = gates[0].model_copy(update={"benchmark_version": "forged"})
        result = get_evaluator(evaluation.evaluator).evaluate(
            case,
            evaluation,
            submission,
            gates,
            context,
        )
        self.assertFalse(result.gates_passed)
        self.assertEqual(result.official_score, 0.0)

    def _evaluate_with_passing_external_gates(self, case_id, submission_root):
        case_path, evaluation_path = case_bundle_paths(MANIFEST, case_id)
        case = load_case(case_path)
        evaluation = load_evaluation(evaluation_path)
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
        gates = [
            ExternalGateResult(
                schema_version="2.0",
                benchmark_id=manifest.benchmark_id,
                benchmark_version=manifest.benchmark_version,
                case_id=case_id,
                submission_sha256=submission.submission_sha256,
                gate_id=gate.id,
                passed=True,
                detail="fixture gate passed",
            )
            for gate in evaluation.hard_gates
        ]
        return get_evaluator(evaluation.evaluator).evaluate(
            case,
            evaluation,
            submission,
            gates,
            context,
        )


if __name__ == "__main__":
    unittest.main()
