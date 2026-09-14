import unittest

from moose_benchmark.comparison import MISSING, compare, resolve_json_pointer


class ComparisonTests(unittest.TestCase):
    def test_json_pointer_and_normalized_comparison(self):
        document = {"claim": {"stage": "Object  Schema\nValidation"}}
        actual = resolve_json_pointer(document, "/claim/stage")
        score, _ = compare(actual, "object schema validation", "normalized_exact")
        self.assertEqual(score, 1.0)

    def test_set_f1_awards_partial_credit(self):
        score, _ = compare(["a", "b"], ["a", "b", "c"], "set_f1")
        self.assertAlmostEqual(score, 0.8)

    def test_sequence_comparator_penalizes_wrong_order(self):
        score, _ = compare(["root", "terminal"], ["terminal", "root"], "sequence_lcs")
        self.assertEqual(score, 0.5)

    def test_empty_json_object_is_a_valid_subset(self):
        score, reason = compare({}, {}, "json_subset")
        self.assertEqual((score, reason), (1.0, "matched"))

    def test_negative_sequence_index_is_not_a_json_pointer_index(self):
        self.assertIs(resolve_json_pointer({"items": ["last"]}, "/items/-1"), MISSING)


if __name__ == "__main__":
    unittest.main()
