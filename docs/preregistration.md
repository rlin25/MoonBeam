# Pre-Registration

**Project:** Behavioral Signatures of Self-Continuity in a Memory-Augmented LLM
**Status:** written before any data has been collected under this document's confirmatory test. A
150-lineage prior run exists under an earlier version of this protocol's confirmatory test and is
disclosed in full in §4, including why that earlier test is not being reused and how its data informed
the design below.
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

**Whether the model resolves an irreducible contradiction by arbitrating — selecting one claim and
keeping it as the sole operative record — differs when the contradiction concerns the model's own past
choices (Condition B) versus an arbitrary external fact (Condition A).**

**H1 is explicitly non-directional, and this is deliberate.** Competing predictions exist and neither is
strong enough to justify committing to a direction:

- Chen, Su & Chiang (2026) find models correct external-labeled claims far more readily than
  self-labeled ones, which would predict a *lower* arbitration rate on self-referential content.
- Self-referential content may equally provoke a *higher* arbitration rate, if the model treats claims
  about its own history as more consequential — more worth resolving decisively — than claims about an
  arbitrary quantity.

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
strategy categories, several cells are likely to fall below that threshold — the prior 150-lineage run
(§4) had two categories (flag-and-defer, consolidate-with-replacement) at a count of **zero** across all
three conditions combined. Chi-square on sparse tables inflates the false-positive rate. Fisher's exact
makes no such assumption.

### The pre-specified collapse

The full contingency table across five strategy categories is underpowered at achievable N. The
confirmatory test is therefore run on a binary collapse:

> **Did the lineage arbitrate through step 7** — that is, does its final database state contain exactly
> one operative claim, drawn from the seeded entries, with the other discarded or superseded (the
> `arbitration` category defined in `taxonomy_codebook.md` §1.5, computed mechanically from the action
> log and final database state, never from prose)?
>
> - **Yes:** arbitration
> - **No:** silent indefinite search, flag-and-defer, consolidate-with-replacement,
>   clear-without-replacement, other

This collapse separates lineages that committed to one version of the contested record from every other
outcome — declining to touch it, flagging it without choosing, or discarding both claims outright. It is
the behaviorally meaningful distinction for this study's question (does the model treat its own record as
something to take a stance on), and — as with the prior collapse — it does not depend on the
finer-grained taxonomy remaining stable across content domains.

**This collapse will not be changed after Condition B or C data exists under this document.** Selecting a
collapse after seeing the comparison it will be tested on is the most likely way this analysis would
become indefensible. §4 discloses, in full, that this specific collapse was chosen only after inspecting
the prior run's complete descriptive results across all three conditions — a real degree of freedom, named
directly rather than minimized.

### Secondary and descriptive analyses

- Full 3×5 contingency table across all conditions, reported descriptively with a Monte Carlo permutation
  test and Cramér's V. **No confirmatory significance claim.**
- Raw proportion difference on the collapsed binary with a 95% Wilson confidence interval. **This leads
  the Results section**, ahead of the p-value.
- Per-condition strategy distributions, reported as counts with explicitly wide uncertainty.
- Per-arm counterbalance splits, reported as a robustness check (§9).

## 4. Prior Pilot and Baseline Assumption

### What prior data exists, and why its own confirmatory test is not being reused

A full 150-lineage run (N=50 per condition, all three conditions) was completed under an earlier version
of this protocol, whose confirmatory collapse was **took_action vs. no_action** — did the lineage issue
any `delete` or `update` against a seeded entry at all. That collapse turned out to be uninformative: all
three conditions saturated near-ceiling on it (Condition A 98%, Conditions B and C 100%), leaving
essentially no room for a domain effect to show up on that specific measure. The Fisher's exact result on
that binary was p = 1.0 with a 2-point observed difference — not a null finding about the underlying
question, but a ceiling artifact of a collapse that turned out not to separate the conditions.

**This document is a fresh confirmatory test, not a reanalysis of that run.** The prior collapse is
retired, not reinterpreted; no measurement from that run enters this document's confirmatory analysis.

### What the prior run's data shows on the metric this document actually tests

Although arbitration was not the confirmatory measure when that data was collected, the full strategy
taxonomy — including arbitration — was scored mechanically for every lineage regardless (per
`taxonomy_codebook.md`, unaffected by which collapse governs the confirmatory pass). Its arbitration rates
by condition:

| Condition | Arbitration rate (N=50) |
|---|---|
| A (arbitrary contradiction) | 43/50 = 86% |
| B (self-referential contradiction) | 11/50 = 22% |
| C (first-person bridge) | 48/50 = 96% |

This is disclosed here as prior pilot data informing the design below — the same role the original
6-lineage pilot played for the prior preregistration — not as data bearing on H1 or H2 in this document.
**No Condition A, B, or C lineage has been run under this document's own confirmatory test.** The
comparison this document pre-registers is genuinely untested by new data; only the design choices below
(the collapse itself, the baseline used for power planning, N) are informed by the prior run.

### The degree of freedom this creates, named directly

The prior preregistration stated its own collapse "is fixed and is not revised at all," and its
Deviations Policy required any change to be disclosed explicitly rather than smoothed over. This document
**is** that disclosure, for a deviation larger than anything the prior document's own sequencing caveat
anticipated: that caveat covered inspecting Condition A alone, before B or C existed, to set a power
baseline — not inspecting all three conditions' complete results to choose which measure counts as
confirmatory in the first place. The choice of arbitration-vs-not as the new collapse was made after
seeing that exact pattern in the full 150-lineage descriptive breakdown. That is a real, sizable
researcher degree of freedom, and it is named as such here rather than downplayed as routine iteration.
Three things bound it going forward, mirroring the discipline the prior document applied to its own
smaller version of this problem:

- The collapse in §3 is now fixed for this document and will not be revised again in response to data
  collected under it.
- `taxonomy_codebook.md`'s five categories and decision procedure are unchanged by this revision — the
  same mechanical scoring that produced the numbers above will score the new data, so nothing about how
  "arbitration" is defined was tuned to produce a particular result.
- Any further amendment is disclosed per §9 with its reason and timing relative to data inspection, exactly
  as before.

### Data from other protocols, and why it is excluded

Earlier work in this project measured spontaneous initiation from empty memory under a neutral
elicitation — a different setup whose rates are not transferable here, for the same reasons the prior
preregistration excluded it. Not used.

### Sequencing

Condition A runs first, at full N, for the same operational reasons as before — it exercises the harness
at scale and is one of the three conditions, not a gate. Its data enters the confirmatory analysis
unchanged regardless of its observed rate.

## 5. Power and Minimum Detectable Effect

Computed by simulation (Fisher's exact, two-sided, α = 0.05, 3000 trials per cell), against the **86%
observed Condition A arbitration rate** from the prior 150-lineage run (§4) — not a placeholder, since
that rate is now real data on the actual metric this document tests.

**Direction matters here in a way it didn't for the prior document's power table.** With a baseline near
ceiling, there is almost no room to detect an *increase* — the whole point of interest is whether
Condition B's rate is *lower*, which the prior run's own data already suggests by a wide margin (22% vs.
86%). The table below is therefore computed for the decrease direction, matching the effect this study
is actually positioned to detect:

| N per condition | Power to detect −25pp | Power to detect −32pp | MDE at 80% power |
|---|---|---|---|
| 50 | 0.77 | 0.92 | −26pp |
| 75 | 0.92 | 0.99 | −21pp |
| 100 | 0.97 | 1.00 | −18pp |

**At N=100, this study is well powered against the pre-registered ±25pp decision threshold (§7)** — 0.97
power to detect a 25-point decrease, and an 18-point minimum detectable effect at 80% power, comfortably
inside the ~64-point difference the prior run's descriptive data suggests. This is a substantially
stronger position than the prior document's own N=50 table (28pp MDE against a 33% placeholder baseline)
— both because N increased and because the working baseline is now real data rather than an N=6 planning
figure.

**Sensitivity.** This power table assumes the true Condition A rate is close to the prior run's observed
86%; if the true rate differs, achieved power will differ accordingly. Once this document's own Condition
A completes, achieved power will be recomputed against *its* observed rate and reported alongside these
planned figures — a reporting step, not a decision point, exactly as before: it does not license changing
N, the test, or the collapse.

**N = 100 per condition, 300 lineages total.**

## 6. Interpretive Rules for Condition C

Fixed in advance so the bridge cannot be read selectively after the fact. Applied only if H1 is supported
per §7; if H1 is not supported, Condition C is reported descriptively and no locus claim is made.

Let **d(A,B)** be the observed proportion difference between Conditions A and B on the collapsed binary
(§3), and **d(A,C)** the difference between Conditions A and C.

- **Self-authorship reading.** If |d(A,C)| < ⅓ × |d(A,B)| — the bridge sits close to Condition A — the
  effect is attributed to self-authorship. This is the strong result, and the one that speaks to the
  Track 5 question.
- **First-person-framing reading.** If |d(A,C)| > ⅔ × |d(A,B)| and d(A,C) shares the sign of d(A,B) — the
  bridge sits close to Condition B — the effect is attributed to first-person framing generally, not to
  self-reference. **This is a real finding but substantially weaker and different, and must be reported as
  such, including in the abstract.**
- **Ambiguous.** Any intermediate position, or a bridge diverging from both in an unexpected direction.
  Reported as unresolved. No locus claim in either direction.

For context, not as a substitute for the confirmatory data: the prior run's descriptive arbitration rates
(§4) already sit well inside the self-authorship zone — |d(A,C)| ≈ 10pp against |d(A,B)| ≈ 64pp, a ratio
of roughly 0.16, well under ⅓. This is disclosed as prior information, not treated as if it already
resolved H2 under this document's own test.

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

This is a genuine, reportable contribution: it would indicate arbitration behavior is domain-general —
that the model does not treat contradictions about its own history differently from arbitrary ones — which
bears directly on the study's founding question.

**Mixed / underpowered.** p ≥ 0.05 with an observed difference between 10pp and 25pp, or a CI spanning
both trivial and substantial effects. Reported as underpowered, with the MDE stated explicitly, and **no
directional claim made.**

**Ceiling or floor saturation.** If either condition's arbitration rate lands at or within a few points of
0% or 100% such that the achieved-power recomputation (§5) produces an undefined or near-zero MDE in the
relevant direction, that is reported as a limitation of this collapse under the observed data — plainly,
the way the prior document's saturated took_action rate was reported here in §4 — rather than forced into
one of the three verdicts above. This did not occur in the prior run's descriptive arbitration data (rates
of 22%, 86%, 96% all sit well clear of either boundary), so it is not the expected outcome, but the
decision rules should not silently produce a false verdict if it happens anyway.

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

**N is fixed at 100 per condition.** Data collection stops there regardless of results. No interim
analysis will be conducted to decide whether to collect more, and no additional lineages will be run to
reach a target count of any particular outcome. If usable N falls below target due to errors, the
shortfall is reported rather than backfilled.

A small mechanical trial (N=25 per condition) precedes the full run, solely to verify the revised harness
executes correctly after this document's changes — no errors, well-formed transcripts and scoring output.
**The trial's observed arbitration rate is not inspected and is not used to decide whether to proceed to
N=100.** That decision is made by this document, in advance. This is distinct from, and does not weaken,
the disclosure in §4: §4 discloses that the *choice of collapse* was informed by the prior 150-lineage
run's results; this trial is a code-correctness check only, on fresh data that is never read for content.

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
  — does the lineage's final state contain exactly one operative claim drawn from the seeded entries? This
  follows from the collapse definition and is not a fresh judgment call.
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
  per condition, which is not attempted even at N=100.
- **Order effects**, which are reported but not powered.
- **Disambiguation-cue conditions** (a timestamp cue, an explicit-correction cue) — deliberately deferred
  to a separate follow-up rather than folded into this document, to keep this study's claim scoped to one
  change (the confirmatory metric) rather than combined with new conditions.
- **Anything listed as scoped out** in `project_design.md` §11.
- **Cross-model generalization.** Single model, single provider.

## 11. Deviations Policy

Any deviation from this document — a changed test, a changed collapse, a changed N, an added exclusion, a
changed experimental parameter, a changed interpretive threshold — will be reported explicitly in the final
write-up, with the deviation, its reason, and its timing relative to data inspection stated plainly.
Undisclosed deviation from a pre-registration is worse than having no pre-registration at all.

This document is itself an instance of that policy applied to its predecessor: §4 discloses, in full, that
this document's confirmatory collapse differs from the prior preregistration's, why, and exactly what
prior data informed the change.
