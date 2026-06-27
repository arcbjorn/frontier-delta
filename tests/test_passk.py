import math
import unittest

from frontier_delta.passk import aggregate_pass_at_k, pass_at_k


class PassKTests(unittest.TestCase):
    def test_pass_at_1_matches_fraction_correct(self):
        self.assertTrue(math.isclose(pass_at_k(10, 3, 1), 0.3))

    def test_pass_at_k_extremes(self):
        self.assertEqual(pass_at_k(10, 0, 5), 0.0)
        self.assertEqual(pass_at_k(10, 10, 5), 1.0)
        self.assertEqual(pass_at_k(10, 3, 10), 1.0)

    def test_pass_at_k_formula(self):
        expected = 1.0 - math.comb(7, 5) / math.comb(10, 5)
        self.assertTrue(math.isclose(pass_at_k(10, 3, 5), expected))

    def test_k_cannot_exceed_n(self):
        with self.assertRaises(ValueError):
            pass_at_k(4, 1, 5)

    def test_aggregate_pass_at_k(self):
        value = aggregate_pass_at_k(10, [0, 5, 10], 1)
        self.assertTrue(math.isclose(value, 0.5))


if __name__ == "__main__":
    unittest.main()
