"""
Statistics for the confirmatory test (preregistration.md Sec 3) and the
achieved-power recomputation (preregistration.md Sec 5). Plain Python --
no scipy/numpy dependency, per implementation.md Sec 9's environment note
(mnemosyne-memory + ANTHROPIC_API_KEY only). Fisher's exact is implemented
directly via the hypergeometric distribution (math.comb); Wilson CIs and
the two-proportion difference CI use closed-form formulas; the power
recomputation and the 3x5 table's permutation test use Monte Carlo
simulation with a fixed seed for reproducibility.
"""

from __future__ import annotations

import math
import random

Z_95 = 1.959963984540054  # two-sided 95% normal quantile


def fisher_exact_two_sided(a: int, b: int, c: int, d: int) -> float:
    """Two-sided Fisher's exact test p-value for a 2x2 table
    [[a, b], [c, d]], via direct summation over the hypergeometric
    distribution of all tables sharing the observed margins, summing the
    probability of every table at least as extreme (<=) as the observed
    one -- the standard definition (matches R's fisher.test / scipy)."""
    n = a + b + c + d
    r1, r2 = a + b, c + d
    c1, c2 = a + c, b + d

    def hyper_prob(x: int) -> float:
        y = c1 - x  # count in cell (2,1) for this value of a
        if x < 0 or y < 0 or x > r1 or y > r2:
            return 0.0
        return (math.comb(r1, x) * math.comb(r2, y)) / math.comb(n, c1)

    lo = max(0, c1 - r2)
    hi = min(r1, c1)
    p_obs = hyper_prob(a)
    total = 0.0
    for x in range(lo, hi + 1):
        p = hyper_prob(x)
        if p <= p_obs * (1 + 1e-7):
            total += p
    return min(total, 1.0)


def wilson_ci(x: int, n: int, z: float = Z_95) -> tuple:
    """Wilson score interval for a single proportion x/n."""
    if n == 0:
        return (0.0, 0.0)
    phat = x / n
    denom = 1 + z * z / n
    center = (phat + z * z / (2 * n)) / denom
    half = (z * math.sqrt(phat * (1 - phat) / n + z * z / (4 * n * n))) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def wilson_diff_ci(x1: int, n1: int, x2: int, n2: int, z: float = Z_95) -> tuple:
    """95% CI for p1 - p2 via Newcombe's hybrid score method (Newcombe 1998,
    method 10) -- the standard 'Wilson CI for a proportion difference'."""
    p1, p2 = x1 / n1, x2 / n2
    l1, u1 = wilson_ci(x1, n1, z)
    l2, u2 = wilson_ci(x2, n2, z)
    diff = p1 - p2
    lower = diff - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2)
    upper = diff + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)
    return (diff, max(-1.0, lower), min(1.0, upper))


def simulate_power(p_a: float, delta: float, n: int = 50, trials: int = 3000,
                    alpha: float = 0.05, seed: int = 20260814) -> float:
    """Monte Carlo power estimate: fraction of simulated N-per-arm trials
    (Condition A ~ Bernoulli(p_a), Condition B ~ Bernoulli(p_a+delta)) for
    which Fisher's exact two-sided test rejects at alpha. Fixed seed for
    reproducibility (preregistration.md Sec 5's methodology, recomputed
    against the observed rate rather than the 33% placeholder)."""
    p_b = min(1.0, max(0.0, p_a + delta))
    rng = random.Random(seed)
    rejections = 0
    for _ in range(trials):
        a = sum(1 for _ in range(n) if rng.random() < p_a)
        b = sum(1 for _ in range(n) if rng.random() < p_b)
        p = fisher_exact_two_sided(a, n - a, b, n - b)
        if p < alpha:
            rejections += 1
    return rejections / trials


def minimum_detectable_effect(p_a: float, n: int = 50, target_power: float = 0.80,
                               trials: int = 1500, alpha: float = 0.05, seed: int = 20260814) -> float:
    """Smallest delta (percentage points, as a 0-1 fraction) reaching
    target_power, via coarse-to-fine search over delta in [0, 1 - p_a] --
    the increase direction. See minimum_detectable_effect_decrease for a
    baseline near ceiling, where the effect of interest is a decrease."""
    best = None
    for pct in range(1, 100):
        delta = pct / 100.0
        if p_a + delta > 1.0:
            break
        power = simulate_power(p_a, delta, n=n, trials=trials, alpha=alpha, seed=seed)
        if power >= target_power:
            best = delta
            break
    return best if best is not None else float("nan")


def minimum_detectable_effect_decrease(p_a: float, n: int = 50, target_power: float = 0.80,
                                        trials: int = 1500, alpha: float = 0.05, seed: int = 20260814) -> float:
    """Smallest decrease (a negative delta, as a 0-1 fraction) reaching
    target_power, via coarse-to-fine search over delta in [-p_a, 0).
    Needed when the baseline sits near ceiling and the effect of interest is
    a decrease (preregistration.md Sec 5) -- minimum_detectable_effect only
    searches the increase direction and returns no useful result there."""
    best = None
    for pct in range(1, 100):
        delta = -pct / 100.0
        if p_a + delta < 0.0:
            break
        power = simulate_power(p_a, delta, n=n, trials=trials, alpha=alpha, seed=seed)
        if power >= target_power:
            best = delta
            break
    return best if best is not None else float("nan")


def cramers_v(table: list) -> float:
    """table: list of rows (conditions), each a list of category counts.
    Descriptive effect size only -- no significance claim attached here."""
    n = sum(sum(row) for row in table)
    if n == 0:
        return 0.0
    row_totals = [sum(row) for row in table]
    col_totals = [sum(row[j] for row in table) for j in range(len(table[0]))]
    chi2 = 0.0
    for i, row in enumerate(table):
        for j, obs in enumerate(row):
            expected = row_totals[i] * col_totals[j] / n
            if expected > 0:
                chi2 += (obs - expected) ** 2 / expected
    k = min(len(table) - 1, len(table[0]) - 1)
    if k <= 0:
        return 0.0
    return math.sqrt(chi2 / (n * k))


def _chi2_stat(table: list) -> float:
    n = sum(sum(row) for row in table)
    if n == 0:
        return 0.0
    row_totals = [sum(row) for row in table]
    col_totals = [sum(row[j] for row in table) for j in range(len(table[0]))]
    chi2 = 0.0
    for i, row in enumerate(table):
        for j, obs in enumerate(row):
            expected = row_totals[i] * col_totals[j] / n
            if expected > 0:
                chi2 += (obs - expected) ** 2 / expected
    return chi2


def permutation_test_table(labels: list, categories: list, condition_labels: list,
                            trials: int = 2000, seed: int = 20260814) -> float:
    """Monte Carlo permutation test for association in the full condition x
    strategy table. `labels` is a list of (condition, strategy) pairs, one
    per lineage. Shuffles condition assignment `trials` times (holding the
    strategy sequence fixed), recomputes the chi-square statistic each
    time, and returns the fraction of permutations at least as extreme as
    observed -- descriptive only, per preregistration.md Sec 3."""
    conditions = [c for c, _ in labels]
    strategies = [s for _, s in labels]

    def build_table(conds, strats):
        table = [[0] * len(categories) for _ in condition_labels]
        cidx = {c: i for i, c in enumerate(condition_labels)}
        sidx = {s: j for j, s in enumerate(categories)}
        for c, s in zip(conds, strats):
            table[cidx[c]][sidx[s]] += 1
        return table

    observed = build_table(conditions, strategies)
    obs_chi2 = _chi2_stat(observed)

    rng = random.Random(seed)
    at_least_as_extreme = 0
    shuffled = list(conditions)
    for _ in range(trials):
        rng.shuffle(shuffled)
        table = build_table(shuffled, strategies)
        if _chi2_stat(table) >= obs_chi2 - 1e-9:
            at_least_as_extreme += 1
    return at_least_as_extreme / trials
