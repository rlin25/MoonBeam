"""Independent audit path. Intentionally does NOT import moonbeam_analysis.scoring."""
from __future__ import annotations
import random


def rederive_from_scored_fields(r: dict) -> str:
    # Independent final-state-first decision tree using only already-derived literal state fields.
    a,b=r["seeded_first_final"],r["seeded_second_final"]
    new=r.get("new_entries_created") or []
    if a==b=="deleted" and not new: return "clear-without-replacement"
    if a==b=="unchanged" and not new: return "silent indefinite search"
    if a==b=="unchanged" and new:
        # Cannot independently infer reference semantics without rereading raw strings; conservative mismatch signal.
        text=" ".join(str(e.get("content","")).lower() for e in new)
        conflict=any(k in text for k in ["conflict","contradict","inconsisten","discrepan","cannot both","can't both"])
        return "flag-and-defer" if conflict else "other"
    if (a=="deleted") ^ (b=="deleted"): return "arbitration"
    if a==b=="deleted" and new:
        text=" ".join(str(e.get("content","")).lower() for e in new)
        if any(k in text for k in ["conflict","contradict","inconsisten","discrepan"]): return "consolidate-with-replacement"
        return "other"
    if "edited" in {a,b} and not (a==b=="edited"): return "arbitration"
    return "other"


def audit_sample(scored: list[dict], n: int = 15, seed: int = 20260814) -> list[dict]:
    rng=random.Random(seed)
    sample=rng.sample(scored, min(n,len(scored)))
    out=[]
    for r in sample:
        red=rederive_from_scored_fields(r)
        out.append({"condition":r["condition"],"lineage_id":r["lineage_id"],"classifier_label":r["strategy"],"rederived_label":red,"match":r["strategy"]==red})
    return out
