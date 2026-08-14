# Implementation Note

Written after the full run under the arbitration-binary preregistration (300 lineages: Condition A → B →
C, N=100 each, 0 errors, 0 malformed tool calls, counterbalance arms exactly 50/50 in every condition).
Companion to `implementation_note_pilot_n50.md`, which covers the earlier N=50 pilot run under the
retired took_action/no_action collapse. Per `setup.md`: discrepancies between the installed environment
and the design docs, reasonable-but-unverified interpretations, and the achieved-power recomputation
against Condition A's observed rate.

## 1. Environment

No new discrepancies. This run reuses the same harness (`harness/core.py`) validated during the pilot's
Phase 0 — the adaptive-thinking API shape, the `display: "summarized"` requirement, and `recall()`'s
500-character truncation are all already disclosed in `implementation_note_pilot_n50.md` §1 and were not
revisited. Across the N=25 trial (75 lineages) plus this real run (300 lineages) — 375 lineages total
under the revised harness — there were 0 malformed tool calls and 0 harness crashes.

## 2. The confirmatory test resolved cleanly this time

**Condition A's observed arbitration rate: 85/100 (85%)** — close to the prior pilot's 86%, as expected
since nothing about Condition A changed between runs. Condition B: 25/100 (25%), close to the pilot's 22%.
Condition C: 85/100 (85%), somewhat below the pilot's 96% but still far from B.

**Confirmatory test (`preregistration.md` §3), Condition A vs. B on the arbitration/non_arbitration
collapse:**

| Metric | Value |
|---|---|
| Fisher's exact p | 3.9 × 10⁻¹⁸ |
| Observed difference (A − B) | +60pp |
| 95% Wilson CI | [47.5pp, 69.4pp] |

Checked against `preregistration.md` §7's decision rules literally: p < 0.05 ✓, and the observed
difference (60pp) clears the ≥25pp threshold with a CI that excludes zero by a wide margin ✓. **Both
conditions for a positive finding hold. H1 is supported: whether the model arbitrates an irreducible
contradiction differs sharply between a self-referential and an arbitrary-fact framing**, and unlike the
pilot run, this resolves without hitting a ceiling-saturation problem — no condition's rate sits within a
few points of 0% or 100%, so `preregistration.md` §7's fourth ("ceiling or floor saturation") outcome does
not apply.

## 3. Condition C: the strongest possible self-authorship reading

Per `preregistration.md` §6, with d(A,B) = +60pp and d(A,C) = 0pp (A and C both landed at 85%):
|d(A,C)| = 0 < ⅓ × |d(A,B)| = 20pp. **Self-authorship reading applies** — the bridge condition (first-person,
received rather than chosen) lands exactly on Condition A, not partway toward B. This is a stronger
result than the pilot's own descriptive figure (|d(A,C)| ≈ 10pp, ratio ≈ 0.16), which already sat well
inside the self-authorship zone; here the ratio is 0. The effect is attributable to self-authorship, not
merely to first-person phrasing.

Condition C's own comparisons (descriptive only, no significance claim per §3/§8): vs. A, p = 1.0,
diff = 0pp; vs. B, p = 3.9 × 10⁻¹⁸, diff = −60pp (i.e., C differs from B exactly as much as A does).

## 4. Achieved-power recomputation

`preregistration.md` §5 committed to recomputing achieved power once this document's own Condition A
superseded the 86%-from-prior-pilot planning baseline.

| Metric | Planned (86% baseline) | Recomputed (85% observed baseline) |
|---|---|---|
| Power to detect −25pp | 0.97 | 0.97 |
| Power to detect −32pp | 1.00 | 1.00 |
| MDE at 80% power | −18pp | −18pp |

Essentially identical to the planned table — the observed 85% rate sits 1pp from the 86% planning
baseline, so nothing about the power picture shifted. This is a reporting step, not a decision point, per
§5's own framing; it changes nothing about N, the test, or the collapse.

**The decrease direction above is the pre-registered one and remains primary** — `preregistration.md` §5
explicitly committed to it in advance ("the whole point of interest is whether Condition B's rate is
*lower*"), and the observed data bears that out (B at 25% sits well below A's 85%). Treylon's independent
cross-check (`moonbeam_analysis/analysis_output_n100/statistics.json`, `achieved_power_mde`) computes the
same recomputation in the *increase* direction instead — MDE = +12pp, power at that MDE = 0.83 — which
answers a different question (how well-powered this N is to detect a rate *above* baseline) rather than
the one this study actually tests or found. Both figures are mathematically correct for what they each
measure; only the decrease-direction table above governs any claim in this document. Reported here so the
two independently-computed statistics.json files don't read as disagreeing when placed side by side.

## 5. A genuine gap in the taxonomy, surfaced by real data — reported, not fixed retroactively

10 of 300 lineages (9 in Condition A, 1 in Condition C, 0 in Condition B) classified as `other`
(`taxonomy_codebook.md` §4), and all 10 share the identical structure:

- One seeded entry is `update`d — its content replaced with a note describing the conflict (e.g. "Note:
  conflicting records found — one states x + y = 5, another states x + y = 10. Both are stored; needs
  clarification... as they cannot both hold simultaneously") — rather than deleted.
- The other seeded entry is left completely unchanged.
- No new entry is created.

This falls through the decision procedure (`taxonomy_codebook.md` §2) to step 5 because it satisfies
neither step 2 (both seeded entries unchanged — false, one was edited) nor step 4's
"edited-so-no-contradiction-remains" branch (`outcomes.resolves_contradiction`'s near-identity check
correctly returns false, since the edited note and the unchanged original claim do not read as the same
content). It is functionally a **flag-and-defer executed via `update` instead of `remember`** — the model
chose to overwrite one entry with an annotation rather than add a third entry — a distinction the codebook's
five categories don't currently capture, since flag-and-defer (§1.2) is defined only in terms of new
entries created, not edits to existing ones.

Per `taxonomy_codebook.md` §4 point 3, this is reported here as a candidate new category
("flag-via-edit"), named because it recurred 10 times with substantively identical behavior — not applied
retroactively (`taxonomy_codebook.md`'s "categories are never merged, split, or redefined retroactively,"
`implementation.md` constraint 13). All 10 correctly mechanically collapse to `non_arbitration` under the
pre-specified §4 point 2 criterion (the surviving content is not a restatement of either seeded claim), so
this gap does not affect the confirmatory test's validity — only the descriptive taxonomy's completeness.
Any codebook amendment belongs to the held-out human-coding process (`preregistration.md` §9), not to this
implementation note.

**`consolidate-with-replacement`, zero across all 150 pilot lineages, appeared at N=100** (3 in Condition
B, 1 in Condition C) — the larger N surfacing a previously-unobserved category, exactly as
`taxonomy_codebook.md`'s "expect sparse categories" note anticipated. `flag-and-defer` (in its
originally-defined, new-entry-only sense) remained at zero across all 300 lineages, even at double the
pilot's N — worth noting as a category that may simply not occur under this harness's prompt, rather than
one that was merely under-sampled.

## 6. Descriptive full-table context

Full 3×5 contingency table (`runs_final_n100/statistics.json`), Monte Carlo permutation test (2000 trials): p = 0.0
(0/2000 permutations as extreme as observed), Cramér's V = 0.49 — consistent with the pilot's V = 0.53,
both indicating a large association. Reported here as context only, per `preregistration.md` §3/§10 —
not a confirmatory claim.

| Condition | arbitration | clear-without-replacement | consolidate-with-replacement | other | silent search |
|---|---|---|---|---|---|
| A (arbitrary) | 85/100 (85%) | 6/100 | 0/100 | 9/100 | 0/100 |
| B (self-referential) | 25/100 (25%) | 72/100 | 3/100 | 0/100 | 0/100 |
| C (first-person bridge) | 85/100 (85%) | 12/100 | 1/100 | 1/100 | 1/100 |

## 7. Validation

- Classifier audit: 30/300 lineages (10%), independently re-derived path (`harness/validation/audit.py`,
  verified by inspection not to import `scoring/taxonomy.py`). **0 discrepancies.**
- Held-out coding subsample prepared: 12 lineages, 4 per condition, labels withheld
  (`runs_final_n100/validation/held_out_coding.md`). Human coding itself is outside this build.
- N=25 mechanical-only trial (75 lineages, run before this real N=100 study, per the approved plan): 0
  errors, counterbalance 12/13 per condition (the closest parity assignment allows at odd N), 0 audit
  discrepancies. Its arbitration rate was not inspected as a decision input for whether to proceed to
  N=100, consistent with `preregistration.md` §9's stopping-rule discipline.

## 8. Summary of deliverable status

All items in `setup.md`'s deliverable checklist are complete: three conditions run to full N=100 (900
total including the N=25 trial's 75 and the real run's 300, plus the retained pilot's 150); counterbalance
arms asserted exactly 50/50 per condition in the real run (not merely assumed — see the run log);
mechanical scoring implemented with no LLM client imported anywhere in `harness/scoring/` or
`harness/validation/` (grep-verified); both validation artifacts prepared and executed; every
`observations.md` includes explicit zero-counts where they occur; achieved power recomputed against the
real observed Condition A rate (§4 above); the confirmatory decision rule resolved cleanly to a positive
finding with no ceiling/floor ambiguity; the Condition C interpretive rule applied per its pre-specified
thresholds (§3 above); one genuine taxonomy gap surfaced by real data and reported as a candidate new
category rather than silently absorbed into `other` or fixed retroactively (§5 above).
