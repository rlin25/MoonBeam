# Pre-Registration

**Project:** Behavioral Signatures of Self-Continuity in a Memory-Augmented LLM
**Status:** written before any data collection begins
**Companion documents:** `project_design.md`, `project_specification.md`, `implementation_plan.md`,
`interface_contract.md`, `experimental_parameters.md`, `taxonomy_codebook.md`

---

## 1. Scope

This document commits, in advance of data collection, to the hypotheses, statistical tests, decision
rules, exclusion criteria, and stopping rule for this study. Its central confirmatory analysis is the
**Condition 2 vs. Condition 5 comparison**.

**Condition 6 (the first-person bridge) is not a second confirmatory test.** Its role is interpretive: it
constrains how a Condition 5 result may be described. §6 states the interpretive rules, fixed in advance,
so that the bridge cannot be used selectively after seeing which reading it favors.

Analyses of Conditions 1, 3, 4, and 7 are exploratory and descriptive. §10 states precisely what is and
is not covered by a confirmatory claim.

## 2. Hypotheses

### H1 — Cue effect (exploratory)

Supplying a recoverable basis for resolution increases the arbitration rate relative to no cue
(Conditions 3 and 4 vs. Condition 2). Directional. Treated as exploratory — see §8.

### H2 — Domain effect (confirmatory, central)

**The distribution of strategies under irreducible contradiction differs when the contradiction concerns
the model's own past choices (Condition 5) versus an arbitrary external fact (Condition 2).**

**H2 is explicitly non-directional, and this is deliberate.** Competing predictions exist and neither is
strong enough to justify committing to a direction:

- Chen, Su & Chiang (2026) find models correct external-labeled claims far more readily than
  self-labeled ones, which would predict *less* decisive action on self-referential content.
- Self-referential content may equally provoke *more* engagement, if the model treats claims about its
  own history as more consequential than claims about an arbitrary quantity.

With no settled theoretical reason to favor either, stating a directional prediction would manufacture
confidence that does not exist. The test is two-sided.

### H3 — Locus of the domain effect (interpretive, not confirmatory)

If H2 is supported, the effect is attributable either to **self-authorship** (the model made the choice)
or to **first-person framing** (the claim merely uses "I"). Condition 6 holds first-person framing and
conversational-history framing constant while removing self-authorship. Its position relative to
Conditions 2 and 5 adjudicates between these. Decision rules in §6.

### H2-exploratory — Ownership language

Ownership/continuity language (Pass 4) differs across Conditions 2, 5, and 6. Registered as anticipated
but exploratory, so that reporting it later is not mistaken for a post-hoc discovery. No confirmatory
claim will be made on this measure.

## 3. Primary Test

**Fisher's exact test (two-sided, α = 0.05) on a pre-specified collapsed 2×2 contingency table**,
comparing Condition 2 against Condition 5.

### Why Fisher's exact rather than chi-square

Chi-square's asymptotic approximation requires expected cell counts of roughly ≥5. At the planned N
spread across five strategy categories, several cells are likely to have expected counts below that
threshold, and chi-square on sparse tables inflates the false-positive rate. Fisher's exact makes no such
assumption.

### The pre-specified collapse

The full 2×5 table (condition × strategy) is underpowered at achievable N. The confirmatory test is
therefore run on a binary collapse, **fixed now, before any data exists:**

> **Did the lineage take a destructive or consolidating action on the seeded entries — that is, any
> `delete` or `update` targeting a seeded memory ID — at any point through step 7?**
>
> - **Yes:** consolidate-with-replacement, clear-without-replacement, arbitration
> - **No:** silent indefinite search, flag-and-defer

This collapse separates lineages that changed the memory state from those that left the contradiction
standing — the behaviorally meaningful distinction, and one that does not depend on the finer-grained
taxonomy remaining stable across content domains.

**This collapse is fixed and will not be changed after data inspection.** Selecting a collapse post hoc
is the most likely way this analysis would become indefensible.

### Secondary and descriptive analyses

- Full 2×5 contingency table, reported descriptively with a Monte Carlo permutation test (no
  distributional assumption) and Cramér's V as an effect size. **No confirmatory significance claim.**
- Raw proportion difference on the collapsed binary with a 95% Wilson confidence interval. **This leads
  the Results section**, ahead of the p-value — at this N the interval is more informative than the test.
- Per-condition strategy distributions, reported as counts with explicitly wide uncertainty.

## 4. Assumed Baseline Rate

The power analysis below assumes a baseline rate of **33%** for destructive/consolidating action in
Condition 2. This is an assumption, not an estimate derived from data.

**Sensitivity.** Power is highest when the baseline sits near 50% and falls as it approaches either
boundary. If the true Condition 2 rate is substantially lower (e.g. 10%) or higher (e.g. 70%), achieved
power for a given absolute difference will differ from the table in §5. Once Condition 2 data is
collected, achieved power will be recomputed against the observed baseline and reported alongside the
planned figures. Recomputing achieved power is a reporting step, not a decision point — it does not
license changing N, the test, or the collapse.

## 5. Power and Minimum Detectable Effect

Computed by simulation (Fisher's exact, two-sided, α = 0.05, 3000 trials per cell), against the assumed
33% baseline in §4.

| N per condition | Power to detect +22pp | Power to detect +32pp | MDE at 80% power |
|---|---|---|---|
| 30 | 0.31 | 0.62 | +38pp |
| 40 | 0.43 | 0.79 | +33pp |
| 50 | 0.54 | 0.88 | +28pp |

**Stated plainly: this study can only reliably detect a large domain effect.** At N=50 per condition the
minimum detectable effect at 80% power is a 28-percentage-point difference. Effects smaller than roughly
20pp will likely be missed, and a resulting null must be reported as underpowered rather than as evidence
of no effect.

**Planned N: 50 each for Conditions 2, 5, and 6.** If budget forces a reduction, these three are the last
place to cut — they carry the confirmatory test and its interpretation.

## 6. Interpretive Rules for Condition 6

Fixed in advance so the bridge cannot be read selectively after the fact. Applied only if H2 is supported
per §7; if H2 is not supported, Condition 6 is reported descriptively alongside the others and no locus
claim is made.

Let **d(2,5)** be the observed proportion difference between Conditions 2 and 5 on the collapsed binary,
and **d(2,6)** the difference between Conditions 2 and 6.

- **Self-authorship reading.** If |d(2,6)| < ⅓ × |d(2,5)| — the bridge sits close to Condition 2 — the
  effect is attributed to self-authorship. This is the strong result, and the one that speaks to the
  Track 5 question.
- **First-person-framing reading.** If |d(2,6)| > ⅔ × |d(2,5)| and d(2,6) shares the sign of d(2,5) — the
  bridge sits close to Condition 5 — the effect is attributed to first-person framing generally, not to
  self-reference. **This is a real finding but a substantially weaker and different one, and must be
  reported as such**, including in the abstract.
- **Ambiguous.** Any intermediate position, or a bridge that diverges from both in an unexpected
  direction. Reported as unresolved. No locus claim is made in either direction.

Condition 6 also receives its own Fisher's exact comparison against both Conditions 2 and 5, reported
with effect sizes and confidence intervals but **without significance claims** (§8).

## 7. Decision Rules for H2

Committed in advance. Each outcome has a pre-specified interpretation.

**Positive finding (H2 supported).** Both must hold:
- Fisher's exact p < 0.05 on the collapsed 2×2, **and**
- observed proportion difference ≥ 25pp with a 95% Wilson CI excluding zero.

Both are required because significance alone at this N could rest on a single cell. Direction, effect
size, the full strategy distribution, and the Condition 6 interpretive reading (§6) are reported
alongside.

**Interpretable null (H2 not supported, meaningfully).** All of:
- p ≥ 0.05, **and**
- observed difference < 10pp, **and**
- the 95% CI excludes effects larger than the MDE for the achieved N.

This is a genuine, reportable contribution: it would indicate non-arbitration behavior is domain-general
— that the model does not treat contradictions about its own history differently from arbitrary ones —
which bears directly on the study's founding question.

**Mixed / underpowered.** p ≥ 0.05 with an observed difference between 10pp and 25pp, or a CI spanning
both trivial and substantial effects. At the planned N this is a likely outcome if a moderate real effect
exists. It will be reported as underpowered, with the minimum detectable effect stated explicitly, and
**no directional claim will be made.**

## 8. Multiple Comparisons

**Exactly one confirmatory test:** H2's collapsed 2×2 Fisher's exact at α = 0.05.

Everything else — H1's pairwise comparisons, Condition 6's comparisons against Conditions 2 and 5, the
full 2×5 tables, ownership-language patterns, Condition 1's initiation rate, Condition 7's eligibility and
trigger outcomes, and both counterbalance splits — is **exploratory**, reported with effect sizes and
confidence intervals but **without significance claims**. No correction is applied because no family-wise
confirmatory claim is made beyond the single pre-specified test.

## 9. Exclusions, Stopping Rule, Counterbalancing, and Taxonomy Handling

### Exclusions

- **Errored lineages** (API failure, unparseable tool call) are excluded from all analyses and reported
  separately with counts and error types.
- **Coherence-check failures** are excluded from LLM-judge passes (2 and 4) only. They remain in the
  mechanical action taxonomy and in the primary collapsed analysis, since a malformed *response* does not
  invalidate a logged *action*.
- No other exclusions. Lineages are not dropped for producing unexpected or hard-to-classify behavior.

### Stopping rule

**N is fixed at the targets in §5 and in `project_specification.md`.** Data collection stops there
regardless of results. No interim analysis will be conducted to decide whether to collect more, and no
additional lineages will be run to reach a target count of any particular outcome. If usable N falls
below target due to errors, the shortfall is reported rather than backfilled.

### Counterbalancing

Conditions 2, 5, and 6 are seed-order counterbalanced; Conditions 3 and 4 are cue-direction
counterbalanced (`project_design.md` §7). The primary analysis **pools across counterbalance arms**. Each
arm's distribution is reported separately as a robustness check. Counterbalancing halves effective
per-cell N and is **not powered to detect order or cue-direction effects** — if the two arms differ
visibly, that is reported as an observation requiring further work, never as a finding.

### New taxonomy categories

`taxonomy_codebook.md` §4 permits assigning `other` when a lineage fits none of the five defined
strategies, and permits reporting a recurring `other` pattern as a candidate new category. Because that
is a researcher degree of freedom, its statistical handling is fixed here:

- A new or `other` category is assigned to the confirmatory collapse **by the mechanical criterion in §3**
  — did the lineage issue a `delete` or `update` targeting a seeded memory ID? This follows from the
  collapse definition and is not a fresh judgment call.
- Emergence of a recurring new pattern is reported as a finding in its own right.
- Category definitions are never merged, split, or redefined retroactively to improve comparability.

## 10. What This Pre-Registration Does Not Cover

- **Conditions 1, 3, 4, and 7.** Their analyses are exploratory or descriptive and carry no confirmatory
  claim.
- **Condition 6's comparisons**, which are interpretive per §6 rather than confirmatory.
- **The strategy taxonomy itself.** The five categories in `taxonomy_codebook.md` are an a priori frame,
  not a validated scheme. The `other` category exists precisely because the frame may prove incomplete.
- **Precise proportions within the taxonomy.** Reaching a ±15pp CI on each bucket would require N≈140-170
  per condition, which is not attempted (`project_design.md` §6).
- **Order and cue-direction effects**, which are reported but not powered.
- **Cross-model generalization.** Single model, single provider. Cross-model work would require its own
  pre-registration.

## 11. Deviations Policy

Any deviation from this document — a changed test, a changed collapse, a changed N, an added exclusion,
a changed experimental parameter, a changed interpretive threshold — will be reported explicitly in the
final write-up, with the deviation, its reason, and its timing relative to data inspection stated
plainly. Undisclosed deviation from a pre-registration is worse than having no pre-registration at all.
