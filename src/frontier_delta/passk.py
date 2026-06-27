"""Unbiased pass@k estimator from Chen et al. (Codex, 2021).

Given n total samples, c correct samples, and k <= n, the unbiased
estimator for pass@k is:

    pass@k = 1 - C(n-c, k) / C(n, k)

where C(n, k) is the binomial coefficient "n choose k", with C(n, k) = 0
when k > n.

Reference: https://arxiv.org/abs/2107.03374
"""

from __future__ import annotations

import math


def _binom(n: int, k: int) -> float:
    """Compute binomial coefficient C(n, k) safely."""
    if k < 0 or k > n:
        return 0.0
    if k == 0 or k == n:
        return 1.0
    # Use math.comb on Python 3.8+
    return math.comb(n, k)


def pass_at_k(n: int, c: int, k: int) -> float:
    """Unbiased pass@k estimator.

    Args:
        n: total number of samples generated.
        c: number of correct samples (those that pass all tests).
        k: number of samples in the hypothetical pass@k evaluation.

    Returns:
        Estimated probability that at least one of k samples is correct.

    Raises:
        ValueError: if k > n (you cannot sample more than you have).
    """
    if k > n:
        raise ValueError(f"k ({k}) cannot exceed n ({n})")
    if n == 0:
        return 0.0
    if n - c < k:
        # All k-sized subsets include at least one correct sample.
        return 1.0
    return 1.0 - _binom(n - c, k) / _binom(n, k)


def pass_at_k_vector(
    n: int, c: int, ks: list[int]
) -> dict[int, float]:
    """Compute pass@k for multiple k values at once.

    Args:
        n: total samples.
        c: correct samples.
        ks: list of k values to compute.

    Returns:
        Dict mapping k to pass@k estimate.
    """
    return {k: pass_at_k(n, c, k) for k in ks}


# ---------------------------------------------------------------------------
# Convenience: compute per-task solve counts -> aggregate pass@k
# ---------------------------------------------------------------------------


def aggregate_pass_at_k(
    n_per_task: int,
    correct_counts: list[int],
    k: int,
) -> float:
    """Aggregate pass@k across tasks.

    Follows the standard convention: for each task, compute the pass@k
    estimate from (n_per_task, c_i, k), then average over tasks.

    Args:
        n_per_task: samples per task (assumed equal across tasks).
        correct_counts: number of correct samples for each task.
        k: evaluation k.

    Returns:
        Mean pass@k across tasks.
    """
    if not correct_counts:
        return 0.0
    estimates = [pass_at_k(n_per_task, c, k) for c in correct_counts]
    return sum(estimates) / len(estimates)
