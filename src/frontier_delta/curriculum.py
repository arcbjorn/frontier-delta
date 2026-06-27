"""Curriculum stubs: difficulty bands and label-decay monitor.

These are placeholders for Phase 0.  The full implementation (Phase 1+)
will track proposer-estimated difficulty and monitor whether tasks drift
in solvability over rounds.
"""

from __future__ import annotations

import dataclasses
from typing import List


@dataclasses.dataclass(frozen=True)
class DifficultyBand:
    """A difficulty band with a label and an approximate solve rate range.

    Attributes:
        label: human-readable band name (e.g., "easy", "medium", "hard").
        min_solve_rate: approximate lower bound of solve rate in this band.
        max_solve_rate: approximate upper bound.
    """

    label: str
    min_solve_rate: float
    max_solve_rate: float


DEFAULT_BANDS: List[DifficultyBand] = [
    DifficultyBand("easy", 0.7, 1.0),
    DifficultyBand("medium", 0.3, 0.7),
    DifficultyBand("hard", 0.0, 0.3),
]


class LabelDecayMonitor:
    """Stub: monitors whether task difficulty labels drift over rounds.

    In the full system, this tracks how the solvability of tasks changes
    as training proceeds, flagging tasks that become "too easy" or
    unexpectedly hard.  Phase 0 stub returns empty.
    """

    def __init__(self, bands: List[DifficultyBand] | None = None):
        self.bands = bands or DEFAULT_BANDS
        self._history: list[dict] = []

    def record(self, round_idx: int, per_task_solve_rates: dict[str, float]) -> None:
        """Record solve rates for a round.  Stub."""
        self._history.append(
            {"round": round_idx, "rates": dict(per_task_solve_rates)}
        )

    def decayed_tasks(self, threshold: float = 0.9) -> list[str]:
        """Return tasks whose solve rate exceeds threshold.  Stub."""
        return []

    def summary(self) -> dict:
        """Return a summary of label decay.  Stub."""
        return {"bands": len(self.bands), "rounds_recorded": len(self._history)}
