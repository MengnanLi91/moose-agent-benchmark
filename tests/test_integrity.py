import tempfile
import unittest
from pathlib import Path

from moose_benchmark.contracts import (
    EvaluationContext,
    ExternalGateResult,
    SubmissionEnvelope,
)
from moose_benchmark.evaluators import get_evaluator
from moose_benchmark.loader import load_case, load_evaluation, sha256_model

ROOT = Path(__file__).resolve().parents[1]


class IntegrityTests(unittest.TestCase):
    def test_nonexistent_submitted_artifacts_fail_closed(self):
        case = load_case(ROOT / "templates/integrated-workflow-case/case.yaml")
        evaluation = load_evaluation(
            ROOT / "templates/integrated-workflow-case/private-evaluation.yaml"
        )
        submission = SubmissionEnvelope.model_validate(
            {
                "schema_version": "1.0",
                "case_id": case.case_id,
                "track": None,
                "subcategory": None,
                "claim": {"stages": {stage: "passed" for stage in case.required_stages}},
                "evidence": [
                    {
                        "source_id": "verification_data",
                        "observation": "claimed",
                        "interpretation": "claimed",
                        "artifact_sha256": None,
                    }
                ],
                "artifacts": [
                    {
                        "role": "final_input",
                        "path": "missing.i",
                        "sha256": "0" * 64,
                    },
                    {
                        "role": "verification_data",
                        "path": "missing.csv",
                        "sha256": "1" * 64,
                    },
                ],
                "confidence": 1.0,
                "limitations": [],
                "usage": {
                    "wall_time_seconds": 1,
                    "cpu_seconds": 1,
                    "validation_attempts": 0,
                    "execution_attempts": 0,
                },
            }
        )
        submission_sha256 = sha256_model(submission)
        gates = [
            ExternalGateResult(
                benchmark_id="benchmark",
                benchmark_version="1.0",
                case_id=case.case_id,
                submission_sha256=submission_sha256,
                gate_id=gate.id,
                passed=True,
                detail="private evaluator passed",
            )
            for gate in evaluation.hard_gates
        ]
        with tempfile.TemporaryDirectory() as directory:
            context = EvaluationContext(
                benchmark_id="benchmark",
                benchmark_version="1.0",
                submission_sha256=submission_sha256,
                artifact_root=Path(directory),
            )
            result = get_evaluator(evaluation.evaluator).evaluate(
                case, evaluation, submission, gates, context
            )
        self.assertFalse(result.gates_passed)
        self.assertEqual(result.official_score, 0.0)


if __name__ == "__main__":
    unittest.main()
