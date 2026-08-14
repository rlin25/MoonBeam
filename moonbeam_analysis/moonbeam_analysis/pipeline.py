from __future__ import annotations
import argparse
from pathlib import Path
from datetime import date
import pandas as pd

from .io import iter_lineage_json, iter_lineage_markdown, dump_json
from .scoring import score_lineage
from .reporting import observations_markdown, scoring_markdown
from .stats import collapsed_comparison, permutation_3x5, achieved_mde
from .constants import STRATEGIES
from .validation import held_out_sample, held_out_template, codebook_hash
from .audit import audit_sample
from .charts import generate_charts


def _load_scored(input_dir: str, input_format: str = "auto", condition: str | None = None) -> tuple[list[dict], str]:
    scored=[]
    fmt=input_format
    if fmt in {"auto","markdown"}:
        md=list(iter_lineage_markdown(input_dir, explicit_condition=condition))
        if md:
            scored=[rec for _,rec in md]
            return scored,"markdown"
        if fmt=="markdown":
            raise SystemExit("No scored lineage Markdown files found (expected lineage_*.md).")
    if fmt in {"auto","json"}:
        js=list(iter_lineage_json(input_dir))
        if js:
            scored=[score_lineage(rec) for _,rec in js]
            return scored,"json"
    raise SystemExit("No usable lineage files found. Expected scored lineage_*.md files or normalized lineage JSON.")


def run(input_dir: str, output_dir: str, codebook: str | None = None,
        permutation_trials: int = 10000, power_trials: int = 3000,
        input_format: str = "auto", condition: str | None = None) -> None:
    out=Path(output_dir); out.mkdir(parents=True,exist_ok=True)
    scored,source_format=_load_scored(input_dir,input_format,condition)

    # Write normalized copies of the scored records for traceability.
    for s in scored:
        if s.get("condition") not in {"A","B","C"}:
            raise SystemExit(f"Could not determine condition for lineage {s.get('lineage_id')}. Put files under condition_a/b/c or pass --condition.")
        cdir=out/f"condition_{s['condition'].lower()}"/"scoring"; cdir.mkdir(parents=True,exist_ok=True)
        (cdir/f"lineage_{int(s['lineage_id']):03d}.md").write_text(scoring_markdown(s),encoding="utf-8")
        dump_json({k:v for k,v in s.items() if k!="events"}, cdir/f"lineage_{int(s['lineage_id']):03d}.json")

    df=pd.DataFrame([{k:v for k,v in s.items() if k not in {"events","new_entries_created"}} for s in scored])
    df.to_csv(out/"lineage_scoring.csv",index=False)

    # Audit any legacy/invalid collapse labels that had to be normalized from
    # seeded final states. Current Richard harness output should normally have
    # zero such rows.
    if "collapse_binary_source" in df.columns:
        adjusted = df[df["collapse_binary_source"] != "reported"]
        adjusted.to_csv(out/"collapse_binary_normalization_audit.csv", index=False)

    generate_charts(df, out/"charts")

    today=str(date.today())
    for cond in ["A","B","C"]:
        cdir=out/f"condition_{cond.lower()}"; cdir.mkdir(parents=True,exist_ok=True)
        (cdir/"observations.md").write_text(observations_markdown(scored,cond,today),encoding="utf-8")

    comps={"A_vs_B":collapsed_comparison(df,"A","B"),"A_vs_C":collapsed_comparison(df,"A","C"),"B_vs_C":collapsed_comparison(df,"B","C")}
    core5=[s for s in STRATEGIES if s!="other"]
    perm=permutation_3x5(df,core5,trials=permutation_trials)
    a=df[df.condition=="A"]; baseline=float((a.collapse_binary=="took_action").mean()) if len(a) else float("nan")
    mde=achieved_mde(baseline,n=len(a),trials=power_trials) if len(a) else {}
    dump_json({"source_format":source_format,"comparisons":comps,"descriptive_3x5":perm,"achieved_power_mde":mde},out/"statistics.json")

    vdir=out/"validation"; vdir.mkdir(exist_ok=True)
    sample=held_out_sample(scored)
    sha=codebook_hash(codebook) if codebook else "CODEBOOK_PATH_NOT_SUPPLIED"
    warning=""
    if source_format=="markdown":
        warning=("\n\n> IMPORTANT: These inputs are already-scored Markdown summaries, not raw lineage logs. "
                 "This file can help select cases, but it is not a valid blind human-coding artifact by itself. "
                 "Use the corresponding raw lineage/action logs for the preregistered human validation.\n")
    (vdir/"held_out_coding.md").write_text(held_out_template(sample,sha,today)+warning,encoding="utf-8")
    pd.DataFrame([{"condition":r["condition"],"lineage_id":r["lineage_id"],"classifier_label":r["strategy"],"human_label":""} for r in sample]).to_csv(vdir/"held_out_labels.csv",index=False)

    audit=audit_sample(scored,15)
    adf=pd.DataFrame(audit); adf.to_csv(vdir/"classifier_audit.csv",index=False)
    title="Scoring Consistency Audit" if source_format=="markdown" else "Classifier Audit"
    lines=[f"# {title} — {today}","",f"Lineages audited: {len(audit)} (target 15 / 10% of 150)"]
    if source_format=="markdown":
        lines += ["Source: already-scored lineage Markdown.","This checks whether reported strategy labels are consistent with reported final-state fields; it is not an independent reclassification of raw logs."]
    else:
        lines += ["Re-derivation path: independent of scoring.py"]
    lines += ["","| Condition | Lineage | Classifier label | Re-derived label | Match |","|---|---|---|---|---|"]
    for r in audit: lines.append(f"| {r['condition']} | {r['lineage_id']} | {r['classifier_label']} | {r['rederived_label']} | {r['match']} |")
    mism=[r for r in audit if not r["match"]]
    lines += ["",f"Discrepancies: {len(mism)} — " + ("none" if not mism else "see CSV and rows above")]
    (vdir/"classifier_audit.md").write_text("\n".join(lines),encoding="utf-8")


def main():
    p=argparse.ArgumentParser(description="Project Moonbeam data/statistics pipeline for Treylon")
    p.add_argument("--input",required=True,help="Root directory containing condition folders with lineage_*.md files (or normalized JSON)")
    p.add_argument("--output",default="analysis_output")
    p.add_argument("--codebook",default=None)
    p.add_argument("--input-format",choices=["auto","markdown","json"],default="auto")
    p.add_argument("--condition",choices=["A","B","C"],default=None,help="Only needed when a single Markdown folder does not include condition_a/b/c in its path")
    p.add_argument("--permutation-trials",type=int,default=10000)
    p.add_argument("--power-trials",type=int,default=3000)
    args=p.parse_args(); run(args.input,args.output,args.codebook,args.permutation_trials,args.power_trials,args.input_format,args.condition)

if __name__=="__main__": main()
