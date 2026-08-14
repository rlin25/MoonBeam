"""
Held-out human coding subsample. Prepares 12 lineages (4 per condition,
deterministically selected) with classifier labels withheld, per
interface_contract.md Sec 7.1 and taxonomy_codebook.md Sec 6. Computes
Cohen's kappa once human labels are returned.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from harness.core import LineageResult, _final_state_string
from harness.scoring.taxonomy import STRATEGIES


def select_stratified_sample(results_by_condition: dict, n_per_condition: int = 4) -> dict:
    """Deterministic selection: the first n_per_condition lineages by
    lineage_num within each condition. Reproducible, no randomness needed --
    which lineages are sampled has no bearing on what label they'll receive,
    so an arbitrary deterministic rule is as good as a random one and is
    easier to audit."""
    sample = {}
    for cond, results in results_by_condition.items():
        ordered = sorted(results, key=lambda r: r.lineage_num)
        sample[cond] = ordered[:n_per_condition]
    return sample


def _codebook_hash(codebook_path: Path) -> str:
    return hashlib.sha256(codebook_path.read_bytes()).hexdigest()[:12]


def _action_log_line(step_num: int, ev) -> str:
    if ev == "decline":
        return f"- Step {step_num}: decline"
    parts = []
    if ev.tool_input.get("memory_id"):
        parts.append(f"target={ev.tool_input['memory_id']}")
    if ev.tool_input.get("content"):
        parts.append(f"content={ev.tool_input['content']!r}")
    if ev.tool_input.get("query"):
        parts.append(f"query={ev.tool_input['query']!r}")
    return f"- Step {step_num}: {ev.tool_name} ({', '.join(parts)})"


def render_held_out_artifact(sample: dict, codebook_path: Path, coder: str, run_date: str) -> str:
    total = sum(len(v) for v in sample.values())
    breakdown = ", ".join(f"{len(sample.get(c, []))} from {c}" for c in ("A", "B", "C"))
    lines = [
        f"# Held-Out Coding Subsample — {run_date}",
        "",
        f"Lineages sampled: {total}, stratified across Conditions A, B, C ({breakdown})",
        f"Codebook version: {_codebook_hash(codebook_path)}",
        f"Coder: {coder}",
        "",
    ]
    for cond in ("A", "B", "C"):
        for r in sample.get(cond, []):
            lines.append(f"## Lineage {r.lineage_num:02d} (Condition {cond})")
            lines.append("")
            lines.append(f"- Counterbalance arm: {r.counterbalance_arm}")
            lines.append("")
            lines.append("**Pre-seeding:**")
            lines.append(f"- Memory ID {r.seed_first.memory_id}: \"{r.seed_first.content}\"")
            lines.append(f"- Memory ID {r.seed_second.memory_id}: \"{r.seed_second.content}\"")
            lines.append("")
            lines.append("**Full action log (tool name, target memory ID, parameters):**")
            for step in r.steps:
                for ev in step.events:
                    lines.append(_action_log_line(step.step_num, ev))
            lines.append("")
            lines.append("**Final database state:**")
            lines.append(f"- Memory ID {r.seed_first.memory_id}: {_final_state_string(r.final_first, r.seed_first.content)}")
            lines.append(f"- Memory ID {r.seed_second.memory_id}: {_final_state_string(r.final_second, r.seed_second.content)}")
            if r.new_memories:
                for nm in r.new_memories:
                    status = "deleted" if nm.get("final_content") is None else repr(nm["final_content"])
                    lines.append(f"- New entry {nm['id']}: {status}")
            else:
                lines.append("- New entries: none")
            lines.append("")
            lines.append(f"Human label: ______________________  (one of: {', '.join(STRATEGIES)})")
            lines.append("")
            lines.append("---")
            lines.append("")
    return "\n".join(lines)


def cohens_kappa(human_labels: list, classifier_labels: list, categories=None) -> float:
    """Standard unweighted Cohen's kappa for two raters over the same N items."""
    assert len(human_labels) == len(classifier_labels), "label lists must be the same length"
    n = len(human_labels)
    categories = categories or sorted(set(human_labels) | set(classifier_labels))
    idx = {c: i for i, c in enumerate(categories)}
    k = len(categories)
    matrix = [[0] * k for _ in range(k)]
    for h, c in zip(human_labels, classifier_labels):
        matrix[idx[h]][idx[c]] += 1
    po = sum(matrix[i][i] for i in range(k)) / n
    row_totals = [sum(matrix[i]) for i in range(k)]
    col_totals = [sum(matrix[i][j] for i in range(k)) for j in range(k)]
    pe = sum(row_totals[i] * col_totals[i] for i in range(k)) / (n * n)
    if pe == 1:
        return 1.0
    return (po - pe) / (1 - pe)
