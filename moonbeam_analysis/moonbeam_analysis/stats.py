from __future__ import annotations
import math
import numpy as np
import pandas as pd
from scipy.stats import fisher_exact, chi2_contingency
from statsmodels.stats.proportion import proportion_confint


def wilson_interval(x: int, n: int, alpha: float = 0.05) -> tuple[float,float]:
    if n == 0:
        return (float("nan"), float("nan"))
    lo, hi = proportion_confint(x, n, alpha=alpha, method="wilson")
    return float(lo), float(hi)


def newcombe_wilson_diff(x1: int, n1: int, x2: int, n2: int, alpha: float = 0.05) -> tuple[float,float]:
    """Newcombe hybrid-score CI for p1-p2, combining Wilson score intervals."""
    if n1 == 0 or n2 == 0:
        return (float("nan"), float("nan"))
    p1, p2 = x1/n1, x2/n2
    l1,u1 = wilson_interval(x1,n1,alpha)
    l2,u2 = wilson_interval(x2,n2,alpha)
    lower = (p1-p2) - math.sqrt((p1-l1)**2 + (u2-p2)**2)
    upper = (p1-p2) + math.sqrt((u1-p1)**2 + (p2-l2)**2)
    return max(-1.0, lower), min(1.0, upper)


def collapsed_comparison(df: pd.DataFrame, cond1: str, cond2: str) -> dict:
    a = df[df.condition == cond1]
    b = df[df.condition == cond2]
    x1 = int((a.collapse_binary == "took_action").sum()); n1 = len(a)
    x2 = int((b.collapse_binary == "took_action").sum()); n2 = len(b)
    table = np.array([[x1, n1-x1], [x2, n2-x2]])
    odds, p = fisher_exact(table, alternative="two-sided")
    diff = x2/n2 - x1/n1 if n1 and n2 else float("nan")
    # CI reported in the same direction: cond2 - cond1.
    ci = newcombe_wilson_diff(x2,n2,x1,n1)
    return {
        "comparison": f"{cond2}-{cond1}",
        "condition_1": cond1, "condition_2": cond2,
        "n1": n1, "actions1": x1, "rate1": x1/n1 if n1 else float("nan"),
        "n2": n2, "actions2": x2, "rate2": x2/n2 if n2 else float("nan"),
        "difference": diff, "ci95_low": ci[0], "ci95_high": ci[1],
        "odds_ratio": float(odds), "fisher_p_two_sided": float(p),
        "table": table.tolist(),
    }


def cramers_v(table: np.ndarray) -> float:
    # Preserve explicit zero categories in reporting, but remove all-zero rows/columns
    # for the statistic because expected frequencies are undefined there.
    table = np.asarray(table, dtype=float)
    keep_r = table.sum(axis=1) > 0
    keep_c = table.sum(axis=0) > 0
    reduced = table[np.ix_(keep_r, keep_c)]
    n = reduced.sum()
    if n == 0 or min(reduced.shape) < 2:
        return 0.0 if n > 0 else float("nan")
    chi2, _, _, _ = chi2_contingency(reduced, correction=False)
    return float(math.sqrt((chi2/n) / max(1, min(reduced.shape[0]-1, reduced.shape[1]-1))))


def permutation_3x5(df: pd.DataFrame, strategies: list[str], trials: int = 10000, seed: int = 20260814) -> dict:
    # Per prereg: full 3x5 across the five named strategies. 'other' is reported separately and omitted from this fixed 3x5.
    core = df[df.strategy.isin(strategies)].copy()
    observed = pd.crosstab(core.condition, core.strategy).reindex(index=["A","B","C"], columns=strategies, fill_value=0)
    table = observed.to_numpy()
    if table.sum() == 0:
        return {"table": observed.to_dict(), "cramers_v": float("nan"), "permutation_p": float("nan"), "trials": trials}
    obs_v = cramers_v(table)
    rng = np.random.default_rng(seed)
    labels = core.condition.to_numpy().copy()
    strats = core.strategy.to_numpy()
    ge = 0
    for _ in range(trials):
        perm = rng.permutation(labels)
        tmp = pd.crosstab(pd.Series(perm), pd.Series(strats)).reindex(index=["A","B","C"], columns=strategies, fill_value=0).to_numpy()
        if cramers_v(tmp) >= obs_v - 1e-15:
            ge += 1
    p = (ge + 1) / (trials + 1)
    return {"table": observed.to_dict(), "cramers_v": obs_v, "permutation_p": p, "trials": trials}


def simulate_power(baseline: float, effect: float, n: int = 50, trials: int = 3000, alpha: float = 0.05, seed: int = 20260814) -> float:
    p2 = baseline + effect
    if not (0 <= baseline <= 1 and 0 <= p2 <= 1):
        return float("nan")
    rng = np.random.default_rng(seed)
    hits = 0
    for _ in range(trials):
        x1 = rng.binomial(n, baseline); x2 = rng.binomial(n, p2)
        _, p = fisher_exact([[x1, n-x1], [x2, n-x2]], alternative="two-sided")
        hits += p < alpha
    return hits/trials


def achieved_mde(baseline: float, n: int = 50, target_power: float = 0.80, trials: int = 3000, step: float = 0.01, seed: int = 20260814) -> dict:
    max_effect = 1-baseline
    effects = np.arange(step, max_effect + step/2, step)
    rows=[]
    for i,e in enumerate(effects):
        power = simulate_power(baseline, float(e), n=n, trials=trials, seed=seed+i)
        rows.append((float(e), power))
        if power >= target_power:
            return {"baseline": baseline, "n": n, "target_power": target_power, "mde": float(e), "power_at_mde": power, "grid": rows}
    return {"baseline": baseline, "n": n, "target_power": target_power, "mde": None, "power_at_mde": None, "grid": rows}
