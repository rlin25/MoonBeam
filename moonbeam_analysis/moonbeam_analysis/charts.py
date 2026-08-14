from __future__ import annotations

from pathlib import Path
import math
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .constants import STRATEGIES
from .stats import arbitration_comparison, wilson_interval

CONDITION_ORDER = ["A", "B", "C"]
ARM_ORDER = ["A-first", "B-first"]
STATE_ORDER = ["unchanged", "edited", "deleted", "unknown"]
ARBITRATION_ORDER = ["kept_first", "kept_second"]


def _save(fig, path: Path) -> None:
    fig.tight_layout()
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def _condition_subset(df: pd.DataFrame) -> pd.DataFrame:
    if "condition" not in df.columns:
        return df.iloc[0:0]
    return df[df["condition"].isin(CONDITION_ORDER)].copy()


def _pct(x: float) -> str:
    return "NA" if pd.isna(x) else f"{100*x:.1f}%"


def _pp(x: float) -> str:
    return "NA" if pd.isna(x) else f"{100*x:+.1f} percentage points"


def _arbitration_rate_ci(df: pd.DataFrame, path: Path) -> tuple[bool, str]:
    if not {"condition", "strategy"}.issubset(df.columns):
        return False, "Required arbitration fields were unavailable."
    d = _condition_subset(df)
    rows=[]
    for cond in CONDITION_ORDER:
        q=d[d.condition==cond]; n=len(q)
        if not n: continue
        x=int((q.strategy.astype(str).str.lower()=="arbitration").sum()); lo,hi=wilson_interval(x,n)
        rows.append((cond,x/n,lo,hi,x,n))
    if not rows: return False,"No usable condition data were available."
    fig,ax=plt.subplots(figsize=(7.4,4.8)); xs=np.arange(len(rows))
    rates=np.array([r[1] for r in rows])*100; lows=np.array([r[2] for r in rows])*100; highs=np.array([r[3] for r in rows])*100
    ax.errorbar(xs,rates,yerr=np.vstack([rates-lows,highs-rates]),fmt="o",capsize=6,markersize=7)
    ax.set_xticks(xs,[f"Condition {r[0]}" for r in rows]); ax.set_ylabel("Lineages ending in arbitration (%)"); ax.set_ylim(0,105)
    ax.set_title("Arbitration rate by condition with 95% Wilson intervals")
    for x,rate,row in zip(xs,rates,rows): ax.annotate(f"{row[4]}/{row[5]}\n{rate:.1f}%",(x,rate),xytext=(0,10),textcoords="offset points",ha="center")
    _save(fig,path)
    summary="; ".join(f"{r[0]}: {r[4]}/{r[5]} ({100*r[1]:.1f}%)" for r in rows)
    return True,("This is the current primary dependent-variable figure. Each point is the percentage of lineages classified as arbitration, and each whisker is a 95% Wilson interval. "
                 "Higher values mean the model more often resolved the contradiction by preserving one claim and eliminating the competing one. Current data: "+summary+".")


def _effect_size_forest(df: pd.DataFrame, path: Path) -> tuple[bool, str]:
    if not {"condition","strategy"}.issubset(df.columns): return False,"Required arbitration fields were unavailable."
    comparisons=[
        ("A − B (confirmatory)", arbitration_comparison(df,"A","B")),
        ("A − C (exploratory)", arbitration_comparison(df,"A","C")),
        ("B − C (exploratory)", arbitration_comparison(df,"B","C")),
    ]
    if any(pd.isna(c[1]["difference"]) for c in comparisons): return False,"At least one condition was missing."
    labels=[c[0] for c in comparisons]; diffs=np.array([c[1]["difference"] for c in comparisons])*100
    lows=np.array([c[1]["ci95_low"] for c in comparisons])*100; highs=np.array([c[1]["ci95_high"] for c in comparisons])*100; ys=np.arange(len(labels))[::-1]
    fig,ax=plt.subplots(figsize=(8.6,4.8))
    for y,diff,lo,hi in zip(ys,diffs,lows,highs): ax.plot([lo,hi],[y,y],linewidth=2); ax.plot(diff,y,"o",markersize=7)
    ax.axvline(0,linestyle="--",linewidth=1); ax.set_yticks(ys,labels); ax.set_xlabel("Difference in arbitration rate (percentage points)")
    ax.set_title("Arbitration-rate effect sizes with 95% confidence intervals")
    bound=max(10,math.ceil(max(abs(lows).max(),abs(highs).max())/5)*5); ax.set_xlim(-bound,bound); _save(fig,path)
    ab=comparisons[0][1]
    return True,("This is the visual companion to the confirmatory Fisher test. The dot is the difference in arbitration rate and the line is its 95% confidence interval; 0 means no difference. "
                 f"The confirmatory direction is A − B. Current A − B estimate: {_pp(ab['difference'])}, 95% CI [{100*ab['ci95_low']:.1f}, {100*ab['ci95_high']:.1f}] percentage points; Fisher p={ab['fisher_p_two_sided']:.3g}. "
                 "The C comparisons are exploratory only.")


def _strategy_100pct(df: pd.DataFrame, path: Path) -> tuple[bool, str]:
    if not {"condition", "strategy"}.issubset(df.columns):
        return False, "Required strategy fields were unavailable."
    d = _condition_subset(df)
    categories = list(STRATEGIES)
    counts = pd.crosstab(d["condition"], d["strategy"]).reindex(index=CONDITION_ORDER, columns=categories, fill_value=0)
    if counts.to_numpy().sum() == 0:
        return False, "No usable strategy labels were available."
    pct = counts.div(counts.sum(axis=1), axis=0) * 100

    fig, ax = plt.subplots(figsize=(10.5, 5.7))
    bottom = np.zeros(len(CONDITION_ORDER))
    for strategy in categories:
        vals = pct[strategy].to_numpy()
        ax.bar(CONDITION_ORDER, vals, bottom=bottom, label=strategy)
        bottom += vals
    ax.set_ylim(0, 100)
    ax.set_ylabel("Share of lineages (%)")
    ax.set_xlabel("Condition")
    ax.set_title("Behavioral strategy composition by condition")
    ax.legend(title="Strategy", bbox_to_anchor=(1.02, 1), loc="upper left")
    _save(fig, path)

    dominant = []
    for cond in CONDITION_ORDER:
        if counts.loc[cond].sum():
            top = counts.loc[cond].idxmax(); n = int(counts.loc[cond, top]); total = int(counts.loc[cond].sum())
            dominant.append(f"{cond}: {top} {n}/{total} ({100*n/total:.1f}%)")
    return True, (
        "Each bar represents 100% of a condition, split by the lineage's overall behavioral strategy. This is better than raw grouped bars for comparing composition across equally sized conditions. "
        "It shows the full behavioral composition underlying the binary arbitration/non-arbitration DV. Current dominant strategies: " + "; ".join(dominant) + ". "
        "This taxonomy view is descriptive; the current preregistered headline test collapses it to arbitration versus non_arbitration."
    )


def _cumulative_action(df: pd.DataFrame, path: Path) -> tuple[bool, str]:
    if not {"condition", "first_action_step"}.issubset(df.columns):
        return False, "First-action-step data were unavailable."
    d = _condition_subset(df)
    d["first_action_step"] = pd.to_numeric(d["first_action_step"], errors="coerce")
    max_step = int(max(7, d["first_action_step"].max(skipna=True) if d["first_action_step"].notna().any() else 7))
    steps = list(range(1, max_step + 1))

    fig, ax = plt.subplots(figsize=(8.2, 5.2))
    summaries = []
    made = False
    for cond in CONDITION_ORDER:
        s = d[d.condition == cond]
        if s.empty:
            continue
        vals = pd.to_numeric(s.first_action_step, errors="coerce")
        cumulative = [100 * (vals.le(step).fillna(False).sum() / len(s)) for step in steps]
        ax.plot(steps, cumulative, marker="o", label=f"Condition {cond}")
        summaries.append(f"{cond}: {cumulative[0]:.1f}% by step 1, {cumulative[-1]:.1f}% by step {max_step}")
        made = True
    if not made:
        plt.close(fig)
        return False, "No usable first-action-step observations were available."
    ax.set_xlabel("Step")
    ax.set_ylabel("Lineages that had acted by this step (%)")
    ax.set_ylim(0, 105)
    ax.set_xticks(steps)
    ax.set_title("Cumulative timing of first memory action")
    ax.legend()
    _save(fig, path)
    return True, (
        "This curve shows how quickly lineages first wrote, edited, or deleted memory. A curve that rises earlier indicates faster intervention; a curve that ends below 100% means some lineages never acted. "
        "Current data: " + "; ".join(summaries) + ". This is a timing/descriptive figure, not the confirmatory A-vs-B test."
    )


def _recall_distribution(df: pd.DataFrame, path: Path) -> tuple[bool, str]:
    if not {"condition", "recall_count"}.issubset(df.columns):
        return False, "Recall-count data were unavailable."
    d = _condition_subset(df)
    d["recall_count"] = pd.to_numeric(d["recall_count"], errors="coerce")
    groups = [d.loc[d.condition == c, "recall_count"].dropna().to_numpy() for c in CONDITION_ORDER]
    if not any(len(g) for g in groups):
        return False, "No usable recall-count observations were available."

    fig, ax = plt.subplots(figsize=(7.8, 5.2))
    valid_positions=[]; valid_groups=[]; labels=[]
    for i,(c,g) in enumerate(zip(CONDITION_ORDER,groups), start=1):
        if len(g):
            valid_positions.append(i); valid_groups.append(g); labels.append(c)
    ax.boxplot(valid_groups, positions=valid_positions, widths=0.45, showfliers=False)
    rng = np.random.default_rng(20260814)
    for pos,g in zip(valid_positions,valid_groups):
        jitter = rng.normal(0, 0.055, len(g))
        ax.scatter(np.full(len(g),pos)+jitter, g, alpha=0.55, s=22)
    ax.set_xticks(valid_positions, [f"Condition {c}" for c in labels])
    ax.set_ylabel("Explicit recall calls")
    ax.set_title("Recall-call distribution by condition")
    _save(fig, path)
    summaries=[]
    for c,g in zip(CONDITION_ORDER,groups):
        if len(g): summaries.append(f"{c}: median {np.median(g):.1f}, mean {np.mean(g):.2f}")
    return True, (
        "Each dot is one lineage's number of explicit recall calls; the box summarizes the middle of the distribution. This shows search effort rather than whether the model ultimately changed memory. "
        "Higher values mean the model searched memory more often. Current data: " + "; ".join(summaries) + "."
    )


def _counterbalance_ci(df: pd.DataFrame, path: Path) -> tuple[bool, str]:
    needed={"condition","counterbalance_arm","strategy"}
    if not needed.issubset(df.columns): return False,"Counterbalance fields were unavailable."
    d=_condition_subset(df); d=d[d.counterbalance_arm.isin(ARM_ORDER)]; rows=[]
    for cond in CONDITION_ORDER:
        for arm in ARM_ORDER:
            q=d[(d.condition==cond)&(d.counterbalance_arm==arm)]
            if len(q):
                x=int((q.strategy.astype(str).str.lower()=="arbitration").sum()); n=len(q); lo,hi=wilson_interval(x,n); rows.append((cond,arm,x/n,lo,hi,x,n))
    if not rows:return False,"No usable counterbalance observations were available."
    fig,ax=plt.subplots(figsize=(8.2,5.2)); base=np.arange(len(CONDITION_ORDER)); offsets={"A-first":-0.12,"B-first":0.12}
    for arm in ARM_ORDER:
        subset=[r for r in rows if r[1]==arm]; xs=np.array([base[CONDITION_ORDER.index(r[0])]+offsets[arm] for r in subset]); rates=np.array([r[2] for r in subset])*100
        lo=np.array([r[3] for r in subset])*100; hi=np.array([r[4] for r in subset])*100; ax.errorbar(xs,rates,yerr=np.vstack([rates-lo,hi-rates]),fmt="o",capsize=5,label=arm)
    ax.set_xticks(base,[f"Condition {c}" for c in CONDITION_ORDER]); ax.set_ylim(0,105); ax.set_ylabel("Arbitration rate (%)"); ax.set_title("Counterbalance robustness check: arbitration rate"); ax.legend(title="Seeding order"); _save(fig,path)
    summaries=[]
    for cond in CONDITION_ORDER:
        parts=[]
        for arm in ARM_ORDER:
            match=[r for r in rows if r[0]==cond and r[1]==arm]
            if match: parts.append(f"{arm} {match[0][5]}/{match[0][6]} ({100*match[0][2]:.1f}%)")
        if parts:summaries.append(f"{cond}: "+", ".join(parts))
    return True,("This robustness figure checks whether arbitration rates differ depending on which contradictory seed was inserted first. It is not powered as an order-effect test, so arm differences are observations rather than confirmatory findings. Current split: "+"; ".join(summaries)+".")


def _seed_states(df: pd.DataFrame, path: Path) -> tuple[bool, str]:
    needed={"condition","seeded_first_final","seeded_second_final"}
    if not needed.issubset(df.columns): return False,"Seed-state fields were unavailable."
    d=_condition_subset(df)
    rows=[]
    for cond in CONDITION_ORDER:
        s=d[d.condition==cond]
        for seed_col,seed_label in [("seeded_first_final","First seed"),("seeded_second_final","Second seed")]:
            vals=s[seed_col].fillna("unknown").astype(str).str.lower()
            counts=vals.value_counts()
            total=len(vals)
            for state in STATE_ORDER:
                rows.append((cond,seed_label,state,int(counts.get(state,0)),total))
    if not rows: return False,"No usable seed-state observations were available."

    labels=[f"{c}\nFirst" for c in CONDITION_ORDER]+[f"{c}\nSecond" for c in CONDITION_ORDER]
    combos=[(c,"First seed") for c in CONDITION_ORDER]+[(c,"Second seed") for c in CONDITION_ORDER]
    fig,ax=plt.subplots(figsize=(10,5.6)); bottom=np.zeros(len(combos))
    for state in STATE_ORDER:
        vals=[]
        for cond,seed in combos:
            match=[r for r in rows if r[0]==cond and r[1]==seed and r[2]==state][0]
            vals.append(100*match[3]/match[4] if match[4] else 0)
        ax.bar(np.arange(len(combos)),vals,bottom=bottom,label=state); bottom+=np.array(vals)
    ax.set_xticks(np.arange(len(combos)),labels); ax.set_ylim(0,100)
    ax.set_ylabel("Final-state share (%)"); ax.set_title("Final state of first vs. second seeded entries")
    ax.legend(title="Final state",bbox_to_anchor=(1.02,1),loc="upper left")
    _save(fig,path)
    return True, (
        "These stacked bars show what happened to the first and second seeded memories by the end of each lineage: unchanged, edited, or deleted. Comparing the two bars within a condition can reveal positional asymmetry that may relate to seeding order. "
        "Treat this as a descriptive diagnostic; the counterbalance analysis is the cleaner robustness check for order."
    )


def _arbitration_direction(df: pd.DataFrame, path: Path) -> tuple[bool, str]:
    needed={"condition","strategy","arbitration_direction"}
    if not needed.issubset(df.columns): return False,"Arbitration fields were unavailable."
    d=_condition_subset(df); d=d[d.strategy=="arbitration"].copy()
    d["arbitration_direction"]=d.arbitration_direction.astype(str).str.strip().str.lower()
    d=d[d.arbitration_direction.isin(ARBITRATION_ORDER)]
    if d.empty:return False,"No arbitration cases with a recorded direction were available."
    table=pd.crosstab(d.condition,d.arbitration_direction).reindex(index=CONDITION_ORDER,columns=ARBITRATION_ORDER,fill_value=0)
    pct=table.div(table.sum(axis=1).replace(0,np.nan),axis=0)*100
    fig,ax=plt.subplots(figsize=(8,5.2)); bottom=np.zeros(3)
    for direction in ARBITRATION_ORDER:
        vals=pct[direction].fillna(0).to_numpy(); label="Kept first" if direction=="kept_first" else "Kept second"
        ax.bar(CONDITION_ORDER,vals,bottom=bottom,label=label); bottom+=vals
    ax.set_ylim(0,100); ax.set_ylabel("Share of arbitration cases (%)"); ax.set_title("Which seeded entry survived when the model arbitrated?")
    ax.legend(); _save(fig,path)
    summaries=[]
    for c in CONDITION_ORDER:
        n=int(table.loc[c].sum())
        if n: summaries.append(f"{c}: kept first {int(table.loc[c,'kept_first'])}/{n}, kept second {int(table.loc[c,'kept_second'])}/{n}")
    return True, (
        "Among arbitration cases only, this figure shows whether the first or second seeded entry survived. It helps diagnose directional/position preference, but it is conditional on already being in the arbitration category and therefore answers a different question from the overall arbitration rate. "
        "Current arbitration cases: " + "; ".join(summaries) + "."
    )


def generate_charts(df: pd.DataFrame, output_dir: str | Path) -> dict[str, str]:
    """Generate paper-oriented PNGs plus plain-English interpretations."""
    out=Path(output_dir); out.mkdir(parents=True,exist_ok=True)
    jobs=[
        ("01_arbitration_rate_with_ci.png", _arbitration_rate_ci, "PRIMARY"),
        ("02_effect_size_forest.png", _effect_size_forest, "PRIMARY"),
        ("03_strategy_composition.png", _strategy_100pct, "PRIMARY"),
        ("04_cumulative_first_action.png", _cumulative_action, "SECONDARY"),
        ("05_recall_distribution.png", _recall_distribution, "SECONDARY"),
        ("06_counterbalance_arbitration_robustness.png", _counterbalance_ci, "ROBUSTNESS"),
        ("07_seed_final_states.png", _seed_states, "SECONDARY"),
        ("08_arbitration_direction.png", _arbitration_direction, "SECONDARY"),
    ]
    status={}; explanations={}; roles={}
    for filename,func,role in jobs:
        roles[filename]=role
        try:
            made, explanation=func(df.copy(),out/filename)
            status[filename]="generated" if made else "skipped — no usable data"
            explanations[filename]=explanation
        except Exception as exc:
            status[filename]=f"skipped — {type(exc).__name__}: {exc}"
            explanations[filename]="This figure could not be generated; see the status above."

    lines=[
        "# MoonBeam charts — what each figure is telling you",
        "",
        "The figures are generated automatically from `lineage_scoring.csv`. **Primary** figures are the clearest paper-facing summaries; **secondary** figures explain behavior and timing; the **robustness** figure checks seeding order without making an order-effect significance claim.",
        "",
        "## Recommended paper order",
        "",
        "1. `01_arbitration_rate_with_ci.png` — current confirmatory DV by condition.",
        "2. `02_effect_size_forest.png` — lead with the effect size and uncertainty for A − B.",
        "3. `03_strategy_composition.png` — shows the full taxonomy behind arbitration vs. non_arbitration.",
        "4. Put the remaining figures in secondary/supplementary results unless they become substantively important.",
        "",
    ]
    for filename,_,role in jobs:
        lines += [f"## {filename}","",f"**Role:** {role}","",f"**Status:** {status[filename]}","",f"**What it tells you:** {explanations[filename]}",""]
    lines += [
        "## Interpretation guardrails",
        "",
        "- The current confirmatory test is A vs. B on `arbitration/non_arbitration`; do not promote the C comparisons or taxonomy figures into additional confirmatory significance claims.",
        "- Counterbalance is a robustness check. If the arms differ, report it as an observation for future work rather than as a powered order-effect finding.",
        "- `took_action/no_action` is retained only as a retired descriptive diagnostic; it must not be reported as the confirmatory DV.",
        "- Arbitration and action remain distinct: a lineage can edit/delete a seeded entry and therefore `take_action` without ending in the arbitration strategy.",
        "",
    ]
    (out/"README.md").write_text("\n".join(lines),encoding="utf-8")
    return status
