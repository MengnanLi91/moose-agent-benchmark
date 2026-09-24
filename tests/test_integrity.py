import json
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from moose_benchmark.contracts import (
    EvaluationContext,
    ExternalGateResult,
    ModelIdentity,
    RecordedArtifact,
    RecordedResponse,
    SubmissionRecord,
    UsageRecord,
)
from moose_benchmark.evaluators import get_evaluator
from moose_benchmark.loader import (
    load_case,
    load_evaluation,
    sha256_file,
)

ROOT = Path(__file__).resolve().parents[1]


class IntegrityTests(unittest.TestCase):
    def test_nonexistent_recorded_artifacts_fail_closed(self):
        case = load_case(ROOT / "templates/integrated-workflow-case/case.yaml")
        evaluation = load_evaluation(
            ROOT / "templates/integrated-workflow-case/private-evaluation.yaml"
        )
        with tempfile.TemporaryDirectory() as directory:
            submission_root = Path(directory)
            response_path = submission_root / "response.json"
            response_path.write_text(
                json.dumps(
                    {
                        "claim": {"stages": {stage: "passed" for stage in case.required_stages}},
                        "evidence": [
                            {
                                "source_id": "verification_data",
                                "observation": "claimed",
                                "interpretation": "claimed",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            response = RecordedResponse(
                path="response.json",
                media_type="application/json",
                sha256=sha256_file(response_path),
                size_bytes=response_path.stat().st_size,
            )
            artifacts = [
                RecordedArtifact(
                    role="final_input",
                    path="artifacts/final.i",
                    sha256="0" * 64,
                    size_bytes=1,
                ),
                RecordedArtifact(
                    role="verification_data",
                    path="artifacts/verification.csv",
                    sha256="1" * 64,
                    size_bytes=1,
                ),
            ]
            submission = SubmissionRecord(
                schema_version="2.0",
                case_id=case.case_id,
                model=ModelIdentity(provider="fixture", model="fixture"),
                started_at=datetime(2026, 9, 24, tzinfo=UTC),
                finished_at=datetime(2026, 9, 24, tzinfo=UTC),
                response=response,
                artifacts=artifacts,
                usage=UsageRecord(
                    wall_time_seconds=1,
                    cpu_seconds=1,
                    memory_mib=1,
                    validation_attempts=0,
                    execution_attempts=0,
                ),
                submission_sha256="0" * 64,
            )
            result = self._evaluate(case, evaluation, submission, submission_root)
        self.assertFalse(result.gates_passed)
        self.assertEqual(result.official_score, 0.0)

    def _evaluate(self, case, evaluation, submission, submission_root):
        gates = [
            ExternalGateResult(
                schema_version="2.0",
                benchmark_id="benchmark",
                benchmark_version="2.0",
                case_id=case.case_id,
                submission_sha256=submission.submission_sha256,
                gate_id=gate.id,
                passed=True,
                detail="private evaluator passed",
            )
            for gate in evaluation.hard_gates
        ]
        context = EvaluationContext(
            benchmark_id="benchmark",
            benchmark_version="2.0",
            submission_sha256=submission.submission_sha256,
            run_record_sha256="2" * 64,
            submission_root=submission_root,
            public_case_root=ROOT / "templates/integrated-workflow-case",
            private_case_root=ROOT / "templates/integrated-workflow-case",
        )
        return get_evaluator(evaluation.evaluator).evaluate(
            case,
            evaluation,
            submission,
            gates,
            context,
        )


if __name__ == "__main__":
    unittest.main()
