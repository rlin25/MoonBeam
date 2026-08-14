from __future__ import annotations
import math
import numpy as np
import pandas as pd
from scipy.stats import fisher_exact, chi2_contingency
from statsmodels.stats.proportion import proportion_confint


def wilson_interval(x: int, n: int, alpha: float = 0.05) -> tuple[float,float]:
    if n == 0:
        return (float('nan'), float('nan'))
    lo, hi = proportion_confint(x, n, alpha=alpha, method='wilson')
    return float(lo), float(hi)


def newcombe_wilson_diff(x1: int, n1: int, x2: int, n2: int, alpha: float = 0.05) -> tuple[float,float]:
    """Newcombe hybrid-score CI for p1-p2 using Wilson score intervals."""
    if n1 == 0 or n2 == 0:
        return (float('nan'), float('nan'))
    p1, p2 = x1/n1, x2/n2
    l1,u1 = wilson_interval(x1,n1,alpha)
    l2,u2 = wilson_interval(x2,n2,alpha)
    lower = (p1-p2) - math.sqrt((p1-l1)**2 + (u2-p2)**2)
    upper = (p1-p2) + math.sqrt((u1-p1)**2 + (p2-l2)**2)
    return max(-1.0, lower), min(1.0, upper)


def ensure_confirmatory_dv(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with the current confirmatory DV: arbitration/non_arbitration.

    The DV is mechanically derived from the final taxonomy label.  The older
    took_action/no_action field is preserved as a descriptive/action variable
    but is not used for confirmatory inference.
    """
    out = df.copy()
    if 'strategy' not in out.columns:
        raise ValueError('strategy column is required to derive arbitration DV')
    out['confirmatory_dv'] = np.where(out['strategy'].astype(str).str.strip().str.lower().eq('arbitration'),
                                     'arbitration', 'non_arbitration')
    return out


def arbitration_comparison(df: pd.DataFrame, cond1: str, cond2: str) -> dict:
    """Compare arbitration rates, reporting cond1 - cond2.

    For the central A-vs-B test this means A-B, so 85% vs 25% is +60pp.
    """
    d = ensure_confirmatory_dv(df)
    a = d[d.condition == cond1]
    b = d[d.condition == cond2]
    x1 = int((a.confirmatory_dv == 'arbitration').sum()); n1 = len(a)
    x2 = int((b.confirmatory_dv == 'arbitration').sum()); n2 = len(b)
    table = np.array([[x1, n1-x1], [x2, n2-x2]])
    odds, p = fisher_exact(table, alternative='two-sided')
    diff = x1/n1 - x2/n2 if n1 and n2 else float('nan')
    ci = newcombe_wilson_diff(x1,n1,x2,n2)
    return {
        'dv': 'arbitration_vs_non_arbitration',
        'comparison': f'{cond1}-{cond2}',
        'condition_1': cond1, 'condition_2': cond2,
        'n1': n1, 'arbitrations1': x1, 'rate1': x1/n1 if n1 else float('nan'),
        'n2': n2, 'arbitrations2': x2, 'rate2': x2/n2 if n2 else float('nan'),
        'difference': diff, 'ci95_low': ci[0], 'ci95_high': ci[1],
        'odds_ratio': float(odds), 'fisher_p_two_sided': float(p),
        'table': table.tolist(),
    }


def action_comparison_descriptive(df: pd.DataFrame, cond1: str, cond2: str) -> dict:
    """Retired took_action/no_action collapse, retained only as a descriptive diagnostic."""
    a = df[df.condition == cond1]; b = df[df.condition == cond2]
    x1 = int((a.collapse_binary == 'took_action').sum()); n1=len(a)
    x2 = int((b.collapse_binary == 'took_action').sum()); n2=len(b)
    table=np.array([[x1,n1-x1],[x2,n2-x2]])
    odds,p=fisher_exact(table,alternative='two-sided')
    diff=x1/n1-x2/n2 if n1 and n2 else float('nan')
    ci=newcombe_wilson_diff(x1,n1,x2,n2)
    return {'dv':'retired_took_action_vs_no_action','comparison':f'{cond1}-{cond2}',
            'n1':n1,'actions1':x1,'rate1':x1/n1 if n1 else float('nan'),
            'n2':n2,'actions2':x2,'rate2':x2/n2 if n2 else float('nan'),
            'difference':diff,'ci95_low':ci[0],'ci95_high':ci[1],
            'odds_ratio':float(odds),'fisher_p_two_sided':float(p),'table':table.tolist()}

# Backward-compatible name now points to the CURRENT confirmatory DV.
def collapsed_comparison(df: pd.DataFrame, cond1: str, cond2: str) -> dict:
    return arbitration_comparison(df, cond1, cond2)


def cramers_v(table: np.ndarray) -> float:
    table=np.asarray(table,dtype=float)
    keep_r=table.sum(axis=1)>0; keep_c=table.sum(axis=0)>0
    reduced=table[np.ix_(keep_r,keep_c)]; n=reduced.sum()
    if n==0 or min(reduced.shape)<2: return 0.0 if n>0 else float('nan')
    chi2,_,_,_=chi2_contingency(reduced,correction=False)
    return float(math.sqrt((chi2/n)/max(1,min(reduced.shape[0]-1,reduced.shape[1]-1))))


def permutation_3x5(df: pd.DataFrame, strategies: list[str], trials: int=10000, seed: int=20260814) -> dict:
    core=df[df.strategy.isin(strategies)].copy()
    observed=pd.crosstab(core.condition,core.strategy).reindex(index=['A','B','C'],columns=strategies,fill_value=0)
    table=observed.to_numpy()
    if table.sum()==0: return {'table':observed.to_dict(),'cramers_v':float('nan'),'permutation_p':float('nan'),'trials':trials}
    obs_v=cramers_v(table); rng=np.random.default_rng(seed); labels=core.condition.to_numpy().copy(); strats=core.strategy.to_numpy(); ge=0
    for _ in range(trials):
        perm=rng.permutation(labels)
        tmp=pd.crosstab(pd.Series(perm),pd.Series(strats)).reindex(index=['A','B','C'],columns=strategies,fill_value=0).to_numpy()
        if cramers_v(tmp)>=obs_v-1e-15: ge+=1
    return {'table':observed.to_dict(),'cramers_v':obs_v,'permutation_p':(ge+1)/(trials+1),'trials':trials}


def simulate_power_rates(p1: float, p2: float, n1: int=100, n2: int|None=None, trials: int=3000, alpha: float=.05, seed: int=20260814) -> float:
    if n2 is None: n2=n1
    if not (0<=p1<=1 and 0<=p2<=1): return float('nan')
    rng=np.random.default_rng(seed); hits=0
    for _ in range(trials):
        x1=rng.binomial(n1,p1); x2=rng.binomial(n2,p2)
        _,p=fisher_exact([[x1,n1-x1],[x2,n2-x2]],alternative='two-sided')
        hits += p < alpha
    return hits/trials


def achieved_mde(baseline: float, n: int=100, target_power: float=.80, trials: int=3000, step: float=.01, seed: int=20260814) -> dict:
    """Smallest absolute rate difference detectable at target power in either feasible direction."""
    rows=[]; best=None
    for i,e in enumerate(np.arange(step,1+step/2,step)):
        candidates=[]
        if baseline-e>=0: candidates.append(('lower',baseline-e))
        if baseline+e<=1: candidates.append(('higher',baseline+e))
        if not candidates: continue
        vals=[]
        for j,(direction,p2) in enumerate(candidates):
            power=simulate_power_rates(baseline,p2,n,n,trials=trials,seed=seed+i*3+j)
            vals.append((direction,p2,power))
        max_power=max(v[2] for v in vals)
        rows.append({'effect':float(e),'directions':[{'direction':d,'comparison_rate':p,'power':pw} for d,p,pw in vals],'max_power':max_power})
        if best is None and max_power>=target_power:
            chosen=max(vals,key=lambda x:x[2])
            best={'mde':float(e),'direction':chosen[0],'comparison_rate':chosen[1],'power_at_mde':chosen[2]}
            break
    return {'baseline':baseline,'n_per_condition':n,'target_power':target_power,**(best or {'mde':None,'direction':None,'comparison_rate':None,'power_at_mde':None}),'grid':rows}


def observed_power(p1: float,p2: float,n1: int,n2: int,trials: int=3000) -> float:
    return simulate_power_rates(p1,p2,n1,n2,trials=trials)
