"""Support-set classification: gained / lost / sharpened / unchanged.

Uses per-problem solve counts from two time points (e.g., base model vs.
after training) to classify each task into one of four categories.
"""

from __future__ import annotations

import dataclasses
import math
from typing import List, Tuple


@dataclasses.dataclass(frozen=True)
class SupportSetClassification:
    """Classification of a single task across two measurement points.

    Attributes:
        task_id: which task.
        label: one of "gained", "lost", "sharpened", "unchanged".
        p_before: estimated solve probability before (point estimate).
        p_after: estimated solve probability after.
        delta: p_after - p_before.
        n_before: sample count before.
        c_before: correct count before.
        n_after: sample count after.
        c_after: correct count after.
    """

    task_id: str
    label: str
    p_before: float
    p_after: float
    delta: float
    n_before: int
    c_before: int
    n_after: int
    c_after: int


# ---------------------------------------------------------------------------
# Classification logic
# ---------------------------------------------------------------------------

def _estimate_p(n: int, c: int, pseudocount: float = 0.5) -> float:
    """Beta-binomial point estimate with pseudocount smoothing."""
    return (c + pseudocount) / (n + 2 * pseudocount)


def classify_task(
    task_id: str,
    n_before: int,
    c_before: int,
    n_after: int,
    c_after: int,
    epsilon: float = 0.05,
    delta_min: float = 0.1,
) -> SupportSetClassification:
    """Classify a task as gained, lost, sharpened, or unchanged.

    A task is "solvable" if its estimated solve probability > 1 - epsilon.
    A task is "unsolvable" if its estimated solve probability < epsilon.

    Classification rules:
    - gained: was unsolvable, now solvable.
    - lost: was solvable, now unsolvable.
    - sharpened: was solvable, still solvable, delta > delta_min.
    - unchanged: everything else.

    Args:
        task_id: task identifier.
        n_before: number of samples at time 1.
        c_before: number of correct samples at time 1.
        n_after: number of samples at time 2.
        c_after: number of correct samples at time 2.
        epsilon: solvability threshold.
        delta_min: minimum probability change to count as sharpened.

    Returns:
        SupportSetClassification.
    """
    p_before = _estimate_p(n_before, c_before)
    p_after = _estimate_p(n_after, c_after)
    delta = p_after - p_before

    solvable_before = p_before > 1.0 - epsilon
    solvable_after = p_after > 1.0 - epsilon
    unsolvable_before = p_before < epsilon
    unsolvable_after = p_after < epsilon

    if unsolvable_before and solvable_after:
        label = "gained"
    elif solvable_before and unsolvable_after:
        label = "lost"
    elif solvable_before and solvable_after and delta > delta_min:
        label = "sharpened"
    else:
        label = "unchanged"

    return SupportSetClassification(
        task_id=task_id,
        label=label,
        p_before=p_before,
        p_after=p_after,
        delta=delta,
        n_before=n_before,
        c_before=c_before,
        n_after=n_after,
        c_after=c_after,
    )


def classify_all(
    task_ids: List[str],
    n_before: List[int],
    c_before: List[int],
    n_after: List[int],
    c_after: List[int],
    epsilon: float = 0.05,
    delta_min: float = 0.1,
) -> List[SupportSetClassification]:
    """Classify all tasks.

    Args:
        task_ids: list of task identifiers.
        n_before: samples per task before.
        c_before: correct per task before.
        n_after: samples per task after.
        c_after: correct per task after.
        epsilon: solvability threshold.
        delta_min: minimum delta for sharpened.

    Returns:
        List of classifications, one per task.
    """
    return [
        classify_task(tid, nb, cb, na, ca, epsilon, delta_min)
        for tid, nb, cb, na, ca in zip(
            task_ids, n_before, c_before, n_after, c_after
        )
    ]


def summary(classifications: List[SupportSetClassification]) -> dict:
    """Return a dict of label -> count."""
    counts: dict[str, int] = {"gained": 0, "lost": 0, "sharpened": 0, "unchanged": 0}
    for c in classifications:
        counts[c.label] += 1
    return counts
