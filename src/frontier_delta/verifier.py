"""Verification interface and PythonFunctionChecker.

The Checker evaluates candidate solutions against either public training
examples or held-out examples using the sandbox. It is the ground-truth
signal: no learned model.
"""

from __future__ import annotations

import dataclasses
from typing import List, Protocol, runtime_checkable

from frontier_delta.tasks import Task
from frontier_delta.sandbox import execute_candidate_on_example, SandboxResult


@dataclasses.dataclass(frozen=True)
class VerificationResult:
    """Outcome of verifying a candidate solution on a task.

    Attributes:
        task_id: which task was evaluated.
        correct: whether the candidate passed ALL test examples.
        total_examples: number of test examples checked.
        passed_examples: how many test examples passed.
        failures: list of (example_index, expected, got) for failed examples.
        split: which task split was evaluated ("train" or "test").
        sandbox_error: True if any example failed due to sandbox error (timeout, crash).
    """

    task_id: str
    correct: bool
    total_examples: int
    passed_examples: int
    split: str = "test"
    failures: List[dict] = dataclasses.field(default_factory=list)
    sandbox_error: bool = False


@runtime_checkable
class Checker(Protocol):
    """Interface for a verifier.

    A Checker takes a Task and candidate solution code and returns
    a VerificationResult.  Implementations must be deterministic and
    must not use learned models.
    """

    def check(
        self, task: Task, candidate_code: str, split: str = "test"
    ) -> VerificationResult:
        ...


class PythonFunctionChecker:
    """Checks a Python function candidate against a Task example split.

    Each example is executed in the sandbox. The candidate passes if its
    return value matches the expected output for every example in the split.
    """

    def __init__(self, timeout_sec: float = 5.0):
        self.timeout_sec = timeout_sec

    def check(
        self, task: Task, candidate_code: str, split: str = "test"
    ) -> VerificationResult:
        if split == "train":
            examples = task.train_examples
        elif split == "test":
            examples = task.test_examples
        else:
            raise ValueError(f"Unknown split: {split!r}")

        passed = 0
        failures: List[dict] = []
        sandbox_error = False

        for i, example in enumerate(examples):
            result = execute_candidate_on_example(
                candidate_code, example, timeout_sec=self.timeout_sec
            )
            if not result.success:
                sandbox_error = True
                failures.append(
                    {
                        "example_index": i,
                        "expected": repr(example.output),
                        "got": f"ERROR: {result.error}",
                    }
                )
                continue

            got = result.output
            expected = repr(example.output)
            if got == expected:
                passed += 1
            else:
                failures.append(
                    {
                        "example_index": i,
                        "expected": expected,
                        "got": got,
                    }
                )

        return VerificationResult(
            task_id=task.task_id,
            correct=(passed == len(examples)),
            total_examples=len(examples),
            passed_examples=passed,
            split=split,
            failures=failures,
            sandbox_error=sandbox_error,
        )
