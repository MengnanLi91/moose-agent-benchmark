import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

from moose_benchmark.cli import main, validate_manifest
from moose_benchmark.loader import case_bundle_paths, load_submission_record
from moose_benchmark.moose_gates.base import prepare_workspace
from moose_benchmark.moose_gates.config import MooseGateConfig
from moose_benchmark.moose_gates.hit import HitTool, parse_hit_diff_paths, parse_hit_find
from moose_benchmark.runner import RunLimits, run_command

ROOT = Path(__file__).resolve().parents[1]


class MooseGateTests(unittest.TestCase):
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
