"""Reward functions for experimental arms.

Each reward function maps a VerificationResult (and optionally other
signals) to a scalar reward.  All rewards are in [0, 1].
"""

from __future__ import annotations

import dataclasses
from typing import Protocol, runtime_checkable
from frontier_delta.verifier import VerificationResult


@runtime_checkable
class Reward(Protocol):
    """Interface for a reward function."""

    def compute(self, result: VerificationResult, **kwargs) -> float:
        ...


# ---------------------------------------------------------------------------
# Concrete rewards
# ---------------------------------------------------------------------------


class VerifiedReward:
    """Binary reward: 1.0 if all checked examples pass, else 0.0."""

    def compute(self, result: VerificationResult, **kwargs) -> float:
        return 1.0 if result.correct else 0.0


class RandomReward:
    """Random binary reward, seeded for reproducibility.

    This is a control arm: any signal that correlates with correctness
    cannot come from the reward function itself.
    """

    def __init__(self, seed: int = 42):
        import random
        self._rng = random.Random(seed)
        self._seed = seed

    def compute(self, result: VerificationResult, **kwargs) -> float:
        return 1.0 if self._rng.random() < 0.5 else 0.0


class FormatOnlyReward:
    """Rewards valid Python syntax regardless of correctness.

    The candidate_code is evaluated for syntax validity only.
    A syntax-valid submission gets 1.0; syntax error gets 0.0.
    """

    def compute(self, result: VerificationResult, **kwargs) -> float:
        candidate_code = kwargs.get("candidate_code", "")
        if not candidate_code:
            return 0.0
        try:
            compile(candidate_code, "<candidate>", "exec")
            return 1.0
        except SyntaxError:
            return 0.0


class PartialCreditReward:
    """Proportional reward: fraction of test examples passed.

    Not a control arm -- used as an auxiliary signal in some configurations.
    """

    def compute(self, result: VerificationResult, **kwargs) -> float:
        if result.total_examples == 0:
            return 0.0
        return result.passed_examples / result.total_examples
