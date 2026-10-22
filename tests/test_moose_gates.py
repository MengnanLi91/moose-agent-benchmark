import json
import shutil
import sys
import tempfile
import unittest
from math import nan
from pathlib import Path
from unittest.mock import patch

import yaml
from pydantic import ValidationError

from moose_benchmark.cli import main, validate_manifest
from moose_benchmark.contracts import EvaluationContext, MmsReferenceData, MmsResponse
from moose_benchmark.loader import (
    case_bundle_paths,
    discover_submission_artifact_paths,
    load_case,
    load_model,
    load_submission_record,
    sha256_file,
)
from moose_benchmark.moose_gates.base import GateTools, prepare_workspace
from moose_benchmark.moose_gates.config import MmsGateConfig, MooseGateConfig
from moose_benchmark.moose_gates.hit import HitTool, parse_hit_diff_paths, parse_hit_find
from moose_benchmark.moose_gates.metrics import classify_mms_verdict, observed_orders
from moose_benchmark.moose_gates.mms import (
    MmsLevelResult,
    MmsStudyResult,
    _extract_level,
    _input_policy_violations,
    _public_scaffold,
    _response_matches_measurement,
    _sequence_matches,
    generate_mms_gates,
    reference_data_matches,
)
from moose_benchmark.runner import RunLimits, RunResult, run_command

ROOT = Path(__file__).resolve().parents[1]


def successful_run(*, exit_code=0):
    return RunResult(
        argv=["/fake/combined-opt"],
        exit_code=exit_code,
        timed_out=False,
        wall_time_seconds=0.1,
        stdout="",
        stderr="",
        memory_limit_enforced=True,
        output_limit_exceeded=False,
        process_limit_exceeded=False,
        process_limit_enforced=True,
    )


def study_from_reference(reference, *, exit_code=0):
    run = successful_run(exit_code=exit_code)
    return MmsStudyResult(
        check=run,
        levels=[
            MmsLevelResult(
                level=item.level,
                parameter=item.parameter,
                controls=item.controls,
                errors=item.errors,
                secondary_metrics={},
                run=run,
                csv_bytes=b"",
            )
            for item in reference.runs
        ],
        orders=reference.observed_orders,
        oracle_valid=True,
        oracle_evidence=[],
    )


class MooseGateTests(unittest.TestCase):
    def test_mms_order_calculation_and_verdict_classification(self):
        orders = observed_orders(
            [0.125, 0.0625, 0.03125, 0.015625],
            [0.25, 0.0625, 0.015625, 0.00390625],
        )
        self.assertEqual(orders, [2.0, 2.0, 2.0])
        assessment, verdict = classify_mms_verdict({"u": orders}, {"u": 2.0})
        self.assertEqual(assessment, {"u": True})
        self.assertEqual(verdict, "verified")
        assessment, verdict = classify_mms_verdict({"u": [2.0, 1.7, 1.6]}, {"u": 2.0})
        self.assertEqual(assessment, {"u": False})
        self.assertEqual(verdict, "not_verified")
        self.assertEqual(
            classify_mms_verdict({"u": [2.0, nan]}, {"u": 2.0}),
            ({}, "inconclusive"),
        )

    def test_mms_gate_config_requires_all_seven_standard_gates(self):
        path = ROOT / "benchmark/private/cases/" "V1-POROUS-DARCY-MMS-001/gate-config.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        config = MmsGateConfig.model_validate(data)
        self.assertEqual(len(config.required_gates), 7)
        data["required_gates"].pop()
        with self.assertRaises(ValidationError):
            MmsGateConfig.model_validate(data)

    def test_mms_gate_generation_emits_seven_gates_and_rejects_bad_claims(self):
        case_id = "V1-POROUS-DARCY-MMS-001"
        public_root = ROOT / f"benchmark/public/cases/{case_id}"
        private_source = ROOT / f"benchmark/private/cases/{case_id}"
        case = load_case(public_root / "case.yaml")
        config = MmsGateConfig.model_validate(
            yaml.safe_load((private_source / "gate-config.yaml").read_text())
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            private_root = root / "private"
            shutil.copytree(private_source, private_root)
            executable = root / "combined-opt"
            executable.write_text("fixture", encoding="utf-8")
            executable.chmod(0o755)
            reference_path = private_root / "reference/metrics.json"
            reference_data = json.loads(reference_path.read_text(encoding="utf-8"))
            reference_data["executable_sha256"] = sha256_file(executable)
            reference_path.write_text(json.dumps(reference_data), encoding="utf-8")
            reference = load_model(reference_path, MmsReferenceData)
            tools = GateTools(moose_dir=root, executable=executable, hit=root / "hit")

            def generate(
                submission_name,
                study,
                *,
                instrumentation_ok=True,
                physics_ok=True,
            ):
                submission_root = ROOT / f"benchmark/example-submissions/{submission_name}"
                record_path = submission_root / "run-record.json"
                submission = load_submission_record(record_path)
                context = EvaluationContext(
                    benchmark_id="moose-agent-benchmark-development",
                    benchmark_version="0.5.0",
                    submission_sha256=submission.submission_sha256,
                    run_record_sha256=sha256_file(record_path),
                    submission_root=submission_root,
                    public_case_root=public_root,
                    private_case_root=private_root,
                )
                with (
                    patch(
                        "moose_benchmark.moose_gates.mms._protected_instrumentation_matches",
                        return_value=(instrumentation_ok, ["protected"]),
                    ),
                    patch(
                        "moose_benchmark.moose_gates.mms._physics_conforms",
                        return_value=(physics_ok, ["physics"]),
                    ),
                    patch(
                        "moose_benchmark.moose_gates.mms.run_mms_study",
                        return_value=study,
                    ),
                ):
                    return generate_mms_gates(case, config, tools, context, submission)

            gold = generate(case_id, study_from_reference(reference))
            self.assertEqual([gate.gate_id for gate in gold], config.required_gates)
            self.assertTrue(all(gate.passed for gate in gold))
            self.assertIsNotNone(
                next(
                    gate for gate in gold if gate.gate_id == "reported_values_match"
                ).mms_measurement
            )
            measurement = next(
                gate for gate in gold if gate.gate_id == "reported_values_match"
            ).mms_measurement
            response = MmsResponse.model_validate(
                json.loads(
                    (ROOT / f"benchmark/example-submissions/{case_id}/response.json").read_text(
                        encoding="utf-8"
                    )
                )
            )
            response.claim.verdict = "not_verified"
            self.assertFalse(_response_matches_measurement(response, measurement, reference))

            mutant = generate(
                f"{case_id}-mutant-001",
                study_from_reference(reference),
            )
            by_id = {gate.gate_id: gate for gate in mutant}
            self.assertFalse(by_id["reported_values_match"].passed)
            self.assertTrue(by_id["protected_error_oracle"].passed)

            failed = generate(case_id, study_from_reference(reference, exit_code=1))
            by_id = {gate.gate_id: gate for gate in failed}
            self.assertFalse(by_id["successful_moose_runs"].passed)
            self.assertFalse(by_id["protected_error_oracle"].passed)

            altered = generate(
                case_id,
                study_from_reference(reference),
                instrumentation_ok=False,
            )
            self.assertFalse(
                next(gate for gate in altered if gate.gate_id == "protected_error_oracle").passed
            )

            missing_physics = generate(
                case_id,
                study_from_reference(reference),
                physics_ok=False,
            )
            self.assertFalse(
                next(
                    gate for gate in missing_physics if gate.gate_id == "physics_conformance"
                ).passed
            )

            nonconvergent_study = study_from_reference(reference)
            nonconvergent_study.orders = {"p": [2.0, 1.5, 1.4]}
            nonconvergent = generate(case_id, nonconvergent_study)
            self.assertFalse(
                next(
                    gate for gate in nonconvergent if gate.gate_id == "required_convergence"
                ).passed
            )

            resource_run = successful_run()
            resource_run = RunResult(
                **{
                    **resource_run.to_dict(),
                    "process_limit_exceeded": True,
                }
            )
            resource_study = study_from_reference(reference)
            resource_study.check = resource_run
            resource_violation = generate(case_id, resource_study)
            self.assertFalse(
                next(
                    gate for gate in resource_violation if gate.gate_id == "resource_compliance"
                ).passed
            )

    def test_mms_sequence_rejects_incorrect_controls(self):
        case_id = "V1-POROUS-DARCY-MMS-001"
        case = load_case(ROOT / f"benchmark/public/cases/{case_id}/case.yaml")
        path = ROOT / f"benchmark/example-submissions/{case_id}/response.json"
        response = json.loads(path.read_text(encoding="utf-8"))
        response["claim"]["runs"][0]["controls"]["n"] = 7
        self.assertFalse(_sequence_matches(case, MmsResponse.model_validate(response)))

    def test_mms_public_scaffold_hash_is_rechecked(self):
        case_id = "V1-POROUS-DARCY-MMS-001"
        source = ROOT / f"benchmark/public/cases/{case_id}"
        case = load_case(source / "case.yaml")
        with tempfile.TemporaryDirectory() as directory:
            public_root = Path(directory) / "public"
            shutil.copytree(source, public_root)
            input_path = public_root / "artifacts/input-scaffold.i"
            input_path.write_text(
                input_path.read_text(encoding="utf-8") + "\n# altered\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "does not match"):
                _public_scaffold(case, public_root, "artifacts/input-scaffold.i")

    def test_mms_input_policy_rejects_includes_and_reserved_name_collisions(self):
        case_id = "V1-POROUS-DARCY-MMS-001"
        canonical = (
            ROOT / f"benchmark/example-submissions/{case_id}/artifacts/solution.i"
        ).read_text(encoding="utf-8")
        patterns = [
            "Functions/exact/type",
            "Functions/exact/expression",
            "Postprocessors/p_l2/**",
            "Outputs/csv",
            "Outputs/file_base",
        ]
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "solution.i"
            candidate.write_text(canonical, encoding="utf-8")
            self.assertEqual(_input_policy_violations(candidate, patterns), [])

            candidate.write_text(f"!include ../private/oracle.i\n{canonical}", encoding="utf-8")
            self.assertIn("unsafe_include:true", _input_policy_violations(candidate, patterns))

            candidate.write_text(
                canonical
                + "\n[Functions]\n  [exact]\n"
                + "    type = ParsedFunction\n"
                + "    expression = '0'\n"
                + "  []\n[]\n",
                encoding="utf-8",
            )
            self.assertIn(
                "reserved_name:Functions/exact,count=2",
                _input_policy_violations(candidate, patterns),
            )

    def test_mms_reference_comparison_detects_frozen_metric_drift(self):
        reference = load_model(
            ROOT / "benchmark/private/cases/V1-POROUS-DARCY-MMS-001/reference/metrics.json",
            MmsReferenceData,
        )
        current = reference.model_copy(deep=True)
        self.assertTrue(reference_data_matches(current, reference))
        current.runs[0].errors["p"] *= 2
        self.assertFalse(reference_data_matches(current, reference))

    def test_generate_mms_reference_preserves_frozen_metrics_on_drift(self):
        case_id = "V1-POROUS-DARCY-MMS-001"
        reference = load_model(
            ROOT / f"benchmark/private/cases/{case_id}/reference/metrics.json",
            MmsReferenceData,
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            executable = root / "combined-opt"
            executable.write_text("fixture", encoding="utf-8")
            executable.chmod(0o755)
            tools = GateTools(moose_dir=root, executable=executable, hit=root / "hit")
            frozen = reference.model_copy(deep=True)
            frozen.executable_sha256 = sha256_file(executable)
            frozen.runs[0].errors["p"] *= 2
            output = root / "metrics.json"
            output.write_text(
                frozen.model_dump_json(indent=2) + "\n",
                encoding="utf-8",
            )
            original = output.read_bytes()

            with (
                patch("moose_benchmark.cli.verify_tools", return_value=tools),
                patch(
                    "moose_benchmark.cli.run_mms_study",
                    return_value=study_from_reference(reference),
                ),
                patch("moose_benchmark.cli.write_validation_artifacts") as write_validation,
                self.assertRaises(SystemExit) as raised,
            ):
                main(
                    [
                        "generate-mms-reference",
                        "--manifest",
                        str(ROOT / "benchmark/manifest.yaml"),
                        "--case-id",
                        case_id,
                        "--moose-dir",
                        str(root),
                        "--executable",
                        str(executable),
                        "--output",
                        str(output),
                        "--validation-dir",
                        str(root / "validation"),
                    ]
                )

            self.assertEqual(raised.exception.code, 2)
            self.assertEqual(output.read_bytes(), original)
            write_validation.assert_not_called()

    def test_mms_private_input_mutants_preserve_intended_faults(self):
        navier_stokes = "V1-FLUID-NAVIER-STOKES-MMS-001"
        mutant = (
            ROOT / f"benchmark/private/cases/{navier_stokes}/mutants/numeric-function-bc.i"
        ).read_text(encoding="utf-8")
        self.assertIn("type = DirichletBC", mutant)
        self.assertIn("value = exact_u", mutant)

        implementation_mutants = {
            "V1-DIFFUSION-TRANSIENT-NEUMANN-MMS-001": (
                "missing-diffusion.i",
                "type = Diffusion",
                False,
            ),
            "V1-THERMAL-MMS-001": (
                "wrong-source-sign.i",
                "expression = '(1-2*pi^2)",
                True,
            ),
            "V1-POROUS-DARCY-MMS-001": (
                "wrong-boundary-data.i",
                "function = wrong_boundary",
                True,
            ),
            "V1-PHASEFIELD-ALLEN-CAHN-MMS-001": (
                "quadratic-discretization.i",
                "order = SECOND",
                True,
            ),
        }
        for case_id, (filename, marker, should_contain) in implementation_mutants.items():
            with self.subTest(case_id=case_id):
                text = (ROOT / f"benchmark/private/cases/{case_id}/mutants/{filename}").read_text(
                    encoding="utf-8"
                )
                self.assertEqual(marker in text, should_contain)

    def test_mms_csv_rejects_missing_zero_and_nonfinite_errors(self):
        case_id = "V1-POROUS-DARCY-MMS-001"
        case = load_case(ROOT / f"benchmark/public/cases/{case_id}/case.yaml")
        config_path = ROOT / f"benchmark/private/cases/{case_id}/gate-config.yaml"
        config = MmsGateConfig.model_validate(
            yaml.safe_load(config_path.read_text(encoding="utf-8"))
        )
        run = successful_run()
        with tempfile.TemporaryDirectory() as directory:
            csv_path = Path(directory) / "mms.csv"
            for content in ("time\n1\n", "time,u_l2\n1,0\n", "time,u_l2\n1,nan\n"):
                with self.subTest(content=content):
                    csv_path.write_text(content, encoding="utf-8")
                    _result, valid, _evidence = _extract_level(
                        config,
                        case.verification_study.levels[0],
                        run,
                        csv_path,
                    )
                    self.assertFalse(valid)

    def test_disabled_case_requires_explicit_opt_in(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            public = root / "public/cases/D1"
            private = root / "private/cases/D1"
            public.mkdir(parents=True)
            private.mkdir(parents=True)
            source_public = ROOT / "benchmark/public/cases/D1-SOLVER-DTMIN-001"
            source_private = ROOT / "benchmark/private/cases/D1-SOLVER-DTMIN-001"
            for source in source_public.iterdir():
                if source.is_file():
                    (public / source.name).write_bytes(source.read_bytes())
                else:
                    shutil.copytree(source, public / source.name)
            (private / "evaluation.yaml").write_bytes(
                (source_private / "evaluation.yaml").read_bytes()
            )
            manifest = {
                "schema_version": "2.0",
                "benchmark_id": "fixture",
                "benchmark_version": "1.0.0",
                "required_atomic_subcategories": ["D1"],
                "cases": [
                    {
                        "case_id": "D1-SOLVER-DTMIN-001",
                        "public_case": "public/cases/D1/case.yaml",
                        "private_evaluation": "private/cases/D1/evaluation.yaml",
                        "split": "development",
                        "enabled": False,
                    }
                ],
            }
            manifest_path = root / "manifest.yaml"
            manifest_path.write_text(yaml.safe_dump(manifest), encoding="utf-8")

            with self.assertRaises(KeyError):
                case_bundle_paths(manifest_path, "D1-SOLVER-DTMIN-001")
            paths = case_bundle_paths(
                manifest_path,
                "D1-SOLVER-DTMIN-001",
                include_disabled=True,
            )

            self.assertEqual(
                paths,
                ((public / "case.yaml").resolve(), (private / "evaluation.yaml").resolve()),
            )
            self.assertEqual(validate_manifest(manifest_path), [])
            self.assertEqual(
                validate_manifest(manifest_path, include_disabled=True),
                [],
            )

    def test_hit_diff_and_find_parsers(self):
        diff_output = """
Parameters added left -> right:

    [Mesh]
      [restricted]
        type = ParsedGenerateSideset
        input = base
      []
    []

Parameters with differing values:

    BCs/Periodic/pair/primary (/tmp/faulty.i:20) has differing values
      'right' -> 'restricted'
"""
        find_output = """
/tmp/input.i:10 Preconditioning/FSP/system/vars = velocity pressure concentration
/tmp/input.i:15 Preconditioning/FSP/fluid/vars = 'velocity pressure'
2 matches found.
"""
        self.assertEqual(
            parse_hit_diff_paths(diff_output),
            {
                "Mesh/restricted/type",
                "Mesh/restricted/input",
                "BCs/Periodic/pair/primary",
            },
        )
        self.assertEqual(
            parse_hit_find(find_output),
            {
                "Preconditioning/FSP/system/vars": "velocity pressure concentration",
                "Preconditioning/FSP/fluid/vars": "'velocity pressure'",
            },
        )

    def test_hit_accepts_difference_and_zero_match_exit_codes(self):
        with tempfile.TemporaryDirectory() as directory:
            moose_dir = Path(directory)
            executable = moose_dir / "framework/contrib/hit/hit"
            executable.parent.mkdir(parents=True)
            executable.write_text(
                f"""#!{sys.executable}
import sys
if sys.argv[1] == "diff":
    print("Parameters with differing values:")
    print("    Mesh/value (/tmp/left.i:1) has differing values")
    raise SystemExit(1)
print("0 matches found.")
raise SystemExit(1)
""",
                encoding="utf-8",
            )
            executable.chmod(0o755)
            left = moose_dir / "left.i"
            right = moose_dir / "right.i"
            left.write_text("value = 1\n", encoding="utf-8")
            right.write_text("value = 2\n", encoding="utf-8")

            hit = HitTool(moose_dir)
            self.assertEqual(hit.diff(left, right).changed_paths, {"Mesh/value"})
            self.assertEqual(hit.find("Preconditioning/**/vars", right), {})

    def test_workspace_verifies_hashes_and_overlays_one_artifact(self):
        config = MooseGateConfig.model_validate(
            {
                "schema_version": "1.0",
                "case_id": "F4-POROUS-SOLUTE-001",
                "case_type": "r1_periodic_sideset",
                "fixture_dir": "fixture",
                "overlay_path": "candidate.i",
                "input_path": "candidate.i",
                "expected_moose_revision": "a" * 40,
                "authorized_hit_paths": ["Mesh/**"],
                "required_gates": ["authorized_edit_scope"],
                "commands": {},
                "limits": {
                    "wall_time_seconds": 10,
                    "cpu_seconds": 5,
                    "memory_mib": 256,
                },
            }
        )
        source = ROOT / "benchmark/example-submissions/F4-POROUS-SOLUTE-001"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            submission_root = root / "submission"
            private_root = root / "private"
            shutil.copytree(source, submission_root)
            fixture = private_root / "fixture"
            fixture.mkdir(parents=True)
            (fixture / "candidate.i").write_text("faulty\n", encoding="utf-8")
            submission = load_submission_record(submission_root / "run-record.json")

            with prepare_workspace(
                private_root,
                submission_root,
                submission,
                "artifacts/solution.i",
                config,
            ) as workspace:
                self.assertEqual(workspace.reference_artifact, b"faulty\n")
                self.assertEqual(
                    workspace.candidate_path.read_bytes(),
                    (submission_root / "artifacts/solution.i").read_bytes(),
                )

            (submission_root / "artifacts/solution.i").write_text(
                "tampered\n",
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                with prepare_workspace(
                    private_root,
                    submission_root,
                    submission,
                    "artifacts/solution.i",
                    config,
                ):
                    pass

    def test_submission_artifact_discovery_rejects_symlinks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifacts = root / "artifacts"
            artifacts.mkdir()
            target = artifacts / "target.i"
            target.write_text("input", encoding="utf-8")
            (artifacts / "solution.i").symlink_to(target)
            with self.assertRaisesRegex(ValueError, "symlink"):
                discover_submission_artifact_paths(root)

    def test_output_limit_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run_command(
                [
                    sys.executable,
                    "-c",
                    "import sys; print('x' * 4096); print('y' * 4096, file=sys.stderr)",
                ],
                cwd=Path(directory),
                limits=RunLimits(
                    wall_time_seconds=10,
                    cpu_seconds=5,
                    memory_mib=256,
                    max_output_bytes=128,
                    max_processes=4,
                ),
            )
        self.assertTrue(result.output_limit_exceeded)
        self.assertLessEqual(
            len(result.stdout.encode()) + len(result.stderr.encode()),
            128,
        )

    def test_process_limit_is_reported(self):
        script = (
            "import subprocess, sys, time; "
            "subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(5)']); "
            "time.sleep(5)"
        )
        with tempfile.TemporaryDirectory() as directory:
            result = run_command(
                [sys.executable, "-c", script],
                cwd=Path(directory),
                limits=RunLimits(
                    wall_time_seconds=10,
                    cpu_seconds=5,
                    memory_mib=256,
                    max_output_bytes=1024,
                    max_processes=1,
                ),
            )
        self.assertTrue(result.process_limit_enforced)
        self.assertTrue(result.process_limit_exceeded)

    def test_gate_infrastructure_error_produces_no_output(self):
        submission = ROOT / "benchmark/example-submissions/R1-DIFFUSION-PERIODIC-SIDESET-001"
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "gates.json"
            with self.assertRaises(SystemExit) as raised:
                main(
                    [
                        "generate-gates",
                        "--manifest",
                        str(ROOT / "benchmark/manifest.yaml"),
                        "--case-id",
                        "R1-DIFFUSION-PERIODIC-SIDESET-001",
                        "--submission-dir",
                        str(submission),
                        "--moose-dir",
                        str(Path(directory) / "missing-moose"),
                        "--executable",
                        str(Path(directory) / "missing-moose/combined-opt"),
                        "--output",
                        str(output),
                        "--include-disabled",
                    ]
                )
            self.assertEqual(raised.exception.code, 2)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
