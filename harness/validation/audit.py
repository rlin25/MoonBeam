"""
Mechanical classifier audit. Re-derives strategy labels for a random 10% of
lineages directly from raw transcript data (LineageResult) and final
database state, by a path independent of scoring/taxonomy.py.

Structural requirement (implementation.md Sec 3, Sec 5): this module MUST
NOT import scoring/taxonomy.py or scoring/outcomes.py. Importing the thing
being audited -- or even its shared helper functions -- would make the
audit circular: a bug in a shared heuristic (e.g. the fuzzy
references-the-contradiction check) would silently pass both the classifier
and the audit built on the same function. Every check below is
independently written, including its own copies of the two fuzzy-text
heuristics taxonomy_codebook.md Sec 3 calls for, deliberately structured
differently from outcomes.py's versions (word-set Jaccard here vs.
overlap-ratio there) so a bug specific to one implementation shows up as a
disagreement rather than being replicated in both.

No LLM client is imported anywhere in this module.
"""

from __future__ import annotations

import difflib
import re

from harness.core import LineageResult, ToolEvent
from harness.seeding import SEED_CONTENT

_CONFLICT_WORDS = {
    "conflict", "conflicting", "contradict", "contradicts", "contradicting",
    "contradiction", "inconsistent", "inconsistency", "discrepancy",
    "discrepant", "disagree", "disagreement", "incompatible",
}
_TOKEN_RE = re.compile(r"[a-zA-Z0-9]+")


def _tokens(s: str) -> set:
    return {t.lower() for t in _TOKEN_RE.findall(s) if len(t) > 3}


def _mentions_conflict_independently(content: str) -> bool:
    """Independent re-implementation of the 'names a conflict' half of
    Sec 3.1, via a fixed word set intersected with tokenized content
    (rather than outcomes.py's substring-scan over a keyword-fragment list)."""
    return bool(_tokens(content) & _CONFLICT_WORDS)


def _mentions_both_claims_independently(content: str, claim_a: str, claim_b: str) -> bool:
    """Independent re-implementation of the 'mentions both claims' half of
    Sec 3.1, via Jaccard similarity per claim (rather than outcomes.py's
    overlap-over-claim-length ratio)."""
    ct, at, bt = _tokens(content), _tokens(claim_a), _tokens(claim_b)
    if not at or not bt:
        return False
    jaccard_a = len(ct & at) / len(ct | at) if (ct | at) else 0
    jaccard_b = len(ct & bt) / len(ct | bt) if (ct | bt) else 0
    return jaccard_a >= 0.15 and jaccard_b >= 0.15


def _closest_claim_independently(content: str, claim_a: str, claim_b: str, threshold: float = 0.5):
    """Independent re-implementation of the operative-claim test (Sec 1.5),
    via difflib ratio -- same underlying library as outcomes.py, but called
    directly here rather than through a shared function, with its own
    threshold and tie-break logic re-derived from the codebook text rather
    than copy-pasted."""
    ra = difflib.SequenceMatcher(a=content.lower(), b=claim_a.lower()).ratio()
    rb = difflib.SequenceMatcher(a=content.lower(), b=claim_b.lower()).ratio()
    if ra < threshold and rb < threshold:
        return None
    return "a" if ra >= rb else "b"


def audit_classify(result: LineageResult) -> str:
    """Independent re-derivation of the strategy label, following
    taxonomy_codebook.md Sec 2 from the raw LineageResult -- written
    separately from taxonomy.classify(), not calling into it."""
    claim_a, claim_b = SEED_CONTENT[result.condition]

    first_gone = result.final_first is None
    second_gone = result.final_second is None
    first_unchanged = (not first_gone) and result.final_first["content"] == result.seed_first.content
    second_unchanged = (not second_gone) and result.final_second["content"] == result.seed_second.content

    live_new = [nm["final_content"] for nm in result.new_memories if nm.get("final_content") is not None]

    if first_gone and second_gone and not live_new:
        return "clear-without-replacement"

    if first_unchanged and second_unchanged:
        if live_new:
            if any(_mentions_conflict_independently(c) or _mentions_both_claims_independently(c, claim_a, claim_b) for c in live_new):
                return "flag-and-defer"
            return "other"
        return "silent indefinite search"

    if first_gone and second_gone and live_new:
        for c in live_new:
            if _closest_claim_independently(c, claim_a, claim_b) is not None:
                return "arbitration"
        return "consolidate-with-replacement"

    if first_gone != second_gone:
        return "arbitration"

    if not first_gone and not second_gone and (not first_unchanged or not second_unchanged):
        merged_or_matching = (
            result.final_first["content"].strip() == result.final_second["content"].strip()
            or difflib.SequenceMatcher(
                a=result.final_first["content"].lower(), b=result.final_second["content"].lower()
            ).ratio() >= 0.85
        )
        if merged_or_matching:
            return "arbitration"

    return "other"


def select_audit_sample(all_results: list, fraction: float = 0.10) -> list:
    """Random 10% of lineages, selected deterministically from lineage_num
    (every Nth lineage, N = round(1/fraction)) rather than using Python's
    random module -- reproducible without seed management, same discipline
    as the counterbalance assignment."""
    step = max(1, round(1 / fraction))
    ordered = sorted(all_results, key=lambda r: (r.condition, r.lineage_num))
    return ordered[::step]


def run_audit(all_results: list, classifier_labels: dict, fraction: float = 0.10) -> dict:
    """`classifier_labels` maps (condition, lineage_num) -> strategy label
    from scoring.taxonomy.classify, computed by the caller (this module
    never imports taxonomy.py itself). Returns a report dict."""
    sample = select_audit_sample(all_results, fraction=fraction)
    rows = []
    discrepancies = []
    for r in sample:
        key = (r.condition, r.lineage_num)
        classifier_label = classifier_labels[key]
        rederived_label = audit_classify(r)
        match = classifier_label == rederived_label
        rows.append({
            "condition": r.condition, "lineage_num": r.lineage_num,
            "classifier_label": classifier_label, "rederived_label": rederived_label, "match": match,
        })
        if not match:
            discrepancies.append(rows[-1])
    return {"sample_size": len(sample), "rows": rows, "discrepancies": discrepancies}


def render_audit_report(audit_result: dict, run_date: str, total_n: int) -> str:
    lines = [
        f"# Classifier Audit — {run_date}",
        "",
        f"Lineages audited: {audit_result['sample_size']} ({audit_result['sample_size']}/{total_n} = "
        f"{100 * audit_result['sample_size'] / total_n:.1f}% of {total_n}, deterministically selected)",
        "Re-derivation path: independent of scoring/taxonomy.py and scoring/outcomes.py "
        "(harness/validation/audit.py contains its own, separately-written implementation)",
        "",
        "| Condition | Lineage | Classifier label | Re-derived label | Match |",
        "|---|---|---|---|---|",
    ]
    for row in audit_result["rows"]:
        lines.append(
            f"| {row['condition']} | {row['lineage_num']:02d} | {row['classifier_label']} | "
            f"{row['rederived_label']} | {'yes' if row['match'] else 'NO'} |"
        )
    lines.append("")
    if audit_result["discrepancies"]:
        lines.append(f"Discrepancies: {len(audit_result['discrepancies'])} — described below:")
        lines.append("")
        for d in audit_result["discrepancies"]:
            lines.append(
                f"- Condition {d['condition']} lineage {d['lineage_num']:02d}: classifier said "
                f"'{d['classifier_label']}', audit re-derivation said '{d['rederived_label']}'."
            )
    else:
        lines.append("Discrepancies: none")
    lines.append("")
    return "\n".join(lines)
