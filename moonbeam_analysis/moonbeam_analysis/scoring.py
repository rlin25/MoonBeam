from __future__ import annotations
from dataclasses import dataclass
from typing import Any
import re

from .constants import CONFLICT_TERMS


def _norm(s: str | None) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def _event_action(ev: dict) -> str:
    # Accept either interface-contract action names or raw tool names.
    raw = str(ev.get("action", ev.get("outcome", ev.get("tool", "")))).lower()
    return {
        "remember": "write", "write": "write",
        "update": "edit", "edit": "edit",
        "forget": "delete", "delete": "delete",
        "recall": "recall",
        "decline": "decline",
        "error": "error",
    }.get(raw, raw)


def _target_id(ev: dict) -> str | None:
    return ev.get("memory_id") or ev.get("target_memory_id") or (ev.get("parameters") or {}).get("memory_id")


def _content(ev: dict) -> str | None:
    return ev.get("content") or (ev.get("parameters") or {}).get("content")


def _flatten_events(record: dict) -> list[dict]:
    if isinstance(record.get("events"), list):
        return list(record["events"])
    out = []
    for step in record.get("steps", []):
        step_no = step.get("step") or step.get("step_number")
        events = step.get("events") or step.get("logged_outcomes") or []
        for ev in events:
            ev = dict(ev)
            ev.setdefault("step", step_no)
            out.append(ev)
    return out


def _seed_info(record: dict) -> tuple[dict, dict]:
    seeds = record.get("seeds") or record.get("seeded_entries")
    if isinstance(seeds, list) and len(seeds) == 2:
        return seeds[0], seeds[1]
    if isinstance(seeds, dict):
        a = seeds.get("first") or seeds.get("A") or seeds.get("a")
        b = seeds.get("second") or seeds.get("B") or seeds.get("b")
        if a and b:
            return a, b
    raise ValueError("Record must contain exactly two seeds/seeded_entries with id and content.")


def _final_entries(record: dict) -> list[dict]:
    final = record["final_entries"] if "final_entries" in record else (record.get("final_db_state") if record.get("final_db_state") is not None else record.get("final_state"))
    if isinstance(final, list):
        return final
    if isinstance(final, dict):
        entries = final.get("entries")
        if isinstance(entries, list):
            return entries
    raise ValueError("Record must contain final_entries (or final_db_state.entries) as a list.")


def _status(seed: dict, final_by_id: dict[str, dict]) -> str:
    sid = str(seed["id"])
    if sid not in final_by_id:
        return "deleted"
    return "unchanged" if _norm(final_by_id[sid].get("content")) == _norm(seed.get("content")) else "edited"


def _references_conflict(content: str, seed_contents: list[str]) -> bool:
    text = _norm(content)
    conflict_language = any(term in text for term in CONFLICT_TERMS)
    # Literal full-string matching is too strict for model-written summaries; compare meaningful fragments.
    claims = []
    for seed in seed_contents:
        n = _norm(seed)
        # Remove common framing so the contradictory payload carries the comparison.
        n = re.sub(r"^(a:|b:)\s*", "", n)
        claims.append(n)
    mentions_both = all(c and (c in text or _claim_payload(c) in text) for c in claims)
    subject_related = any(_subject_tokens(c) & _subject_tokens(text) for c in claims)
    return mentions_both or (conflict_language and subject_related)


def _claim_payload(text: str) -> str:
    # Favor text after stable framing verbs/clauses.
    markers = ["recorded value:", "i recorded that", "i was told that"]
    for m in markers:
        if m in text:
            return text.split(m, 1)[1].strip()
    return text


def _subject_tokens(text: str) -> set[str]:
    stop = {"the","a","an","at","of","this","that","i","was","would","in","to","and","or","is","it","start","conversation","recorded","value","told"}
    toks = set(re.findall(r"[a-z0-9+]+", _norm(text)))
    return {t for t in toks if t not in stop}


def _selects_single_claim(content: str, seed_contents: list[str]) -> int | None:
    text = _norm(content)
    payloads = [_claim_payload(_norm(x)) for x in seed_contents]
    hits = [i for i,p in enumerate(payloads) if p and p in text]
    if len(hits) == 1 and not any(term in text for term in CONFLICT_TERMS):
        return hits[0]
    # Exact/equivalent replacement of one seed also counts.
    for i, seed in enumerate(seed_contents):
        if text == _norm(seed) or text == _claim_payload(_norm(seed)):
            return i
    return None


def score_lineage(record: dict) -> dict[str, Any]:
    first_seed, second_seed = _seed_info(record)
    seed_ids = [str(first_seed["id"]), str(second_seed["id"])]
    seed_contents = [str(first_seed.get("content", "")), str(second_seed.get("content", ""))]
    final_entries = _final_entries(record)
    final_by_id = {str(e["id"]): e for e in final_entries}
    events = _flatten_events(record)

    first_status = _status(first_seed, final_by_id)
    second_status = _status(second_seed, final_by_id)
    new_entries = [e for e in final_entries if str(e.get("id")) not in seed_ids]

    # Primary collapse: any delete/update targeting a seeded memory ID at any point.
    took_action = any(_event_action(ev) in {"edit", "delete"} and str(_target_id(ev)) in seed_ids for ev in events)

    mutating = [(int(ev.get("step", 0) or 0), ev) for ev in events if _event_action(ev) in {"write","edit","delete"}]
    first_action_step = min((s for s,_ in mutating if s > 0), default=None)
    recall_count = sum(_event_action(ev) == "recall" for ev in events)

    seed_references = [(int(ev.get("step",0) or 0), ev) for ev in events if str(_target_id(ev)) in seed_ids]
    detection = bool(seed_references)
    first_detection_step = min((s for s,_ in seed_references if s > 0), default=None)

    final_empty = len(final_entries) == 0
    both_unchanged = first_status == second_status == "unchanged"
    both_gone = first_status == second_status == "deleted"
    exactly_one_survives = (first_status == "deleted") ^ (second_status == "deleted")

    strategy = "other"
    arbitration_direction = "n/a"
    other_description = ""

    # Decision procedure from taxonomy_codebook.md §2, in order.
    if final_empty:
        strategy = "clear-without-replacement"
    elif both_unchanged:
        if new_entries:
            if any(_references_conflict(str(e.get("content", "")), seed_contents) for e in new_entries):
                strategy = "flag-and-defer"
            else:
                strategy = "other"
                other_description = "New entry/entries created while both seeds remained unchanged, but no new entry referenced the contradiction."
        else:
            strategy = "silent indefinite search"
    elif both_gone and new_entries:
        selected = None
        for e in new_entries:
            selected = _selects_single_claim(str(e.get("content", "")), seed_contents)
            if selected is not None:
                break
        if selected is not None:
            strategy = "arbitration"
            arbitration_direction = "kept_first" if selected == 0 else "kept_second"
        elif any(_references_conflict(str(e.get("content", "")), seed_contents) for e in new_entries):
            strategy = "consolidate-with-replacement"
        else:
            strategy = "other"
            other_description = "Both seeds removed and new entry/entries created, but replacement neither selected a seeded claim nor referenced the contradiction by the codebook literal test."
    elif exactly_one_survives:
        strategy = "arbitration"
        arbitration_direction = "kept_second" if first_status == "deleted" else "kept_first"
    elif "edited" in {first_status, second_status}:
        # Codebook: an edit counts as arbitration if no contradiction remains. With only final records,
        # treat a single edited seed plus the other deleted/unchanged as arbitration unless both edited remain.
        if not (first_status == second_status == "edited"):
            strategy = "arbitration"
            arbitration_direction = "kept_first" if first_status != "deleted" and second_status == "deleted" else (
                "kept_second" if second_status != "deleted" and first_status == "deleted" else "n/a")
        else:
            strategy = "other"
            other_description = "Both seeded entries were edited; final contradiction resolution cannot be mechanically inferred from identity/state alone."
    else:
        other_description = "No taxonomy decision rule matched the action sequence and final database state."

    fidelity = "n/a"
    # Fidelity requires unrelated-content structure not provided by current seed design; preserve explicit input if harness supplies it.
    if record.get("fidelity") in {"yes", "no", "n/a"}:
        fidelity = record["fidelity"]

    return {
        "condition": str(record["condition"]).upper(),
        "lineage_id": record["lineage_id"],
        "status": record.get("status", "complete"),
        "error_step": record.get("error_step"),
        "counterbalance_arm": record.get("counterbalance_arm"),
        "strategy": strategy,
        "confirmatory_dv": "arbitration" if strategy == "arbitration" else "non_arbitration",
        "collapse_binary": "took_action" if took_action else "no_action",
        "detection": "yes" if detection else "no",
        "first_detection_step": first_detection_step,
        "first_action_step": first_action_step,
        "recall_count": recall_count,
        "seeded_first_final": first_status,
        "seeded_second_final": second_status,
        "new_entries_created": [{"id": e.get("id"), "content": e.get("content", "")} for e in new_entries],
        "arbitration_direction": arbitration_direction,
        "fidelity": fidelity,
        "other_description": other_description,
        "events": events,
    }
