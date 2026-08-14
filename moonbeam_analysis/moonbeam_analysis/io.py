from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Any, Iterable


def load_json(path: str | Path) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _json_safe(obj: Any) -> Any:
    import math
    if isinstance(obj, float) and not math.isfinite(obj):
        return None
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_safe(v) for v in obj]
    return obj

def dump_json(obj: Any, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(_json_safe(obj), f, indent=2, ensure_ascii=False, allow_nan=False)


def iter_lineage_json(root: str | Path) -> Iterable[tuple[Path, dict]]:
    root = Path(root)
    for path in sorted(root.rglob("*.json")):
        data = load_json(path)
        if isinstance(data, dict) and "lineage_id" in data and "condition" in data:
            yield path, data


def _infer_condition(path: Path, explicit_condition: str | None = None) -> str | None:
    if explicit_condition:
        c = explicit_condition.upper()
        if c in {"A", "B", "C"}:
            return c
    for part in reversed(path.parts):
        p = part.lower().replace("-", "_")
        m = re.fullmatch(r"condition_?([abc])", p)
        if m:
            return m.group(1).upper()
        if p in {"a", "b", "c"}:
            return p.upper()
    return None


def _value(text: str, label: str) -> str | None:
    # Match one Markdown bullet line with a literal label, case-insensitive.
    m = re.search(rf"(?mi)^\s*-\s*{re.escape(label)}\s*:\s*(.*?)\s*$", text)
    return m.group(1).strip() if m else None


def _parse_step(value: str | None) -> int | None:
    if not value or value.lower() in {"n/a", "na", "none", "null", "—", "-"}:
        return None
    m = re.search(r"\d+", value)
    return int(m.group()) if m else None


def _parse_boolish(value: str | None) -> str | None:
    if value is None:
        return None
    v = value.strip().lower()
    if v.startswith("yes"): return "yes"
    if v.startswith("no"): return "no"
    return value.strip()


def _parse_new_entries(value: str | None) -> list[dict]:
    if value is None or value.strip().lower() in {"none", "n/a", "na", ""}:
        return []
    # The scored Markdown may contain free text rather than stable IDs. Preserve it verbatim.
    return [{"id": "reported", "content": value.strip()}]


def _normalize_collapse_binary(reported: str, first_state: str | None, second_state: str | None) -> tuple[str, str]:
    """Normalize the preregistered action binary used by Richard's harness.

    Current MoonBeam emits only ``took_action`` / ``no_action``.  Older or
    hand-produced scoring summaries may contain strategy-like values such as
    ``arbitration`` / ``non_arbitration`` in this field.  Those must never be
    interpreted as the action binary.  For such legacy values, derive action
    mechanically from the seeded final states: edited/deleted => took_action;
    both unchanged => no_action.  If the states are insufficient, fail loudly.
    """
    value = (reported or "").strip().lower()
    if value in {"took_action", "no_action"}:
        return value, "reported"

    states = {(first_state or "").strip().lower(), (second_state or "").strip().lower()}
    if states & {"edited", "deleted"}:
        return "took_action", f"derived_from_seed_states (reported={value or 'missing'})"
    if states <= {"unchanged", ""} and "unchanged" in states:
        return "no_action", f"derived_from_seed_states (reported={value or 'missing'})"
    raise ValueError(
        f"Unrecognized collapse binary {reported!r} and insufficient seeded states "
        f"to derive the preregistered action binary"
    )


def parse_scored_markdown(path: str | Path, explicit_condition: str | None = None) -> dict:
    """Parse Richard's per-lineage scored Markdown into the fields used by Treylon's analysis.

    This parser intentionally does not invent the raw action log. Fields unavailable in the scored
    Markdown are represented as empty/None so downstream reports can label them unavailable.
    """
    path = Path(path)
    text = path.read_text(encoding="utf-8")

    m = re.search(r"(?mi)^##\s*Scoring\s*[—-]\s*Lineage\s*0*(\d+)\s*$", text)
    if not m:
        # fall back to filename such as lineage_001.md
        m = re.search(r"lineage[_-]?0*(\d+)", path.stem, re.I)
    if not m:
        raise ValueError(f"Could not determine lineage id from {path}")
    lineage_id = int(m.group(1))

    condition = _infer_condition(path, explicit_condition)
    strategy = _value(text, "Strategy (per taxonomy_codebook.md §2)") or _value(text, "Strategy")
    collapse_reported = _value(text, "Collapse binary (per preregistration.md §3)") or _value(text, "Collapse binary")
    if not strategy or not collapse_reported:
        raise ValueError(f"Missing Strategy or Collapse binary in {path}")

    first_state = _value(text, "Seeded entry (first)")
    second_state = _value(text, "Seeded entry (second)")
    collapse, collapse_source = _normalize_collapse_binary(collapse_reported, first_state, second_state)
    new_entries = _parse_new_entries(_value(text, "New entries created"))

    # Counterbalance is preregistered deterministically: even index A-first; odd B-first.
    arm = "A-first" if lineage_id % 2 == 0 else "B-first"

    return {
        "source_path": str(path),
        "source_format": "scored_markdown",
        "condition": condition,
        "lineage_id": lineage_id,
        "counterbalance_arm": arm,
        "strategy": strategy.strip().lower(),
        "confirmatory_dv": "arbitration" if strategy.strip().lower() == "arbitration" else "non_arbitration",
        "collapse_binary": collapse,
        "collapse_binary_reported": collapse_reported.strip().lower(),
        "collapse_binary_source": collapse_source,
        "detection": (lambda m: m.group(1).lower() if m else _parse_boolish(_value(text, "Detection")))(re.search(r"(?mi)^\s*-\s*Detection:\s*did any tool call reference a seeded memory ID\?\s*(yes|no)\s*$", text)),
        "first_detection_step": _parse_step(_value(text, "If yes, first at step")),
        "first_action_step": _parse_step(_value(text, "First action step (first write/update/delete)")),
        "recall_count": int((_value(text, "Recall count") or "0").strip()),
        "seeded_first_final": (first_state or "unknown").strip().lower(),
        "seeded_second_final": (second_state or "unknown").strip().lower(),
        "new_entries_created": new_entries,
        "arbitration_direction": (lambda m: m.group(1).strip() if m else "n/a")(re.search(r"(?mi)^\s*-\s*If arbitration:\s*which entry was kept\?\s*(.*?)\s*$", text)),
        "fidelity": (_value(text, "Fidelity, where an edit or consolidation occurred") or "n/a").strip(),
        "other_description": (_value(text, "Other description") or "").strip(),
        "status": "complete",
        "error_step": None,
        "events": [],
        "raw_events_available": False,
    }


def iter_lineage_markdown(root: str | Path, explicit_condition: str | None = None) -> Iterable[tuple[Path, dict]]:
    root = Path(root)
    # Richard's actual MoonBeam layout stores scored summaries under
    # runs/condition_*/scoring/. Prefer those files so transcript Markdown is
    # never mistaken for primary scoring input. Fall back to a recursive scan
    # for standalone/scoped folders supplied by the user.
    scoring_paths = sorted(root.glob("condition_*/scoring/lineage_*.md"))
    paths = scoring_paths if scoring_paths else sorted(root.rglob("lineage_*.md"))
    seen: set[tuple[str, int]] = set()
    for path in paths:
        try:
            rec = parse_scored_markdown(path, explicit_condition=explicit_condition)
        except ValueError:
            continue
        if rec.get("condition") is not None:
            key = (rec["condition"], int(rec["lineage_id"]))
            if key in seen:
                continue
            seen.add(key)
            yield path, rec
