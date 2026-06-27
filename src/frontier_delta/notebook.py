"""Claims-gated public notebook template.

In Phase 0 this is a concept: a local SQLite-backed renderer that
produces a static HTML report from the ledger.  Nothing is posted
externally -- every claim must be explicitly gated by human review.

The template defines the structure of a claim:
- Claim text (what is asserted).
- Supporting evidence (ledger rows, statistical tests).
- Gate status (draft, review, approved, rejected).
"""

from __future__ import annotations

import dataclasses
import sqlite3
import json
from typing import List, Optional


@dataclasses.dataclass
class Claim:
    """A single gated claim.

    Attributes:
        claim_id: unique identifier.
        text: the claim statement.
        evidence_query: SQL query that produces supporting rows from the ledger.
        gate_status: one of draft, review, approved, rejected.
        reviewer_notes: human notes from the review process.
    """

    claim_id: str
    text: str
    evidence_query: str
    gate_status: str = "draft"
    reviewer_notes: str = ""


class NotebookDB:
    """SQLite-backed notebook that stores claims and renders them.

    In Phase 0 this is a stub: it can store claims and print them,
    but the ledger integration (evidence_query execution) is a
    placeholder.

    Usage::

        nb = NotebookDB(":memory:")
        nb.add_claim(Claim("c1", "Support expansion observed", "SELECT ..."))
        print(nb.render_markdown())
    """

    def __init__(self, db_path: str = ":memory:"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()
        self._claims: List[Claim] = []

    def _init_schema(self) -> None:
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS claims (
                claim_id TEXT PRIMARY KEY,
                text TEXT NOT NULL,
                evidence_query TEXT,
                gate_status TEXT DEFAULT 'draft',
                reviewer_notes TEXT DEFAULT ''
            )
            """
        )
        self.conn.commit()

    def add_claim(self, claim: Claim) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO claims VALUES (?, ?, ?, ?, ?)",
            (
                claim.claim_id,
                claim.text,
                claim.evidence_query,
                claim.gate_status,
                claim.reviewer_notes,
            ),
        )
        self.conn.commit()

    def get_claims(self, gate_status: str | None = None) -> List[Claim]:
        if gate_status:
            rows = self.conn.execute(
                "SELECT * FROM claims WHERE gate_status = ?", (gate_status,)
            ).fetchall()
        else:
            rows = self.conn.execute("SELECT * FROM claims").fetchall()
        return [
            Claim(
                claim_id=r["claim_id"],
                text=r["text"],
                evidence_query=r["evidence_query"],
                gate_status=r["gate_status"],
                reviewer_notes=r["reviewer_notes"],
            )
            for r in rows
        ]

    def render_markdown(self) -> str:
        """Render all claims as a Markdown report."""
        claims = self.get_claims()
        lines = ["# Frontier Delta -- Notebook", "", "## Claims", ""]
        for c in claims:
            lines.append(f"### [{c.gate_status}] {c.claim_id}: {c.text}")
            lines.append(f"")
            lines.append(f"- **Status:** {c.gate_status}")
            lines.append(f"- **Evidence query:** `{c.evidence_query}`")
            if c.reviewer_notes:
                lines.append(f"- **Reviewer notes:** {c.reviewer_notes}")
            lines.append("")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Standalone: render ledger rows as a simple HTML table (no external deps)
# ---------------------------------------------------------------------------

def render_ledger_html(ledger_dicts: List[dict], title: str = "Ledger") -> str:
    """Convert a list of ledger-row dicts to a basic HTML table.

    This is a minimal renderer for Phase 0; no external posting.
    """
    if not ledger_dicts:
        return f"<html><body><h1>{title}</h1><p>No rows.</p></body></html>"

    keys = list(ledger_dicts[0].keys())
    lines = [
        "<html><body>",
        f"<h1>{title}</h1>",
        "<table border='1'><tr>",
    ]
    for k in keys:
        lines.append(f"<th>{k}</th>")
    lines.append("</tr>")
    for row in ledger_dicts:
        lines.append("<tr>")
        for k in keys:
            v = row.get(k, "")
            lines.append(f"<td>{v}</td>")
        lines.append("</tr>")
    lines.append("</table></body></html>")
    return "\n".join(lines)
