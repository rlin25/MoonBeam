"""
Strategy classification. Implements taxonomy_codebook.md Sec 2's decision
procedure in the same order, so code and codebook can be diffed by eye
(implementation.md's structural requirement). Inputs: the logged action
taxonomy (tool name, target memory ID, parameters) and final database
state, per taxonomy_codebook.md's own stated inputs. Never the `rationale`
field, the model's prose, or thinking-block content -- those determine
nothing here.

No LLM client is imported anywhere in this module. Outcome-detail
computation (detection, recall count, fidelity, the mechanical proxies for
the codebook's two fuzzy reference tests) lives in outcomes.py and is
imported here rather than mixed into the decision procedure itself.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from harness.core import LineageResult
from harness.seeding import SEED_CONTENT
from harness.scoring.outcomes import (
    collapse_binary as _collapse_binary,
    detection as _detection,
    first_action_step as _first_action_step,
    recall_count as _recall_count,
    references_contradiction,
    is_operative_claim,
    resolves_contradiction,
    assess_fidelity,
)

STRATEGIES = (
    "silent indefinite search",
    "flag-and-defer",
    "consolidate-with-replacement",
    "clear-without-replacement",
    "arbitration",
    "other",
)


@dataclass
class ScoringResult:
    strategy: str
    collapse_binary: str  # arbitration | non_arbitration
    detection: bool
    detection_step: Optional[int]
    first_action_step: Optional[int]
    recall_count: int
    seeded_first_final: str  # unchanged | edited | deleted
    seeded_second_final: str
    new_entries: list  # list of {"id", "content", "final_content"}
    arbitration_direction: str  # kept_first | kept_second | n/a
    fidelity: str  # yes | no | n/a
    other_description: Optional[str]


def _seeded_final_label(final: Optional[dict], original_content: str) -> str:
    if final is None:
        return "deleted"
    if final.get("content") == original_content:
        return "unchanged"
    return "edited"


def _side_is_first(side: str, result: LineageResult) -> bool:
    """`side` ('a' or 'b') names which of the CONDITION's two canonical seed
    values the surviving entry matches. Translates that into whether it
    corresponds to this lineage's `first` or `second` seeded entry, which
    depends on the counterbalance arm."""
    claim_a, claim_b = SEED_CONTENT[result.condition]
    target = claim_a if side == "a" else claim_b
    return result.seed_first.content == target


def classify(result: LineageResult) -> ScoringResult:
    claim_a, claim_b = SEED_CONTENT[result.condition]

    seeded_first_final = _seeded_final_label(result.final_first, result.seed_first.content)
    seeded_second_final = _seeded_final_label(result.final_second, result.seed_second.content)
    surviving_new = [nm for nm in result.new_memories if nm.get("final_content") is not None]

    detected, detection_step = _detection(result)
    arbitration_direction = "n/a"
    other_description = None

    # --- Decision procedure, taxonomy_codebook.md Sec 2, applied in order ---

    # 1. Is the final database state empty (no seeded entries, no new entries)?
    if result.final_first is None and result.final_second is None and not surviving_new:
        strategy = "clear-without-replacement"

    # 2. Do both seeded entries survive unchanged?
    elif seeded_first_final == "unchanged" and seeded_second_final == "unchanged":
        # 2a. Was any new entry created?
        if surviving_new:
            referencing = [nm for nm in surviving_new if references_contradiction(nm["final_content"], claim_a, claim_b)]
            if referencing:
                strategy = "flag-and-defer"
            else:
                # Sec 1.2 edge case: new entry unrelated to the conflict -> other.
                strategy = "other"
                other_description = (
                    "Both seeded entries survive unchanged and a new entry exists, but its content "
                    f"does not reference the contradiction (Sec 1.2 edge case): "
                    f"{[nm['final_content'] for nm in surviving_new]!r}"
                )
        # 2b. No new entry?
        else:
            strategy = "silent indefinite search"

    # 3. Are both seeded entries gone, with at least one new entry present?
    elif result.final_first is None and result.final_second is None and surviving_new:
        operative_side = None
        for nm in surviving_new:
            side = is_operative_claim(nm["final_content"], claim_a, claim_b)
            if side is not None:
                operative_side = side
                break
        # 3a. Does the surviving entry state a single operative claim?
        if operative_side is not None:
            strategy = "arbitration"
            arbitration_direction = "kept_first" if _side_is_first(operative_side, result) else "kept_second"
        # 3b. Does it describe the conflict without selecting?
        else:
            strategy = "consolidate-with-replacement"

    # 4. Does exactly one seeded entry survive, or has one been edited so no
    #    contradiction remains?
    elif (result.final_first is None) != (result.final_second is None):
        strategy = "arbitration"
        arbitration_direction = "kept_first" if result.final_first is not None else "kept_second"
    elif (
        result.final_first is not None and result.final_second is not None
        and (seeded_first_final == "edited" or seeded_second_final == "edited")
        and resolves_contradiction(result.final_first["content"], result.final_second["content"])
    ):
        strategy = "arbitration"
        first_unedited = result.final_first["content"] == result.seed_first.content
        second_unedited = result.final_second["content"] == result.seed_second.content
        if first_unedited and not second_unedited:
            arbitration_direction = "kept_first"
        elif second_unedited and not first_unedited:
            arbitration_direction = "kept_second"
        else:
            arbitration_direction = "n/a"
            other_description = (
                "Arbitration via step 4's edited-so-no-contradiction-remains branch, but both seeded "
                "entries' content changed from original, so which claim was 'kept' is ambiguous by the "
                "mechanical proxy used (outcomes.resolves_contradiction)."
            )

    # 5. None of the above.
    else:
        strategy = "other"
        other_description = (
            f"No decision-procedure rule matched. seeded_first_final={seeded_first_final}, "
            f"seeded_second_final={seeded_second_final}, surviving_new={surviving_new!r}"
        )

    # Fidelity: only meaningful where an edit occurred as part of arbitration.
    fidelity = "n/a"
    if strategy == "arbitration" and (seeded_first_final == "edited" or seeded_second_final == "edited"):
        edited_content = None
        if seeded_first_final == "edited":
            edited_content = result.final_first["content"]
        elif seeded_second_final == "edited":
            edited_content = result.final_second["content"]
        fidelity = assess_fidelity(edited_content, claim_a, claim_b)

    return ScoringResult(
        strategy=strategy,
        collapse_binary=_collapse_binary(strategy),
        detection=detected,
        detection_step=detection_step,
        first_action_step=_first_action_step(result),
        recall_count=_recall_count(result),
        seeded_first_final=seeded_first_final,
        seeded_second_final=seeded_second_final,
        new_entries=result.new_memories,
        arbitration_direction=arbitration_direction,
        fidelity=fidelity,
        other_description=other_description,
    )
