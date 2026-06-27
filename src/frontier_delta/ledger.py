"""Support-set ledger: per-task, per-round, per-arm data cells.

The ledger is the central data structure for the experiment.  Every
measurement -- solve counts, classifications, verifier disagreement,
cost -- is recorded as a row in the ledger.  The ledger can be
serialized to JSON for analysis and rendering.
"""

from __future__ import annotations

import dataclasses
import json
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Color labels for support-set classification
# ---------------------------------------------------------------------------

@dataclasses.dataclass(frozen=True)
class ColorLabel:
    """Human-readable label with a terminal color code.

    Attributes:
        label: classification label (gained, lost, sharpened, unchanged).
        color: ANSI terminal color name.
        symbol: single-character symbol for compact display.
    """

    label: str
    color: str
    symbol: str


COLOR_MAP: Dict[str, ColorLabel] = {
    "gained": ColorLabel("gained", "green", "+"),
    "lost": ColorLabel("lost", "red", "-"),
    "sharpened": ColorLabel("sharpened", "yellow", "~"),
    "unchanged": ColorLabel("unchanged", "white", "."),
}


# ---------------------------------------------------------------------------
# Ledger row
# ---------------------------------------------------------------------------


@dataclasses.dataclass
class LedgerRow:
    """A single measurement row in the support-set ledger.

    Attributes:
        task_id: which task.
        round_idx: which training round (0 = base model).
        arm: experimental arm name.
        n_samples: number of rollouts.
        c_correct: number of correct rollouts.
        pass_at_1: pass@1 estimate.
        pass_at_k: dict of k -> pass@k estimate.
        p_solve: beta-binomial point estimate of solve probability.
        label: support-set classification label.
        verifier_disagreement: fraction of examples where checker A != checker B.
        cost_tokens: total token count for this task-round.
        meta: arbitrary additional data.
    """

    task_id: str
    round_idx: int
    arm: str
    n_samples: int
    c_correct: int
    pass_at_1: float
    pass_at_k: Dict[int, float] = dataclasses.field(default_factory=dict)
    p_solve: float = 0.0
    label: str = "unchanged"
    verifier_disagreement: float = 0.0
    cost_tokens: int = 0
    meta: dict = dataclasses.field(default_factory=dict)


class Ledger:
    """Accumulating ledger of per-task, per-round measurements.

    Usage::

        ledger = Ledger()
        ledger.add(row)
        rows = ledger.rows_for_arm("vanilla_rlvr")
        ledger.to_json("ledger.json")
    """

    def __init__(self):
        self._rows: List[LedgerRow] = []

    def add(self, row: LedgerRow) -> None:
        self._rows.append(row)

    def rows_for_arm(self, arm: str) -> List[LedgerRow]:
        return [r for r in self._rows if r.arm == arm]

    def rows_for_round(self, round_idx: int) -> List[LedgerRow]:
        return [r for r in self._rows if r.round_idx == round_idx]

    def rows_for_task(self, task_id: str) -> List[LedgerRow]:
        return [r for r in self._rows if r.task_id == task_id]

    def all_rows(self) -> List[LedgerRow]:
        return list(self._rows)

    def to_dicts(self) -> List[dict]:
        return [dataclasses.asdict(r) for r in self._rows]

    def to_json(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump(self.to_dicts(), f, indent=2, default=str)

    @classmethod
    def from_json(cls, path: str) -> "Ledger":
        with open(path) as f:
            raw = json.load(f)
        ledger = cls()
        for d in raw:
            ledger.add(LedgerRow(**d))
        return ledger

    def summary(self) -> dict:
        """Quick summary across all rows."""
        arms = list({r.arm for r in self._rows})
        rounds = list({r.round_idx for r in self._rows})
        tasks = list({r.task_id for r in self._rows})
        labels = {}
        for r in self._rows:
            labels[r.label] = labels.get(r.label, 0) + 1
        return {
            "total_rows": len(self._rows),
            "arms": arms,
            "rounds": rounds,
            "tasks": len(tasks),
            "label_counts": labels,
        }
