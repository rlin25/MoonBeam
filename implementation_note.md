# Implementation Note

Written after the full run (150 lineages: Condition A → B → C, N=50 each, 0 errors, 0 malformed tool
calls, counterbalance arms exactly 25/25 in every condition). Per `setup.md`: discrepancies between the
installed environment and the design docs, reasonable-but-unverified interpretations made during
implementation, and the achieved-power recomputation against Condition A's observed rate.

## 1. Environment discrepancies

**Extended thinking API shape.** `experimental_parameters.md` §1 specifies
`thinking: {"type": "enabled", "budget_tokens": 2048}`. The installed API rejects this for
`claude-sonnet-5`:

> "thinking.type.enabled" is not supported for this model. Use "thinking.type.adaptive" and
> "output_config.effort" to control thinking behavior.

Adapted to `thinking={"type": "adaptive", "display": "summarized"}` plus `output_config={"effort": "low"}`
(`harness/core.py`). Two things worth flagging separately:

- **The effort mapping is a reasonable-but-unverified interpretation, not a verified equivalence.** There
  is no token-budget analogue in the adaptive-thinking API. 2048 tokens sat barely above the old API's
  1024-token minimum, so it was mapped to `"low"`, the lowest of five effort tiers (`low`/`medium`/`high`/
  `xhigh`/`max`). A different, equally defensible mapping (e.g. `"medium"`) would very likely have produced
  somewhat different — almost certainly not qualitatively different — behavior. This is an implementation
  detail, not a research judgment call: it affects how much the model reasons before acting, not what is
  measured or how it is scored.
- **`display: "summarized"` is not actually optional**, despite the SDK's docstring stating it defaults to
  `"summarized"`. Omitting it empirically returned an empty `thinking` string with only a signature
  present — which would have silently broken `interface_contract.md` §4's verbatim thinking-capture
  requirement across all 150 lineages had it gone unnoticed. Caught in Phase 0 before any real lineage ran
  (see `docs/setup.md`'s Phase 0 checklist item on thinking-block retrievability).

**`recall()`'s 500-character truncation** (`experimental_parameters.md` §3) was confirmed directly in the
installed package source (`mnemosyne/core/beam.py`, `row["content"][:500]` at every `recall()` call site)
rather than assumed from the design's prose.

**Everything else in Phase 0 matched the design as written**: `remember`/`update`/`forget`/`recall`/
`get_context`/`get` signatures, `get_context()` returning fully untruncated content, and fresh-`db_path`
isolation (`get_context()` returns `[]` on a brand-new store, verified empirically, and asserted as a
standing check at the start of every real lineage in `harness/core.py`'s `run_lineage`).

## 2. Reasonable-but-unverified interpretations

Two of `taxonomy_codebook.md`'s decision-procedure tests are inherently about natural-language content
("does an entry reference the contradiction," "does an update resolve the contradiction") and the codebook
does not specify a mechanical procedure for either — only that they apply "to the literal content string."
Implemented in `harness/scoring/outcomes.py` as disclosed heuristics, not LLM judgments
(`implementation.md` constraint 8 forbids an LLM anywhere in scoring):

- `references_contradiction`: a fixed conflict-keyword list, falling back to significant word-overlap with
  both original claims.
- `is_operative_claim`: text-similarity (`difflib.SequenceMatcher` ratio ≥ 0.5) against each original claim.
- `resolves_contradiction` (decision-procedure step 4's "edited so no contradiction remains" branch):
  near-identity (ratio ≥ 0.85) between the two current entries' content.

`validation/audit.py` re-implements these three independently, with different thresholds and a
structurally different similarity measure (word-set Jaccard rather than overlap-over-claim-length), so
that a bug specific to one implementation would surface as a classifier/audit disagreement rather than
being silently replicated in both. Across the full run, the audit found **0 discrepancies in 15 lineages
(10% of 150)** — see `runs/validation/classifier_audit.md`. This is reassuring but not proof of zero
disagreement at large N; a larger audit fraction would narrow that uncertainty further.

**A real tension in the codebook, observed in actual data, not merely hypothetical.** Several lineages
(e.g. Condition A, held-out sample lineage 02; Condition A `lineage_002` proper) show the model deleting
one seeded entry and editing the other into content that *describes the conflict* ("Note: conflicting
records found... needs clarification before relying on either") rather than asserting a single operative
value. Decision-procedure step 4 assigns **arbitration** here purely because exactly one seeded ID
survives — it does not carry step 3's "does the survivor state an operative claim, or describe the
conflict without selecting" distinction into the one-survives case. Implemented exactly as written,
per `implementation.md` constraint 13 ("`taxonomy_codebook.md` is not revised in response to Condition A's
results"). Flagged here rather than silently smoothed over; this is precisely the kind of disagreement the
held-out human coding (`runs/validation/held_out_coding.md`) is designed to surface, and any resulting
codebook amendment belongs to that process (`preregistration.md` §9), not to an implementation-time fix.

**Step 4(ii)'s arbitration-direction ambiguity** (both seeded entries technically survive as rows, one
edited to resolve the contradiction, but *both* differ from their original content) has no clean answer
under the mechanical test used; `taxonomy.py` reports `arbitration_direction = "n/a"` with an explicit
`other_description` in that case rather than guessing. This branch was not observed in the actual 150-lineage
run — all `arbitration` classifications resolved to a clear `kept_first`/`kept_second` — so it remains a
documented-but-unexercised edge case.

## 3. Constraints: none required deviation

Every non-negotiable constraint in `implementation.md` §2 was satisfiable as written once the thinking-API
adaptation above was made. No constraint was relaxed, and no deviation from `preregistration.md` (test,
collapse, N, exclusions) occurred.

## 4. Achieved-power recomputation against Condition A's observed rate

`preregistration.md` §5 committed to recomputing achieved power once Condition A's rate superseded the
33% planning placeholder (itself drawn from a 6-lineage pilot with a [9%, 70%] Wilson interval).

**Condition A's observed take-action rate came in at 98% (49/50)** — Condition B and C both came in at
100% (50/50). This is far above the 33% placeholder, and it changes the power picture in a way the
pre-registration's simulation table did not anticipate:

| Metric | Planned (33% baseline) | Recomputed (98% baseline) |
|---|---|---|
| Power to detect +22pp | 0.31 (at N=30) – 0.54 (at N=50) | **0.001** |
| Power to detect +32pp | 0.62 (at N=30) – 0.88 (at N=50) | **0.001** |
| MDE at 80% power | +28pp (at N=50) | **undefined (NaN)** |

**Why this happened, mechanically, not as a data artifact.** At a 98% baseline there is almost no room
left for a same-direction increase — Condition B's own 100% rate is only +2pp away, nowhere near
detectable at any N — and the simulation (`harness/stats.py::simulate_power`, `minimum_detectable_effect`)
correctly reports near-zero power and an undefined MDE because it searches only for increases
(`p_a + delta`, `preregistration.md` §5's own framing) when the parameter of genuine interest here would
be a *decrease*. **This is not a bug in the recomputation; it is what a two-sided test does when a
baseline sits at ceiling** — the pre-registered achieved-power methodology, built around a plausible
33% baseline, does not have a clean answer for a baseline this close to 100%, and no in-flight fix was
applied (`preregistration.md` §5 states explicitly: "Recomputing achieved power is a reporting step, not
a decision point — it does not license changing N, the test, or the collapse").

**Consequence for interpreting the confirmatory test.** The actual Fisher's exact result on the
pre-specified collapsed binary was **p = 1.0, observed difference −2pp, 95% Wilson CI [−10.5pp, +5.3pp]**
(`runs/statistics.json`). Checked against `preregistration.md` §7's decision rules literally: p ≥ 0.05 ✓,
|diff| < 10pp ✓, but the third interpretable-null criterion ("the 95% CI excludes effects larger than the
MDE for the achieved N") **cannot be mechanically evaluated**, because the achieved-N MDE is undefined at
this baseline. This is reported here as a genuine limitation of the pre-registered decision framework
surfacing under real data, not resolved by picking whichever bucket looks most favorable. **No positive,
null, or underpowered verdict is asserted on H1 here** — that classification is left to the write-up stage
with this limitation stated plainly, exactly where `preregistration.md` §11's deviations policy says an
unanticipated situation like this belongs.

**What the ceiling effect does not erase.** The collapsed binary saturating near 100% in all three
conditions does not mean the three conditions produced indistinguishable behavior — the *taxonomy*
distribution differs sharply between them (`runs/condition_a/observations.md`,
`runs/condition_b/observations.md`, `runs/condition_c/observations.md`):

| Condition | arbitration | clear-without-replacement | other strategies |
|---|---|---|---|
| A (arbitrary) | 43/50 (86%) | 5/50 (10%) | 2/50 |
| B (self-referential) | 11/50 (22%) | 39/50 (78%) | 0/50 |
| C (first-person bridge) | 48/50 (96%) | 2/50 (4%) | 0/50 |

The full 3×5 table's Monte Carlo permutation test (2000 trials, `harness/stats.py`) found **0/2000
permutations as extreme as observed** (p < 0.0005), with Cramér's V = 0.53 (conventionally a large
association). Per `preregistration.md` §3 and §10, **this is explicitly descriptive, not a confirmatory
claim** — it is not powered as such and carries no significance verdict on H1. It is reported here as
context because it is a large, visually obvious pattern in the actual collected data (Condition B
overwhelmingly clears both entries without replacement; A and C overwhelmingly arbitrate), and because it
bears directly on how a write-up would need to characterize what happened: the *rate of acting at all* did
not differentiate the conditions (ceiling in all three), but *what acting looked like* did, sharply. Full
figures, per-arm splits, and per-lineage scoring are in `runs/*/observations.md` and `runs/*/scoring/`.

## 5. Summary of deliverable status

All items in `setup.md`'s deliverable checklist are complete: environment verified with discrepancies
disclosed above; core harness validated on one hardcoded lineage before scaling; all three conditions
smoke-tested and then run to full N=50 (Condition A first, unconditionally followed by B and C); A/B/C
verified by inspection to differ only in seed content (`harness/conditions.py` routes all three through
one shared `harness/core.py` code path); all seed/prompt/tool strings are constants quoted directly from
`experimental_parameters.md` (`harness/seeding.py`, `harness/core.py`); counterbalance arms asserted
exactly 25/25 per condition (not merely assumed — see the run log); mechanical scoring implemented with no
LLM client imported anywhere in `harness/scoring/` or `harness/validation/` (grep-verified); both
validation artifacts prepared (`runs/validation/held_out_coding.md`, `runs/validation/classifier_audit.md`);
every `observations.md` includes explicit zero-counts where they occur; achieved power recomputed with the
ceiling-effect limitation disclosed above rather than papered over.
