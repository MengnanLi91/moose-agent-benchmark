"""Build a participant bundle without private evaluator paths or gold answers."""

from __future__ import annotations

import argparse
import shutil
import tarfile
import tempfile
from pathlib import Path

import yaml

from moose_benchmark.loader import load_manifest, resolve_inside


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    manifest_path = Path(args.manifest).resolve()
    repository_root = manifest_path.parent.parent
    manifest = load_manifest(manifest_path)
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as temporary:
        staging = Path(temporary) / "moose-agent-benchmark-public"
        staging.mkdir()
        for case in manifest.cases:
            if not case.enabled:
                continue
            source_case = resolve_inside(manifest_path.parent, case.public_case)
            destination = staging / Path(case.public_case).parent
            shutil.copytree(source_case.parent, destination, dirs_exist_ok=True)
        shutil.copytree(repository_root / "templates/submission", staging / "submission-template")
        shutil.copy2(
            repository_root / "templates/public-bundle/README.md",
            staging / "README.md",
        )
        public_manifest = {
            "schema_version": manifest.schema_version,
            "benchmark_id": manifest.benchmark_id,
            "benchmark_version": manifest.benchmark_version,
            "required_atomic_subcategories": manifest.required_atomic_subcategories,
            "cases": [
                {
                    "case_id": case.case_id,
                    "public_case": case.public_case,
                    "split": case.split,
                }
                for case in manifest.cases
                if case.enabled
            ],
        }
        (staging / "manifest.public.yaml").write_text(
            yaml.safe_dump(public_manifest, sort_keys=False), encoding="utf-8"
        )
        with tarfile.open(output, "w:gz") as archive:
            archive.add(staging, arcname=staging.name)


if __name__ == "__main__":
    main()
