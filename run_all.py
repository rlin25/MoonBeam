"""
Entry point (implementation.md Sec 3). Runs Condition A to N=50 first, then
B, then C -- concurrent within a condition, sequential between conditions
per preregistration.md Sec 9's sequencing. Then mechanical scoring, the
validation layer, per-condition observations.md, and the achieved-power
recomputation. Writes everything under runs/ per interface_contract.md
Sec 8.
"""

from __future__ import annotations

import sys
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

from anthropic import Anthropic

from harness.core import LineageResult, StepLog, render_transcript, render_raw_json
from harness.conditions import run_condition_lineage
from harness.scoring.taxonomy import classify, STRATEGIES
from harness.validation.held_out import select_stratified_sample, render_held_out_artifact
from harness.validation.audit import select_audit_sample, run_audit, render_audit_report
from harness import stats as st

N_PER_CONDITION = 50
MAX_WORKERS = 20
CONDITIONS_IN_ORDER = ["A", "B", "C"]

ROOT = Path(__file__).resolve().parent
RUNS_DIR = ROOT / "runs"
DOCS_DIR = ROOT / "docs"

CONDITION_DIR_NAME = {"A": "condition_a", "B": "condition_b", "C": "condition_c"}


def log(msg: str):
    print(msg, file=sys.stderr, flush=True)


def run_condition_batch(client: Anthropic, condition: str, n: int, dbs_dir: Path) -> list:
    results: list = [None] * n

    def _run_one(i):
        db_path = dbs_dir / f"lineage_{i:03d}.db"
        try:
            return i, run_condition_lineage(client, condition, i, db_path)
        except Exception:
            tb = traceback.format_exc()
            log(f"[run_all] Condition {condition} lineage {i:03d} crashed: {tb}")
            from harness.core import SeedRecord
            return i, LineageResult(
                lineage_num=i, condition=condition, db_path=str(db_path),
                started=datetime.now().isoformat(), status="errored at step 1",
                counterbalance_arm="A-first" if i % 2 == 0 else "B-first",
                seed_first=SeedRecord("", "", ""), seed_second=SeedRecord("", "", ""),
                steps=[StepLog(1, "", "", [], None, [], [], error=f"Harness crash: {tb}")],
            )

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = [pool.submit(_run_one, i) for i in range(1, n + 1)]
        done = 0
        for fut in as_completed(futures):
            i, result = fut.result()
            results[i - 1] = result
            done += 1
            if done % 10 == 0 or done == n:
                log(f"[run_all] Condition {condition}: {done}/{n} lineages complete")
    return results


def assert_counterbalance_balanced(results: list, condition: str):
    a_first = sum(1 for r in results if r.counterbalance_arm == "A-first")
    b_first = sum(1 for r in results if r.counterbalance_arm == "B-first")
    assert a_first == 25 and b_first == 25, (
        f"Condition {condition}: counterbalance arms not exactly 25/25 (A-first={a_first}, B-first={b_first})"
    )
    log(f"[run_all] Condition {condition}: counterbalance arms confirmed 25/25")


def render_scoring_block(result: LineageResult, score) -> str:
    lines = [
        f"## Scoring — Lineage {result.lineage_num:02d}",
        "",
        f"- Strategy (per taxonomy_codebook.md §2): {score.strategy}",
        f"- Collapse binary (per preregistration.md §3): {score.collapse_binary}",
        f"- Detection: did any tool call reference a seeded memory ID? {'yes' if score.detection else 'no'}",
    ]
    if score.detection:
        lines.append(f"- If yes, first at step: {score.detection_step}")
    lines.append(f"- First action step (first write/update/delete): {score.first_action_step if score.first_action_step is not None else 'null'}")
    lines.append(f"- Recall count: {score.recall_count}")
    lines.append(f"- Seeded entry (first): {score.seeded_first_final}")
    lines.append(f"- Seeded entry (second): {score.seeded_second_final}")
    if score.new_entries:
        lines.append("- New entries created:")
        for nm in score.new_entries:
            status = "deleted" if nm.get("final_content") is None else nm["final_content"]
            lines.append(f"  - {nm['id']}: {status!r}")
    else:
        lines.append("- New entries created: none")
    if score.strategy == "arbitration":
        lines.append(f"- If arbitration: which entry was kept? {score.arbitration_direction}")
    lines.append(f"- Fidelity, where an edit or consolidation occurred: {score.fidelity}")
    if score.strategy == "other":
        lines.append(f"- Other description: {score.other_description}")
    lines.append("")
    return "\n".join(lines)


def render_observations(condition: str, results: list, scores: dict, run_date: str) -> str:
    completed = [r for r in results if r.status == "complete"]
    errored = [r for r in results if r.status != "complete"]

    outcome_cols = ("write", "edit", "delete", "recall", "decline", "error")
    by_step = {n: {c: 0 for c in outcome_cols} for n in range(1, 8)}
    pooled = {c: 0 for c in outcome_cols}
    malformed = []

    for r in results:
        for step in r.steps:
            if step.events == ["decline"]:
                by_step[step.step_num]["decline"] += 1
                pooled["decline"] += 1
            elif not step.events:
                by_step[step.step_num]["error"] += 1
                pooled["error"] += 1
            else:
                for ev in step.events:
                    if hasattr(ev, "outcome"):
                        by_step[step.step_num][ev.outcome] += 1
                        pooled[ev.outcome] += 1
                        if ev.outcome == "error":
                            malformed.append(ev.detail)

    strategy_counts = {s: 0 for s in STRATEGIES}
    strategy_collapse = {s: {"took_action": 0, "no_action": 0} for s in STRATEGIES}
    for r in completed:
        sc = scores[(condition, r.lineage_num)]
        strategy_counts[sc.strategy] += 1
        strategy_collapse[sc.strategy][sc.collapse_binary] += 1

    arm_stats = {}
    for arm in ("A-first", "B-first"):
        arm_results = [r for r in completed if r.counterbalance_arm == arm]
        dist = {}
        for r in arm_results:
            sc = scores[(condition, r.lineage_num)]
            dist[sc.strategy] = dist.get(sc.strategy, 0) + 1
        took = sum(1 for r in arm_results if scores[(condition, r.lineage_num)].collapse_binary == "took_action")
        no_action = len(arm_results) - took
        arm_stats[arm] = {"n": len(arm_results), "dist": dist, "took_action": took, "no_action": no_action}

    both_unchanged = sum(1 for r in completed if scores[(condition, r.lineage_num)].seeded_first_final == "unchanged" and scores[(condition, r.lineage_num)].seeded_second_final == "unchanged")
    one_deleted = sum(1 for r in completed if [scores[(condition, r.lineage_num)].seeded_first_final, scores[(condition, r.lineage_num)].seeded_second_final].count("deleted") == 1)
    both_deleted = sum(1 for r in completed if scores[(condition, r.lineage_num)].seeded_first_final == "deleted" and scores[(condition, r.lineage_num)].seeded_second_final == "deleted")
    one_or_both_edited = sum(1 for r in completed if "edited" in (scores[(condition, r.lineage_num)].seeded_first_final, scores[(condition, r.lineage_num)].seeded_second_final))
    new_entries_created = sum(1 for r in completed if r.new_memories)

    errored_list = ", ".join(f"lineage {r.lineage_num:03d}: {r.status}" for r in errored) or "none"

    lines = [
        f"# Observations — Condition {condition}",
        "",
        f"Run date: {run_date}",
        f"Lineages attempted: {len(results)}",
        f"Completed without error: {len(completed)}",
        f"Errored (and at which step): {errored_list}",
        "",
        "## Action taxonomy by step position",
        "| Step | write | edit | delete | recall | decline | error |",
        "|------|-------|------|--------|--------|---------|-------|",
    ]
    for n in range(1, 8):
        c = by_step[n]
        lines.append(f"| {n} | {c['write']} | {c['edit']} | {c['delete']} | {c['recall']} | {c['decline']} | {c['error']} |")
    lines += [
        "",
        "## Pooled totals",
        "| write | edit | delete | recall | decline | error |",
        "|-------|------|--------|--------|---------|-------|",
        f"| {pooled['write']} | {pooled['edit']} | {pooled['delete']} | {pooled['recall']} | {pooled['decline']} | {pooled['error']} |",
        "",
        "## Strategy distribution",
        "| Strategy | Count | took_action | no_action |",
        "|---|---|---|---|",
    ]
    for s in STRATEGIES:
        lines.append(f"| {s} | {strategy_counts[s]} | {strategy_collapse[s]['took_action']} | {strategy_collapse[s]['no_action']} |")
    lines += [
        "",
        "## By counterbalance arm",
        "| Arm | N | Strategy distribution | took_action | no_action |",
        "|---|---|---|---|---|",
    ]
    for arm, d in arm_stats.items():
        dist_str = ", ".join(f"{k}: {v}" for k, v in d["dist"].items()) or "none"
        lines.append(f"| {arm} | {d['n']} | {dist_str} | {d['took_action']} | {d['no_action']} |")
    lines += [
        "",
        "## Final DB state",
        "| Outcome | Count |",
        "|---|---|",
        f"| Both entries unchanged | {both_unchanged} |",
        f"| One entry deleted | {one_deleted} |",
        f"| Both entries deleted | {both_deleted} |",
        f"| One or both edited | {one_or_both_edited} |",
        f"| New entries created | {new_entries_created} |",
        "",
        "## Malformed / errored tool calls",
        f"- Total: {len(malformed)}",
        f"- Error types encountered, by literal message: {malformed if malformed else 'none'}",
        "",
    ]
    return "\n".join(lines)


def main():
    for cond in CONDITIONS_IN_ORDER:
        d = RUNS_DIR / CONDITION_DIR_NAME[cond]
        (d / "dbs").mkdir(parents=True, exist_ok=True)
        (d / "transcripts").mkdir(parents=True, exist_ok=True)
        (d / "scoring").mkdir(parents=True, exist_ok=True)
    (RUNS_DIR / "validation").mkdir(parents=True, exist_ok=True)

    client = Anthropic()
    run_date = datetime.now().strftime("%Y-%m-%d")

    all_results = {}  # condition -> list[LineageResult]
    for cond in CONDITIONS_IN_ORDER:
        log(f"[run_all] === Starting Condition {cond} (N={N_PER_CONDITION}) ===")
        cdir = RUNS_DIR / CONDITION_DIR_NAME[cond]
        results = run_condition_batch(client, cond, N_PER_CONDITION, cdir / "dbs")
        assert_counterbalance_balanced(results, cond)
        for r in results:
            (cdir / "transcripts" / f"lineage_{r.lineage_num:03d}.md").write_text(render_transcript(r))
            (cdir / "transcripts" / f"lineage_{r.lineage_num:03d}_raw.json").write_text(render_raw_json(r))
        all_results[cond] = results
        log(f"[run_all] === Condition {cond} complete: "
            f"{sum(1 for r in results if r.status == 'complete')}/{N_PER_CONDITION} without error ===")

    # --- Phase 4: mechanical scoring ---
    log("[run_all] Scoring all lineages")
    scores = {}
    for cond in CONDITIONS_IN_ORDER:
        cdir = RUNS_DIR / CONDITION_DIR_NAME[cond]
        for r in all_results[cond]:
            if r.status != "complete":
                continue
            sc = classify(r)
            scores[(cond, r.lineage_num)] = sc
            (cdir / "scoring" / f"lineage_{r.lineage_num:03d}.md").write_text(render_scoring_block(r, sc))

    # --- Per-condition observations.md ---
    for cond in CONDITIONS_IN_ORDER:
        cdir = RUNS_DIR / CONDITION_DIR_NAME[cond]
        obs = render_observations(cond, all_results[cond], scores, run_date)
        (cdir / "observations.md").write_text(obs)
    log("[run_all] Per-condition observations.md written")

    # --- Phase 5: validation layer ---
    log("[run_all] Preparing validation artifacts")
    results_by_condition = {c: [r for r in all_results[c] if r.status == "complete"] for c in CONDITIONS_IN_ORDER}
    held_out_sample = select_stratified_sample(results_by_condition, n_per_condition=4)
    held_out_md = render_held_out_artifact(
        held_out_sample, DOCS_DIR / "taxonomy_codebook.md", coder="(unassigned)", run_date=run_date,
    )
    (RUNS_DIR / "validation" / "held_out_coding.md").write_text(held_out_md)

    flat_results = [r for c in CONDITIONS_IN_ORDER for r in results_by_condition[c]]
    classifier_labels = {(r.condition, r.lineage_num): scores[(r.condition, r.lineage_num)].strategy for r in flat_results}
    audit_result = run_audit(flat_results, classifier_labels, fraction=0.10)
    audit_md = render_audit_report(audit_result, run_date, total_n=len(flat_results))
    (RUNS_DIR / "validation" / "classifier_audit.md").write_text(audit_md)
    log(f"[run_all] Validation artifacts written. Audit discrepancies: {len(audit_result['discrepancies'])}")

    # --- Statistics: confirmatory test + exploratory + achieved power ---
    log("[run_all] Computing statistics")

    def took_action_count(cond):
        return sum(1 for r in results_by_condition[cond] if scores[(cond, r.lineage_num)].collapse_binary == "took_action")

    n_a, n_b, n_c = len(results_by_condition["A"]), len(results_by_condition["B"]), len(results_by_condition["C"])
    x_a, x_b, x_c = took_action_count("A"), took_action_count("B"), took_action_count("C")

    p_ab = st.fisher_exact_two_sided(x_a, n_a - x_a, x_b, n_b - x_b)
    diff_ab, lo_ab, hi_ab = st.wilson_diff_ci(x_a, n_a, x_b, n_b)

    p_ac = st.fisher_exact_two_sided(x_a, n_a - x_a, x_c, n_c - x_c)
    diff_ac, lo_ac, hi_ac = st.wilson_diff_ci(x_a, n_a, x_c, n_c)

    p_bc = st.fisher_exact_two_sided(x_b, n_b - x_b, x_c, n_c - x_c)
    diff_bc, lo_bc, hi_bc = st.wilson_diff_ci(x_b, n_b, x_c, n_c)

    p_a_rate = x_a / n_a if n_a else 0.0
    achieved_power_22 = st.simulate_power(p_a_rate, 0.22, n=n_a, trials=3000)
    achieved_power_32 = st.simulate_power(p_a_rate, 0.32, n=n_a, trials=3000)
    mde_80 = st.minimum_detectable_effect(p_a_rate, n=n_a, target_power=0.80, trials=1500)

    labels_3x5 = []
    for cond in CONDITIONS_IN_ORDER:
        for r in results_by_condition[cond]:
            labels_3x5.append((cond, scores[(cond, r.lineage_num)].strategy))
    categories = list(STRATEGIES)
    table_3x5 = [[0] * len(categories) for _ in CONDITIONS_IN_ORDER]
    cidx = {c: i for i, c in enumerate(CONDITIONS_IN_ORDER)}
    sidx = {s: j for j, s in enumerate(categories)}
    for c, s in labels_3x5:
        table_3x5[cidx[c]][sidx[s]] += 1
    cramers_v = st.cramers_v(table_3x5)
    perm_p = st.permutation_test_table(labels_3x5, categories, CONDITIONS_IN_ORDER, trials=2000)

    stats_report = {
        "n": {"A": n_a, "B": n_b, "C": n_c},
        "took_action": {"A": x_a, "B": x_b, "C": x_c},
        "rate": {"A": p_a_rate, "B": x_b / n_b if n_b else 0.0, "C": x_c / n_c if n_c else 0.0},
        "confirmatory_A_vs_B": {"p": p_ab, "diff": diff_ab, "ci": (lo_ab, hi_ab)},
        "exploratory_A_vs_C": {"p": p_ac, "diff": diff_ac, "ci": (lo_ac, hi_ac)},
        "exploratory_B_vs_C": {"p": p_bc, "diff": diff_bc, "ci": (lo_bc, hi_bc)},
        "achieved_power": {"at_22pp": achieved_power_22, "at_32pp": achieved_power_32, "mde_80": mde_80},
        "table_3x5": table_3x5,
        "categories": categories,
        "cramers_v": cramers_v,
        "permutation_p": perm_p,
    }

    import json
    (RUNS_DIR / "statistics.json").write_text(json.dumps(stats_report, indent=2, default=str))
    log(f"[run_all] Statistics written to {RUNS_DIR / 'statistics.json'}")
    log(f"[run_all] A vs B: p={p_ab:.4f}, diff={diff_ab:+.3f}, 95% CI=[{lo_ab:.3f}, {hi_ab:.3f}]")
    log(f"[run_all] Achieved power at observed rate {p_a_rate:.1%}: +22pp={achieved_power_22:.2f}, +32pp={achieved_power_32:.2f}, MDE@80%={mde_80}")
    log("[run_all] Done.")


if __name__ == "__main__":
    main()
