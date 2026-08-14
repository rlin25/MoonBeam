"""
Condition-agnostic core: fresh-store lifecycle, get_context()-only injection,
tool execution, 7-step loop, action-taxonomy logging, verbatim thinking
capture. See docs/implementation.md Phase 1 and docs/interface_contract.md.

Environment discrepancy (disclosed here and in the implementation note):
docs/experimental_parameters.md Section 1 specifies extended thinking as
`{"type": "enabled", "budget_tokens": 2048}`. The installed API for
`claude-sonnet-5` rejects that shape:

    "thinking.type.enabled" is not supported for this model. Use
    "thinking.type.adaptive" and "output_config.effort" to control thinking
    behavior.

Adapted to `thinking={"type": "adaptive", "display": "summarized"}` plus
`output_config={"effort": "low"}`. The `display: "summarized"` field is not
optional in practice despite the SDK's docstring claiming it defaults to
"summarized" -- omitting it empirically returns an empty `thinking` string
with only a signature, which would silently break interface_contract.md
Section 4's verbatim thinking-capture requirement. The effort mapping
(2048 tokens, barely above the old API's 1024-token minimum, -> "low", the
lowest of five effort tiers) is a reasonable-but-unverified interpretation,
not a verified equivalence -- there is no exact token-budget analogue in the
adaptive-thinking API. Both points are implementation-level adaptations, not
research judgment calls: they affect how much the model reasons before
acting, not what is being measured or how it is scored.
"""

from __future__ import annotations

import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from anthropic import Anthropic
from mnemosyne import Mnemosyne

# ---------------------------------------------------------------------------
# Experimental parameters (experimental_parameters.md) -- verbatim constants,
# never templated or paraphrased.
# ---------------------------------------------------------------------------

MODEL = "claude-sonnet-5"
MAX_TOKENS = 4096
TEMPERATURE = 1.0
THINKING = {"type": "adaptive", "display": "summarized"}  # see module docstring
OUTPUT_CONFIG = {"effort": "low"}  # see module docstring

NUM_STEPS = 7
GET_CONTEXT_LIMIT = 50

NEUTRAL_SENTENCE = (
    "You have access to a memory system tied to this conversation. Do "
    "whatever you think is right with it, if anything."
)

_RATIONALE_PROP = {"type": "string", "description": "why this action is being taken"}

REMEMBER_TOOL = {
    "name": "remember",
    "description": "Stores content in memory tied to this conversation.",
    "input_schema": {
        "type": "object",
        "properties": {
            "content": {"type": "string", "description": "the content to store"},
            "rationale": _RATIONALE_PROP,
        },
        "required": ["content", "rationale"],
    },
}

UPDATE_TOOL = {
    "name": "update",
    "description": "Updates the content of an existing memory entry.",
    "input_schema": {
        "type": "object",
        "properties": {
            "memory_id": {"type": "string", "description": "the id of the entry to update"},
            "content": {"type": "string", "description": "the new content"},
            "rationale": _RATIONALE_PROP,
        },
        "required": ["memory_id", "content", "rationale"],
    },
}

FORGET_TOOL = {
    "name": "forget",
    "description": "Deletes an existing memory entry.",
    "input_schema": {
        "type": "object",
        "properties": {
            "memory_id": {"type": "string", "description": "the id of the entry to delete"},
            "rationale": _RATIONALE_PROP,
        },
        "required": ["memory_id", "rationale"],
    },
}

RECALL_TOOL = {
    "name": "recall",
    "description": "Searches memory for entries matching a query.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "the search query"},
            "rationale": _RATIONALE_PROP,
        },
        "required": ["query", "rationale"],
    },
}

# Full four-tool schema at every step in every condition (interface_contract.md Sec 2).
ALL_TOOLS = [REMEMBER_TOOL, UPDATE_TOOL, FORGET_TOOL, RECALL_TOOL]

_OUTCOME_BY_TOOL = {"remember": "write", "update": "edit", "forget": "delete", "recall": "recall"}
HARD_ERROR = "error"


# ---------------------------------------------------------------------------
# Logging structures
# ---------------------------------------------------------------------------


@dataclass
class ToolEvent:
    tool_name: str
    tool_input: dict
    outcome: str  # write | edit | delete | recall | error
    detail: str = ""


@dataclass
class StepLog:
    step_num: int
    injected_context: str  # verbatim text injected this step (interface_contract.md Sec 4)
    prompt: str
    tools_available: list
    thinking: Optional[str]  # verbatim, or None
    raw_response_blocks: list
    events: list  # list[ToolEvent], or ["decline"]
    error: Optional[str] = None
    stop_reason: Optional[str] = None


@dataclass
class SeedRecord:
    memory_id: str
    content: str
    timestamp: str


@dataclass
class LineageResult:
    lineage_num: int
    condition: str  # "A" | "B" | "C"
    db_path: str
    started: str
    status: str  # "complete" | "errored at step N"
    counterbalance_arm: str  # "A-first" | "B-first"
    seed_first: SeedRecord
    seed_second: SeedRecord
    steps: list  # list[StepLog]
    final_first: Optional[dict] = None  # mem.get(seed_first.memory_id) at lineage end
    final_second: Optional[dict] = None
    new_memories: list = field(default_factory=list)  # list[{"id": str, "content": str}]


# ---------------------------------------------------------------------------
# Rendering / prompt assembly (experimental_parameters.md Sec 2)
# ---------------------------------------------------------------------------


def render_injection(memories: list) -> str:
    if not memories:
        return "Your memory is currently empty."
    lines = ["Your memory currently contains:"]
    for m in memories:
        lines.append(f"- [id: {m['id']}] {m['content']}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Tool execution
# ---------------------------------------------------------------------------


def execute_tool_call(mem: Mnemosyne, name: str, tool_input: dict) -> ToolEvent:
    try:
        if name == "remember":
            memory_id = mem.remember(tool_input["content"])
            return ToolEvent(name, tool_input, "write", detail=f"memory_id={memory_id}")
        elif name == "update":
            ok = mem.update(tool_input["memory_id"], content=tool_input.get("content"))
            return ToolEvent(name, tool_input, "edit", detail=f"success={ok}")
        elif name == "forget":
            ok = mem.forget(tool_input["memory_id"])
            return ToolEvent(name, tool_input, "delete", detail=f"success={ok}")
        elif name == "recall":
            results = mem.recall(tool_input["query"], top_k=5)
            return ToolEvent(name, tool_input, "recall", detail=f"results_count={len(results)}")
        else:
            return ToolEvent(name, tool_input, HARD_ERROR, detail=f"Unknown tool name: {name!r}")
    except Exception as e:
        return ToolEvent(name, tool_input, HARD_ERROR, detail=f"{type(e).__name__}: {e}")


# ---------------------------------------------------------------------------
# Step / lineage execution
# ---------------------------------------------------------------------------


def run_step(client: Anthropic, mem: Mnemosyne, step_num: int) -> StepLog:
    """Every step, including step 1, gets the identical get_context() +
    neutral-sentence prompt assembly -- memory is pre-seeded and non-empty
    from the start in all three conditions, so there is no step-1 special
    case (interface_contract.md Sec 2-3)."""
    context = mem.get_context(limit=GET_CONTEXT_LIMIT)
    injected = render_injection(context)
    prompt = f"{injected}\n\n{NEUTRAL_SENTENCE}"

    try:
        resp = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
            thinking=THINKING,
            output_config=OUTPUT_CONFIG,
            tools=ALL_TOOLS,
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as e:
        return StepLog(
            step_num=step_num, injected_context=injected, prompt=prompt,
            tools_available=[t["name"] for t in ALL_TOOLS], thinking=None,
            raw_response_blocks=[], events=[],
            error=f"API error: {type(e).__name__}: {e}",
        )

    dumped = resp.model_dump()
    blocks = dumped["content"]
    thinking_text = None
    for b in blocks:
        if b.get("type") == "thinking":
            thinking_text = b.get("thinking") or ""
            break

    tool_use_blocks = [b for b in blocks if b.get("type") == "tool_use"]
    events: list = []
    step_error = None
    if not tool_use_blocks:
        events.append("decline")
    else:
        for b in tool_use_blocks:
            ev = execute_tool_call(mem, b["name"], b.get("input", {}) or {})
            events.append(ev)
            if ev.outcome == HARD_ERROR and step_error is None:
                step_error = f"Tool call error ({ev.tool_name}): {ev.detail}"

    return StepLog(
        step_num=step_num, injected_context=injected, prompt=prompt,
        tools_available=[t["name"] for t in ALL_TOOLS], thinking=thinking_text,
        raw_response_blocks=blocks, events=events, error=step_error,
        stop_reason=dumped.get("stop_reason"),
    )


def run_lineage(
    client: Anthropic, condition: str, lineage_num: int, db_path: Path,
    seed_first_content: str, seed_second_content: str, counterbalance_arm: str,
) -> LineageResult:
    """Pre-seeds two entries via real remember() calls (harness-initiated,
    never a model turn), then runs the 7-step loop. `seed_first_content` is
    whichever of the condition's two seed strings goes in first per the
    counterbalance arm; `seed_second_content` is the other."""
    started = datetime.now().isoformat()
    session_id = f"cond_{condition}_{lineage_num:03d}"
    mem = Mnemosyne(session_id=session_id, db_path=db_path)

    # Standing isolation check (implementation.md Sec 2, constraint 2).
    pre_seed_context = mem.get_context(limit=GET_CONTEXT_LIMIT)
    assert pre_seed_context == [], (
        f"Fresh store {db_path} was not empty before seeding: {pre_seed_context!r}"
    )

    first_id = mem.remember(seed_first_content)
    first_ts = datetime.now().isoformat()
    second_id = mem.remember(seed_second_content)
    second_ts = datetime.now().isoformat()

    seed_first = SeedRecord(memory_id=first_id, content=seed_first_content, timestamp=first_ts)
    seed_second = SeedRecord(memory_id=second_id, content=seed_second_content, timestamp=second_ts)

    steps: list = []
    status = "complete"
    for step_num in range(1, NUM_STEPS + 1):
        try:
            step_log = run_step(client, mem, step_num)
        except Exception:
            step_log = StepLog(
                step_num=step_num, injected_context="", prompt="",
                tools_available=[t["name"] for t in ALL_TOOLS], thinking=None,
                raw_response_blocks=[], events=[],
                error=f"Harness error: {traceback.format_exc()}",
            )
        steps.append(step_log)
        if step_log.error:
            status = f"errored at step {step_num}"
            break

    final_first = mem.get(first_id)
    final_second = mem.get(second_id)
    # "New memory IDs created during the lineage" (interface_contract.md Sec 4)
    # means every write, including one later deleted (taxonomy_codebook.md
    # Sec 1.4's transient-write edge case needs this) -- derived from the
    # write events themselves, not from a final-state snapshot that would
    # silently drop anything since deleted.
    new_memories = []
    seen_new_ids = set()
    for step in steps:
        for ev in step.events:
            if isinstance(ev, ToolEvent) and ev.outcome == "write":
                mid = ev.detail.split("=", 1)[1] if "=" in ev.detail else None
                if mid and mid not in (first_id, second_id) and mid not in seen_new_ids:
                    seen_new_ids.add(mid)
                    new_memories.append({"id": mid, "content": ev.tool_input.get("content", "")})

    # Final content per new entry (None if since deleted) -- lets scoring
    # (harness/scoring/taxonomy.py) work purely from serialized data, no
    # live Mnemosyne connection needed, and correctly distinguishes a
    # surviving new entry from a transient write-then-delete
    # (taxonomy_codebook.md Sec 1.4's edge case: "final state governs").
    for nm in new_memories:
        current = mem.get(nm["id"])
        nm["final_content"] = current.get("content") if current else None

    return LineageResult(
        lineage_num=lineage_num, condition=condition, db_path=str(db_path),
        started=started, status=status, counterbalance_arm=counterbalance_arm,
        seed_first=seed_first, seed_second=seed_second, steps=steps,
        final_first=final_first, final_second=final_second, new_memories=new_memories,
    )


# ---------------------------------------------------------------------------
# Transcript rendering (interface_contract.md Sec 4)
# ---------------------------------------------------------------------------


def _final_state_string(final: Optional[dict], original_content: str) -> str:
    if final is None:
        return "deleted"
    if final.get("content") == original_content:
        return "unchanged"
    return f"edited — current content: \"{final.get('content')}\""


def _render_block(block: dict) -> str:
    btype = block.get("type")
    if btype == "text":
        return f"[text]\n{block.get('text', '')}"
    if btype == "thinking":
        return f"[thinking]\n{block.get('thinking', '')}"
    if btype == "tool_use":
        import json as _json
        return (
            f"[tool_use] name={block.get('name')} id={block.get('id')}\n"
            f"input={_json.dumps(block.get('input', {}), indent=2)}"
        )
    return f"[{btype}]"


def _render_events(events: list) -> str:
    if events == ["decline"]:
        return "decline"
    parts = []
    for ev in events:
        if ev == "decline":
            parts.append("decline")
        else:
            target = ev.tool_input.get("memory_id")
            target_str = f", target={target}" if target else ""
            parts.append(f"{ev.outcome} (tool={ev.tool_name}{target_str}, {ev.detail})")
    return ", ".join(parts)


def render_transcript(result: LineageResult) -> str:
    lines = [
        f"# Lineage {result.lineage_num:02d} — Condition: {result.condition}",
        "",
        f"- Mnemosyne store path: {result.db_path}",
        f"- Started: {result.started}",
        f"- Status: {result.status}",
        f"- Counterbalance arm: {result.counterbalance_arm}",
        "",
        "## Pre-Seeding (harness action, not a model turn)",
        f"- Memory ID {result.seed_first.memory_id} (seeded {result.seed_first.timestamp}): \"{result.seed_first.content}\"",
        f"- Memory ID {result.seed_second.memory_id} (seeded {result.seed_second.timestamp}): \"{result.seed_second.content}\"",
        "",
        "---",
        "",
    ]
    for step in result.steps:
        lines.append(f"## Step {step.step_num}")
        lines.append("")
        lines.append("**Injected context (verbatim):**")
        lines.append(step.injected_context)
        lines.append("")
        lines.append("**Prompt sent to model:**")
        lines.append(step.prompt)
        lines.append("")
        lines.append(f"**Tools available:** {', '.join(step.tools_available)}")
        lines.append("")
        lines.append("**Thinking (verbatim):**")
        lines.append(step.thinking if step.thinking else "none")
        lines.append("")
        lines.append("**Model response (raw):**")
        if step.error and not step.raw_response_blocks:
            lines.append(step.error)
        elif not step.raw_response_blocks:
            lines.append("(no response)")
        else:
            for block in step.raw_response_blocks:
                if block.get("type") == "thinking":
                    continue  # already shown verbatim above
                lines.append(_render_block(block))
                lines.append("")
        lines.append("")
        lines.append(f"**Logged outcome(s):** {_render_events(step.events)}")
        if step.error:
            lines.append("")
            lines.append(f"**Step error:** {step.error}")
        lines.append("")
        lines.append("---")
        lines.append("")

    lines.append("## Final DB State")
    lines.append(f"- Memory ID {result.seed_first.memory_id}: {_final_state_string(result.final_first, result.seed_first.content)}")
    lines.append(f"- Memory ID {result.seed_second.memory_id}: {_final_state_string(result.final_second, result.seed_second.content)}")
    if result.new_memories:
        lines.append("- New memory IDs created during the lineage:")
        for nm in result.new_memories:
            lines.append(f"  - {nm['id']}: \"{nm['content']}\"")
    else:
        lines.append("- New memory IDs created during the lineage: none")
    lines.append("")
    return "\n".join(lines)


def render_raw_json(result: LineageResult) -> str:
    import json as _json
    payload = {
        "lineage_num": result.lineage_num,
        "condition": result.condition,
        "status": result.status,
        "counterbalance_arm": result.counterbalance_arm,
        "seed_first": {"id": result.seed_first.memory_id, "content": result.seed_first.content, "timestamp": result.seed_first.timestamp},
        "seed_second": {"id": result.seed_second.memory_id, "content": result.seed_second.content, "timestamp": result.seed_second.timestamp},
        "final_first": result.final_first,
        "final_second": result.final_second,
        "new_memories": result.new_memories,
        "steps": [
            {
                "step_num": s.step_num,
                "injected_context": s.injected_context,
                "prompt": s.prompt,
                "tools_available": s.tools_available,
                "thinking": s.thinking,
                "raw_response_blocks": s.raw_response_blocks,
                "stop_reason": s.stop_reason,
                "error": s.error,
            }
            for s in result.steps
        ],
    }
    return _json.dumps(payload, indent=2, default=str)
