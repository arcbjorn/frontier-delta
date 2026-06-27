"""Mock trainer for Phase 0 loop validation.

The real training phases will replace this with GRPO + LoRA/QLoRA updates.
Phase 0 only needs a deterministic object that records what a training step
would consume and returns a versioned solver handle.
"""

from __future__ import annotations

import dataclasses
from typing import Sequence


@dataclasses.dataclass(frozen=True)
class TrainingExample:
    """A candidate and scalar reward admitted to a training step."""

    task_id: str
    candidate_code: str
    reward: float
    split: str = "train"


@dataclasses.dataclass(frozen=True)
class TrainingStepResult:
    """Summary of a mock training step."""

    model_version: int
    examples_seen: int
    mean_reward: float
    trainer: str = "mock"


class MockTrainer:
    """Records training batches without changing model weights."""

    def __init__(self, model_version: int = 0):
        self.model_version = model_version
        self.history: list[TrainingStepResult] = []

    def step(self, examples: Sequence[TrainingExample]) -> TrainingStepResult:
        count = len(examples)
        mean_reward = 0.0
        if count:
            mean_reward = sum(ex.reward for ex in examples) / count

        self.model_version += 1
        result = TrainingStepResult(
            model_version=self.model_version,
            examples_seen=count,
            mean_reward=mean_reward,
        )
        self.history.append(result)
        return result
