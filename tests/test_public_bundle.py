import runpy
import shutil
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[1]


class PublicBundleTests(unittest.TestCase):
    def test_public_bundle_excludes_private_evaluation_material(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "public.tar.gz"
            argv = [
                "build_public_bundle.py",
                "--manifest",
                str(ROOT / "benchmark/manifest.yaml"),
                "--output",
                str(output),
            ]
            with patch.object(sys, "argv", argv):
                runpy.run_path(
                    str(ROOT / "ci/build_public_bundle.py"),
                    run_name="__main__",
                )

            with tarfile.open(output, "r:gz") as archive:
                names = archive.getnames()
                public_manifest = archive.extractfile(
                    "moose-agent-benchmark-public/manifest.public.yaml"
                )
                self.assertIsNotNone(public_manifest)
                manifest_text = public_manifest.read().decode("utf-8")

        forbidden_fragments = (
            "/private/",
            "/example-submissions/",
            "/evaluation.yaml",
            "/reference-",
            "/reference.",
            "/controls/",
            "/control.i",
            "/periodic_mesh_control.e",
            "/h1-missing-offdiag.i",
            "/h2-poor-scaling.i",
            "/oracle.i",
            "/metrics.json",
            "/external-gates",
            "/gold",
            "/mutant",
        )
        for name in names:
            self.assertFalse(
                any(fragment in name for fragment in forbidden_fragments),
                name,
            )
        self.assertNotIn("private_evaluation", manifest_text)

    def test_enabled_mms_bundle_excludes_private_calibration_material(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            benchmark_root = root / "benchmark"
            shutil_public = benchmark_root / "public"
            shutil_public.parent.mkdir(parents=True)
            shutil.copytree(ROOT / "benchmark/public", shutil_public)
            shutil.copytree(ROOT / "templates", root / "templates")
            manifest = yaml.safe_load(
                (ROOT / "benchmark/manifest.yaml").read_text(encoding="utf-8")
            )
            for case in manifest["cases"]:
                if case["case_id"].startswith("V1-"):
                    case["enabled"] = True
            manifest_path = benchmark_root / "manifest.yaml"
            manifest_path.write_text(
                yaml.safe_dump(manifest, sort_keys=False),
                encoding="utf-8",
            )
            output = root / "public.tar.gz"
            argv = [
                "build_public_bundle.py",
                "--manifest",
                str(manifest_path),
                "--output",
                str(output),
            ]
            with patch.object(sys, "argv", argv):
                runpy.run_path(
                    str(ROOT / "ci/build_public_bundle.py"),
                    run_name="__main__",
                )

            with tarfile.open(output, "r:gz") as archive:
                names = archive.getnames()
                text = "\n".join(
                    archive.extractfile(member).read().decode("utf-8", errors="ignore")
                    for member in archive.getmembers()
                    if member.isfile()
                )

        forbidden_names = (
            "canonical.i",
            "reference-solution.md",
            "metrics.json",
            "evaluation.yaml",
            "external-gates",
            "oracle.i",
            "mutant",
            "gold",
        )
        for name in names:
            self.assertFalse(any(fragment in name for fragment in forbidden_names), name)
        for fragment in (
            "reference/metrics.json",
            "error_tolerance",
            "order_tolerance",
            "canonical_input_path",
        ):
            self.assertNotIn(fragment, text)


if __name__ == "__main__":
    unittest.main()
