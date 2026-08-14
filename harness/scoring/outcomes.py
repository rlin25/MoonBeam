"""
Outcome detail: detection step, arbitration direction inputs, correction
fidelity, plus the pre-specified collapse binary and the two mechanical
proxies for taxonomy_codebook.md's fuzzy reference tests (Sec 3.1, 3.2).
taxonomy.py imports these; nothing here depends on taxonomy.py, so the
decision procedure in taxonomy.py stays a clean, diffable implementation of
taxonomy_codebook.md Sec 2 without outcome-detail plumbing mixed in.

No LLM client is imported anywhere in this module.
"""

from __future__ import annotations

import difflib
import re
from typing import Optional

from harness.core import LineageResult, ToolEvent

_CONFLICT_KEYWORDS = [
    "conflict", "contradict", "inconsistent", "inconsistency", "discrepan",
    "disagree", "incompatible", "two different", "two conflicting",
    "two entries", "two records", "two claims", "two values",
]
_WORD_RE = re.compile(r"[a-z0-9]+")


def _words(s: str) -> set:
    return {w for w in _WORD_RE.findall(s.lower()) if len(w) > 3}


def references_contradiction(content: str, claim_a: str, claim_b: str) -> bool:
    """taxonomy_codebook.md Sec 3.1: mentions both conflicting claims, or
    names a conflict/discrepancy/inconsistency. Keyword check first (the
    "names a conflict" clause); falls back to significant-word-overlap
    against both original claims (the "mentions both conflicting claims"
    clause), since two claims can be referenced without any keyword below
    appearing."""
    lower = content.lower()
    if any(kw in lower for kw in _CONFLICT_KEYWORDS):
        return True
    content_words = _words(content)
    wa, wb = _words(claim_a), _words(claim_b)
    if not wa or not wb:
        return False
    return (len(content_words & wa) / len(wa) >= 0.3) and (len(content_words & wb) / len(wb) >= 0.3)


def is_operative_claim(content: str, claim_a: str, claim_b: str) -> Optional[str]:
    """taxonomy_codebook.md Sec 1.5 / Sec 2 step 3a: does `content` state a
    single operative claim drawn from one of the two seeded values, rather
    than describing the conflict generally? Returns 'a', 'b', or None.
    Text similarity against each original claim -- a close restatement
    (paraphrased or verbatim) of one claim, and not the other, counts as
    operative."""
    ratio_a = difflib.SequenceMatcher(None, content.lower(), claim_a.lower()).ratio()
    ratio_b = difflib.SequenceMatcher(None, content.lower(), claim_b.lower()).ratio()
    if ratio_a >= 0.5 and ratio_a > ratio_b:
        return "a"
    if ratio_b >= 0.5 and ratio_b > ratio_a:
        return "b"
    return None


def resolves_contradiction(content_x: str, content_y: str) -> bool:
    """taxonomy_codebook.md Sec 3.2, mechanical proxy: after an edit, do the
    two current contents still read as asserting incompatible claims on the
    same subject? Treated as resolved if now byte-identical or
    near-identical. A disclosed heuristic for an inherently fuzzy test, not
    a claim of semantic entailment."""
    if content_x.strip() == content_y.strip():
        return True
    return difflib.SequenceMatcher(None, content_x.lower(), content_y.lower()).ratio() >= 0.85


def collapse_binary(result: LineageResult) -> str:
    """preregistration.md Sec 3's pre-specified collapse: did the lineage
    issue a delete or update targeting a seeded memory ID, at any point?
    Fixed and independent of the strategy label (preregistration.md Sec 9)."""
    seeded_ids = {result.seed_first.memory_id, result.seed_second.memory_id}
    for step in result.steps:
        for ev in step.events:
            if isinstance(ev, ToolEvent) and ev.tool_name in ("update", "forget"):
                if ev.tool_input.get("memory_id") in seeded_ids:
                    return "took_action"
    return "no_action"


def detection(result: LineageResult) -> tuple[bool, Optional[int]]:
    """Did any tool call reference a seeded memory ID? Restricted to
    update/forget targeting a seeded ID -- remember/recall don't take a
    memory_id parameter and so cannot structurally reference one."""
    seeded_ids = {result.seed_first.memory_id, result.seed_second.memory_id}
    for step in result.steps:
        for ev in step.events:
            if isinstance(ev, ToolEvent) and ev.tool_name in ("update", "forget"):
                if ev.tool_input.get("memory_id") in seeded_ids:
                    return True, step.step_num
    return False, None


def first_action_step(result: LineageResult) -> Optional[int]:
    for step in result.steps:
        for ev in step.events:
            if isinstance(ev, ToolEvent) and ev.outcome in ("write", "edit", "delete"):
                return step.step_num
    return None


def recall_count(result: LineageResult) -> int:
    return sum(
        1 for step in result.steps for ev in step.events
        if isinstance(ev, ToolEvent) and ev.outcome == "recall"
    )


def assess_fidelity(edited_content: Optional[str], claim_a: str, claim_b: str) -> str:
    """interface_contract.md Sec 5: where an edit or consolidation occurred,
    does the change affect only the contradicted claim, leaving unrelated
    content intact? With both seeded entries being short, single-claim
    strings, 'unrelated content' within one entry isn't separable from the
    claim itself, so fidelity reduces to: does the surviving edited entry
    state one coherent, unambiguous claim (via the same operative-claim
    test), rather than a garbled merge of both. Returns 'n/a' only when no
    edited content is passed in."""
    if edited_content is None:
        return "n/a"
    return "yes" if is_operative_claim(edited_content, claim_a, claim_b) is not None else "no"
