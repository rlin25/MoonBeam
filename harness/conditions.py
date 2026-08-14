"""
The three conditions, expressed as data rather than three code paths
(implementation.md Sec 3: "this should be a small table, not three
modules"). Every code path below is shared; the only thing that varies
across A/B/C is which seed pair `run_condition_lineage` pulls from
seeding.SEED_CONTENT.
"""

from __future__ import annotations

from pathlib import Path

from anthropic import Anthropic

from harness.core import LineageResult, run_lineage
from harness.seeding import seed_order

CONDITIONS = {
    "A": "Arbitrary contradiction",
    "B": "Self-referential contradiction",
    "C": "First-person bridge",
}


def run_condition_lineage(
    client: Anthropic, condition: str, lineage_num: int, db_path: Path,
) -> LineageResult:
    """The single entry point every condition's lineage goes through --
    seed content is the only condition-dependent input; everything else
    (session id shape, tool schema, prompt assembly, step loop) is
    core.run_lineage, shared unmodified across A, B, and C."""
    first_content, second_content, arm = seed_order(condition, lineage_num)
    return run_lineage(
        client, condition, lineage_num, db_path,
        seed_first_content=first_content, seed_second_content=second_content,
        counterbalance_arm=arm,
    )
