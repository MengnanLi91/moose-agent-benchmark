import runpy
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

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
        )
        for name in names:
            self.assertFalse(
                any(fragment in name for fragment in forbidden_fragments),
                name,
            )
        self.assertNotIn("private_evaluation", manifest_text)


if __name__ == "__main__":
    unittest.main()
