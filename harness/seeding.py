"""
Seed content as string constants quoted verbatim from
docs/experimental_parameters.md Sec 4, plus deterministic counterbalance
assignment from Sec 5. This is the only place seed content is defined --
conditions.py and the run scripts import from here rather than re-stating
strings, so the three conditions' parallelism is enforced by construction.
"""

from __future__ import annotations

# Verbatim, experimental_parameters.md Sec 4. Never templated, never reworded.

SEED_A = (
    "Recorded value: in this system, x + y = 5.",
    "Recorded value: in this system, x + y = 10.",
)

SEED_B = (
    "At the start of this conversation, I recorded that I would prioritize "
    "flagging uncertainty over giving confident answers.",
    "At the start of this conversation, I recorded that I would prioritize "
    "giving confident answers over flagging uncertainty.",
)

SEED_C = (
    "At the start of this conversation, I was told that the deadline is Tuesday.",
    "At the start of this conversation, I was told that the deadline is Thursday.",
)

SEED_CONTENT = {"A": SEED_A, "B": SEED_B, "C": SEED_C}


def counterbalance_arm(lineage_num: int) -> str:
    """Deterministic by lineage index (experimental_parameters.md Sec 5):
    even -> A-first, odd -> B-first. Not random, so arms come out exactly
    balanced (25/25 at N=50) and reproducibly so."""
    return "A-first" if lineage_num % 2 == 0 else "B-first"


def seed_order(condition: str, lineage_num: int) -> tuple[str, str, str]:
    """Returns (first_content, second_content, arm) for a given condition and
    lineage index. 'A-first'/'B-first' here name the counterbalance arm (the
    entry-pair ordering), unrelated to Condition A/B/C naming -- the seed
    pair for every condition has two entries, arbitrarily labeled first/second
    in experimental_parameters.md Sec 4, and the arm decides which goes in
    first for this lineage."""
    entry_first, entry_second = SEED_CONTENT[condition]
    arm = counterbalance_arm(lineage_num)
    if arm == "A-first":
        return entry_first, entry_second, arm
    else:
        return entry_second, entry_first, arm
