import unittest

from frontier_delta.rewards import FormatOnlyReward, PartialCreditReward, RandomReward, VerifiedReward
from frontier_delta.verifier import VerificationResult


class RewardTests(unittest.TestCase):
    def test_verified_reward(self):
        good = VerificationResult("t", True, 3, 3)
        bad = VerificationResult("t", False, 3, 1)
        self.assertEqual(VerifiedReward().compute(good), 1.0)
        self.assertEqual(VerifiedReward().compute(bad), 0.0)

    def test_random_reward_is_seeded_binary(self):
        reward = RandomReward(seed=1)
        values = [reward.compute(VerificationResult("t", True, 1, 1)) for _ in range(5)]
        self.assertEqual(values, [1.0, 0.0, 0.0, 1.0, 1.0])

    def test_format_only_reward_checks_syntax(self):
        reward = FormatOnlyReward()
        result = VerificationResult("t", False, 1, 0)
        self.assertEqual(
            reward.compute(result, candidate_code="def solve(x):\n    return x\n"),
            1.0,
        )
        self.assertEqual(reward.compute(result, candidate_code="def solve(:"), 0.0)

    def test_partial_credit_reward(self):
        result = VerificationResult("t", False, 4, 3)
        self.assertEqual(PartialCreditReward().compute(result), 0.75)


if __name__ == "__main__":
    unittest.main()
