import unittest

from moose_benchmark.scoring import aggregate_results, calculate_case_score


def case_result(
    case_id,
    *,
    subcategory="F1",
    score=100.0,
    passed=True,
    case_kind="atomic",
    first_failed_stage=None,
    gates_passed=True,
):
    track = None
    if case_kind == "atomic":
        track = {
            "F": "FORM",
            "D": "DIAG",
            "R": "REPAIR",
            "V": "VERIFY",
        }[subcategory[0]]
    return {
        "schema_version": "1.0",
        "benchmark_id": "benchmark",
        "benchmark_version": "1.0.0",
        "evaluator": "structured_claim_v1",
        "case_id": case_id,
        "case_kind": case_kind,
        "track": track,
        "subcategory": subcategory if case_kind == "atomic" else None,
        "difficulty": "L1",
        "base_problem_id": f"base-{case_id}",
        "physics_domains": ["thermal_energy_transport"],
        "submission_sha256": "0" * 64,
        "submitted_artifacts": [],
        "component_scores": {
            "capability": score,
            "evidence": score,
            "contract": score,
        },
        "raw_score": score if gates_passed else 100.0,
        "official_score": score,
        "gates_passed": gates_passed,
        "case_passed": passed,
        "gate_results": (
            []
            if gates_passed
            else [
                {
                    "id": "workflow_gate",
                    "passed": False,
                    "detail": "failed",
                    "stage": first_failed_stage,
                }
            ]
        ),
        "criterion_details": {},
        "first_failed_stage": first_failed_stage,
    }


class ScoringTests(unittest.TestCase):
    def test_weighted_case_score(self):
        result = calculate_case_score(
            90,
            80,
            100,
            [{"id": "gate", "passed": True, "detail": "ok"}],
        )
        self.assertEqual(result["raw_score"], 89.0)
        self.assertEqual(result["official_score"], 89.0)
        self.assertTrue(result["case_passed"])

    def test_failed_gate_zeroes_official_score(self):
        result = calculate_case_score(
            100,
            100,
            100,
            [{"id": "gate", "passed": False, "detail": "failed"}],
        )
        self.assertEqual(result["raw_score"], 100.0)
        self.assertEqual(result["official_score"], 0.0)
        self.assertFalse(result["case_passed"])

    def test_macro_average_does_not_weight_large_subcategory(self):
        results = [
            case_result("f1-1"),
            case_result("f1-2"),
            case_result("f1-3"),
            case_result("d1-1", subcategory="D1", score=0.0, passed=False),
        ]
        aggregate = aggregate_results(results)
        self.assertEqual(aggregate["subcategory_scores"], {"D1": 0.0, "F1": 100.0})
        self.assertEqual(aggregate["atomic_capability_score"], 50.0)

    def test_integrated_workflow_completion_is_reported_separately(self):
        aggregate = aggregate_results(
            [
                case_result(
                    "integrated-pass",
                    case_kind="integrated_workflow",
                ),
                case_result(
                    "integrated-fail",
                    score=0.0,
                    passed=False,
                    case_kind="integrated_workflow",
                    first_failed_stage="execution",
                    gates_passed=False,
                ),
            ]
        )
        self.assertEqual(aggregate["atomic_case_count"], 0)
        self.assertEqual(aggregate["integrated_workflow_case_count"], 2)
        self.assertEqual(aggregate["integrated_workflow_completion_rate"], 0.5)
        self.assertEqual(aggregate["integrated_first_failed_stage_counts"], {"execution": 1})

    def test_aggregate_rejects_duplicate_case_ids(self):
        with self.assertRaisesRegex(ValueError, "one result per case_id"):
            aggregate_results([case_result("duplicate"), case_result("duplicate")])

    def test_aggregate_rejects_out_of_range_scores(self):
        invalid = case_result("invalid")
        invalid["official_score"] = 1_000_000.0
        with self.assertRaises(ValueError):
            aggregate_results([invalid])


if __name__ == "__main__":
    unittest.main()
