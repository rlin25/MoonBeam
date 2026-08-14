from __future__ import annotations
from pathlib import Path
import hashlib, random
import pandas as pd
from sklearn.metrics import cohen_kappa_score


def codebook_hash(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def held_out_sample(scored: list[dict], seed: int = 20260814) -> list[dict]:
    rng=random.Random(seed); out=[]
    for cond in ["A","B","C"]:
        pool=[r for r in scored if r["condition"]==cond]
        if len(pool) < 4: out.extend(pool)
        else: out.extend(rng.sample(pool,4))
    return out


def held_out_template(sample: list[dict], codebook_sha256: str, date: str, coder: str = "________________") -> str:
    lines=[f"# Held-Out Coding Subsample — {date}","",f"Lineages sampled: {len(sample)}, stratified across Conditions A, B, C (target 4 each)",f"Codebook version: {codebook_sha256}",f"Coder: {coder}",""]
    for r in sample:
        lines += [f"## Lineage {r['lineage_id']} — Condition {r['condition']}", "", f"Counterbalance arm: {r.get('counterbalance_arm')}", f"Seeded entry first final state: {r['seeded_first_final']}", f"Seeded entry second final state: {r['seeded_second_final']}", "New entries created:"]
        if r.get("new_entries_created"):
            lines += [f"- {e['id']}: {e['content']}" for e in r['new_entries_created']]
        else: lines += ["- none"]
        lines += ["Action log:"]
        for ev in r.get("events",[]): lines += [f"- step {ev.get('step')}: {ev}"]
        lines += ["", "Human label: ______________________", ""]
    return "\n".join(lines)


def compute_kappa(labels_df: pd.DataFrame, human_col="human_label", classifier_col="classifier_label") -> float:
    x=labels_df.dropna(subset=[human_col,classifier_col])
    if len(x)==0: return float("nan")
    return float(cohen_kappa_score(x[human_col], x[classifier_col]))
