# Pre-Registration

**Project:** Behavioral Signatures of Self-Continuity in a Memory-Augmented LLM
**Status:** written before any Condition B or Condition C data has been collected. A small prior pilot
exists and is disclosed in full in §4.
**Companion documents:** `project_design.md`, `implementation.md`, `interface_contract.md`,
`experimental_parameters.md`, `taxonomy_codebook.md`

---

## 1. Scope

This document commits, in advance of the data collection it governs, to the hypotheses, statistical test,
decision rules, exclusion criteria, and stopping rule for this study. Its central confirmatory analysis is
the **Condition A vs. Condition B comparison**.

**Condition C (the first-person bridge) is not a second confirmatory test.** Its role is interpretive: it
constrains how a Condition B result may be described. §6 states the interpretive rules, fixed in advance,
so the bridge cannot be read selectively after seeing which reading it favors.

§10 states precisely what is and is not covered by a confirmatory claim.

## 2. Hypotheses

### H1 — Domain effect (confirmatory, central)

**The distribution of strategies under irreducible contradiction differs when the contradiction concerns
the model's own past choices (Condition B) versus an arbitrary external fact (Condition A).**

**H1 is explicitly non-directional, and this is deliberate.** Competing predictions exist and neither is
strong enough to justify committing to a direction:

- Chen, Su & Chiang (2026) find models correct external-labeled claims far more readily than
  self-labeled ones, which would predict *less* decisive action on self-referential content.
- Self-referential content may equally provoke *more* engagement, if the model treats claims about its own
  history as more consequential than claims about an arbitrary quantity.

With no settled theoretical reason to favor either, stating a directional prediction would manufacture
confidence that does not exist. The test is two-sided.

### H2 — Locus of the effect (interpretive, not confirmatory)

If H1 is supported, the effect is attributable either to **self-authorship** (the model made the choice)
or to **first-person framing** (the claim merely uses "I"). Condition C holds first-person framing and
conversational-history framing constant while removing self-authorship. Its position relative to
Conditions A and B adjudicates between these. Decision rules in §6.

## 3. Primary Test

**Fisher's exact test (two-sided, α = 0.05) on a pre-specified collapsed 2×2 contingency table**,
comparing Condition A against Condition B.

### Why Fisher's exact rather than chi-square

Chi-square's asymptotic approximation requires expected cell counts of roughly ≥5. Spread across five
strategy categories, several cells are likely to fall below that threshold — the prior pilot (§4) had
three categories at a count of one. Chi-square on sparse tables inflates the false-positive rate.
Fisher's exact makes no such assumption.

### The pre-specified collapse

The full contingency table across five strategy categories is underpowered at achievable N. The
confirmatory test is therefore run on a binary collapse, **fixed before any Condition B or C data
exists:**

> **Did the lineage take a destructive or consolidating action on the seeded entries — that is, any
> `delete` or `update` targeting a seeded memory ID — at any point through step 7?**
>
> - **Yes:** consolidate-with-replacement, clear-without-replacement, arbitration
> - **No:** silent indefinite search, flag-and-defer

This collapse separates lineages that changed the memory state from those that left the contradiction
standing — the behaviorally meaningful distinction, and one that does not depend on the finer-grained
taxonomy remaining stable across content domains.

**This collapse will not be changed after data inspection.** Selecting a collapse post hoc is the most
likely way this analysis would become indefensible.

### Secondary and descriptive analyses

- Full 3×5 contingency table across all conditions, reported descriptively with a Monte Carlo permutation
  test and Cramér's V. **No confirmatory significance claim.**
- Raw proportion difference on the collapsed binary with a 95% Wilson confidence interval. **This leads
  the Results section**, ahead of the p-value — at this N the interval is more informative than the test.
- Per-condition strategy distributions, reported as counts with explicitly wide uncertainty.
- Per-arm counterbalance splits, reported as a robustness check (§9).

## 4. Prior Pilot and Baseline Assumption

### What prior data exists

A single small pilot was run under an early version of this protocol: **six lineages of the
arbitrary-contradiction condition** (the design now designated Condition A), pre-seeded with two
contradictory `x + y` claims and full tool access. Of those six lineages, **two took a destructive or
consolidating action on the seeded entries and four did not** — a 33% rate on the collapse binary defined
in §3.

Its 95% Wilson confidence interval is approximately **[9%, 70%]**. At N=6 this interval is so wide that it
constrains almost nothing. The 33% figure is used below as a **planning placeholder**, not as an estimate
of the true rate.

Also observed in that pilot: behavior distributed across four of the five strategy categories, with three
categories at a count of one. This informed the decision to use Fisher's exact rather than chi-square
(§3) and to treat the taxonomy as descriptive rather than as an estimated distribution
(`project_design.md` §6).

### What that pilot does not establish

The pilot ran the arbitrary-contradiction condition only. **No Condition B or Condition C lineage has been
run in any form.** The comparison this document pre-registers is therefore genuinely untested, and no data
bearing on H1 or H2 exists.

### Data from other protocols, and why it is excluded

Earlier work in this project measured a different setup entirely — memory *empty* at step 1, with a
neutral self-directed elicitation, testing whether the model spontaneously initiates a memory write. That
work is not a baseline for this study. Its protocol differs in the two respects that most plausibly drive
action rates: memory state at step 1 (empty vs. pre-seeded with a contradiction) and the presence or
absence of anything to resolve. Rates from that setup are not transferable here and are not used.

### Sequencing, and the degree of freedom it creates

Condition A will be run first, at full N. Its observed rate supersedes the 33% placeholder for all
power reporting.

**This creates a researcher degree of freedom that is acknowledged here rather than discovered later:**
inspecting Condition A's strategy distribution before finalizing the classifier means the taxonomy could
in principle be shaped by observed data. Three constraints bound this:

- The five strategy categories and the decision procedure are already fixed in `taxonomy_codebook.md` and
  are not revised in response to Condition A.
- The collapse binary in §3 is fixed and is not revised at all.
- Any codebook amendment — including one prompted by Condition A — is disclosed per §9 with its reason
  and its timing relative to data inspection.

Condition A is not a pilot for Conditions B and C. It is one of the three conditions, run first for
operational reasons, and its data enters the confirmatory analysis unchanged.

## 5. Power and Minimum Detectable Effect

Computed by simulation (Fisher's exact, two-sided, α = 0.05, 3000 trials per cell), against the 33%
planning placeholder from §4.

| N per condition | Power to detect +22pp | Power to detect +32pp | MDE at 80% power |
|---|---|---|---|
| 30 | 0.31 | 0.62 | +38pp |
| 40 | 0.43 | 0.79 | +33pp |
| 50 | 0.54 | 0.88 | +28pp |

**Stated plainly: this study can only reliably detect a large domain effect.** At N=50 the minimum
detectable effect at 80% power is a 28-percentage-point difference. Effects smaller than roughly 20pp will
likely be missed, and a resulting null must be reported as underpowered rather than as evidence of no
effect.

**Sensitivity.** Power is highest when the baseline sits near 50% and falls toward either boundary. A
baseline substantially below 33% would *raise* power for a given absolute difference; a baseline near 50%
would lower it. Once Condition A is complete, achieved power will be recomputed against its observed rate
and reported alongside these planned figures. **Recomputing achieved power is a reporting step, not a
decision point** — it does not license changing N, the test, or the collapse.

**N = 50 per condition, 150 lineages total.**

## 6. Interpretive Rules for Condition C

Fixed in advance so the bridge cannot be read selectively after the fact. Applied only if H1 is supported
per §7; if H1 is not supported, Condition C is reported descriptively and no locus claim is made.

Let **d(A,B)** be the observed proportion difference between Conditions A and B on the collapsed binary,
and **d(A,C)** the difference between Conditions A and C.

- **Self-authorship reading.** If |d(A,C)| < ⅓ × |d(A,B)| — the bridge sits close to Condition A — the
  effect is attributed to self-authorship. This is the strong result, and the one that speaks to the
  Track 5 question.
- **First-person-framing reading.** If |d(A,C)| > ⅔ × |d(A,B)| and d(A,C) shares the sign of d(A,B) — the
  bridge sits close to Condition B — the effect is attributed to first-person framing generally, not to
  self-reference. **This is a real finding but substantially weaker and different, and must be reported as
  such, including in the abstract.**
- **Ambiguous.** Any intermediate position, or a bridge diverging from both in an unexpected direction.
  Reported as unresolved. No locus claim in either direction.

Condition C also receives Fisher's exact comparisons against both A and B, reported with effect sizes and
confidence intervals but **without significance claims** (§8).

## 7. Decision Rules for H1

Committed in advance.

**Positive finding (H1 supported).** Both must hold:
- Fisher's exact p < 0.05 on the collapsed 2×2, **and**
- observed proportion difference ≥ 25pp with a 95% Wilson CI excluding zero.

Both are required because significance alone at this N could rest on a single cell. Direction, effect
size, the full strategy distribution, and the Condition C interpretive reading (§6) are reported alongside.

**Interpretable null (H1 not supported, meaningfully).** All of:
- p ≥ 0.05, **and**
- observed difference < 10pp, **and**
- the 95% CI excludes effects larger than the MDE for the achieved N.

This is a genuine, reportable contribution: it would indicate non-arbitration behavior is domain-general —
that the model does not treat contradictions about its own history differently from arbitrary ones — which
bears directly on the study's founding question.

**Mixed / underpowered.** p ≥ 0.05 with an observed difference between 10pp and 25pp, or a CI spanning
both trivial and substantial effects. At this N this is a likely outcome if a moderate real effect exists.
Reported as underpowered, with the MDE stated explicitly, and **no directional claim made.**

## 8. Multiple Comparisons

**Exactly one confirmatory test:** H1's collapsed 2×2 Fisher's exact at α = 0.05.

Everything else — Condition C's comparisons against A and B, the full 3×5 table, per-arm counterbalance
splits, and any descriptive breakdown — is **exploratory**, reported with effect sizes and confidence
intervals but **without significance claims**. No correction is applied because no family-wise confirmatory
claim is made beyond the single pre-specified test.

## 9. Exclusions, Stopping Rule, Counterbalancing, and Taxonomy Handling

### Exclusions

- **Errored lineages** (API failure, unparseable tool call) are excluded from all analyses and reported
  separately with counts and error types.
- No other exclusions. Lineages are not dropped for producing unexpected or hard-to-classify behavior.
  Because this study uses no LLM judge, there is no coherence pre-check and no judgment-based exclusion
  path.

### Stopping rule

**N is fixed at 50 per condition.** Data collection stops there regardless of results. No interim analysis
will be conducted to decide whether to collect more, and no additional lineages will be run to reach a
target count of any particular outcome. If usable N falls below target due to errors, the shortfall is
reported rather than backfilled.

**Condition A being run first does not constitute an interim analysis.** Its results do not determine
whether Conditions B and C run, at what N, or under what test.

### Counterbalancing

All three conditions are seed-order counterbalanced, deterministically by lineage index
(`experimental_parameters.md` §5). The primary analysis **pools across arms**. Each arm's distribution is
reported separately as a robustness check. Counterbalancing halves effective per-cell N and is **not
powered to detect an order effect** — if arms differ visibly, that is reported as an observation requiring
further work, never as a finding.

### New taxonomy categories

`taxonomy_codebook.md` §4 permits assigning `other` when a lineage fits none of the five defined
strategies, and permits reporting a recurring `other` pattern as a candidate new category. Because that is
a researcher degree of freedom, its statistical handling is fixed here:

- A new or `other` category is assigned to the confirmatory collapse **by the mechanical criterion in §3**
  — did the lineage issue a `delete` or `update` targeting a seeded memory ID? This follows from the
  collapse definition and is not a fresh judgment call.
- Emergence of a recurring new pattern is reported as a finding in its own right.
- Category definitions are never merged, split, or redefined retroactively to improve comparability.

### Codebook amendment

If held-out human coding (`project_design.md` §8) or inspection of Condition A surfaces an ambiguity
resolved by amending `taxonomy_codebook.md`, the amendment, its reason, and its timing relative to data
inspection are reported in full. Amendments may clarify an ambiguous case; they may not redefine a
category in a way that changes already-assigned labels without those relabelings being disclosed
individually.

## 10. What This Pre-Registration Does Not Cover

- **Condition C's comparisons**, which are interpretive per §6 rather than confirmatory.
- **The strategy taxonomy itself.** The five categories in `taxonomy_codebook.md` are an a priori frame,
  not a validated scheme. The `other` category exists precisely because the frame may prove incomplete.
- **Precise proportions within the taxonomy.** Reaching a ±15pp CI on each bucket would require N≈140-170
  per condition, which is not attempted.
- **Order effects**, which are reported but not powered.
- **Anything listed as scoped out** in `project_design.md` §11.
- **Cross-model generalization.** Single model, single provider.

## 11. Deviations Policy

Any deviation from this document — a changed test, a changed collapse, a changed N, an added exclusion, a
changed experimental parameter, a changed interpretive threshold — will be reported explicitly in the final
write-up, with the deviation, its reason, and its timing relative to data inspection stated plainly.
Undisclosed deviation from a pre-registration is worse than having no pre-registration at all.
