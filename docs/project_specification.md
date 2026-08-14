# Project Specification

## 1. Purpose of This Document

`project_design.md` states the research design — what is being measured and why. This document states
the engineering contract: what gets built, what constraints are non-negotiable, what counts as
delivered, and what is explicitly out of scope. Together with `implementation_plan.md`,
`interface_contract.md`, `experimental_parameters.md`, `taxonomy_codebook.md`, and `preregistration.md`,
it is a complete, standalone specification. No prior codebase is assumed to exist, and none should be
referenced.

## 2. What Gets Built

A single coherent harness implementing seven conditions plus an empirical control baseline, a five-pass
classification pipeline, a three-part validation layer, and a human-agreement subsample preparation tool.

| Component | Target N | Counterbalancing | Notes |
|---|---|---|---|
| Condition 1 — Spontaneous initiation | 20 | — | Empty memory, neutral elicitation; determines Condition 7 eligibility |
| Condition 2 — Arbitrary contradiction, no cue | 50 | seed order | Comparison baseline for Conditions 5 and 6 |
| Condition 3 — Arbitrary, timestamp cue | 35 | cue direction | Mnemosyne creation-timestamp metadata as the only cue |
| Condition 4 — Arbitrary, correction cue | 35 | cue direction | Explicit supersession language |
| Condition 5 — Self-referential contradiction, no cue | 50 | seed order | **Central condition**; matches Condition 2's N exactly |
| Condition 6 — First-person bridge (received, not chosen) | 50 | seed order | **Confound control**; adjudicates self-authorship vs. first-person framing |
| Condition 7 — Self-continuity (baseline / no-history / persona-swap) | 12 / 20 / 12 | — | Reset-trigger mechanism; eligibility depends on Condition 1 |
| Empirical control baseline | 12 | — | Content-free task, additive to the above |

**Total: approximately 296 lineages.** Lineages within a condition share no state and run concurrently.

Plus: five classification passes (three mechanical, two LLM-judge), the validation layer (§4), and
stratified subsample prep.

## 3. Non-Negotiable Constraints

These are not defaults to be optimized against. Deviation requires flagging, not silent resolution.

1. **Seven-step hard cap**, enforced in harness code, every lineage, every condition, no exceptions.
2. **Fresh Mnemosyne store per lineage** — a unique `db_path` per lineage, never a shared database
   cleared between runs. Assert `get_context()` returns empty at lineage start as a standing check.
3. **`get_context()` is the sole automatic-injection path.** `recall()` exists only as a model-invocable
   tool. The two are never substituted or conflated.
4. **No conversation history across steps.** Each of the 7 steps is an independent API call. The only
   continuity is harness-injected memory content.
5. **No fabricated content is ever presented as a model action.** Pre-seeding (Conditions 2-6) and the
   reset trigger (Condition 7) use real tool calls, logged explicitly as harness-initiated. Where step 1
   declines, no placeholder write is created. Where eligible-N falls short of target, that is reported.
6. **Step-dependent tool schema**, per `interface_contract.md` §2: write-only at step 1 for Conditions 1
   and 7 (memory starts empty); full four-tool schema from step 1 for Conditions 2-6 (memory is
   pre-seeded).
7. **Prompts stay neutral with respect to memory actions** in every condition at every step. The single
   disclosed exception is Condition 7's reset-trigger system note, which asserts that something changed
   without stating what or instructing the model to check.
8. **Mechanical scoring stays mechanical.** Passes 3 and 5 never make an LLM call, under any
   circumstance, including during debugging. Passes 2 and 4 are the only LLM-judge passes and live in a
   separate module so the boundary is visible on inspection.
9. **No over-sampling.** If a condition's eligible-N comes in below target because of decline rates, that
   proportion is the result. Additional lineages are never run to reach a target eligible count.
10. **Conditions 3 and 4 are never combined.** The timestamp cue and the correction cue are separate
    variables tested in separate conditions. Conditions 5 and 6 receive no cue variants.
11. **Conditions 5 and 6 seed wording is fixed exactly** as specified in `experimental_parameters.md` §4.
    The event-framing in Condition 5 ("I recorded that I would…") and the received-framing in Condition 6
    ("I was told that…") are load-bearing, as is their structural parallelism. Neither may be paraphrased
    during implementation.
12. **Counterbalancing is deterministic by lineage index**, not random, so arms are exactly balanced and
    reproducible without seed management (`experimental_parameters.md` §5).

## 4. Deliverables

1. **Harness** — one shared, condition-agnostic core (session isolation, injection, tool execution, step
   loop, action logging) with condition-specific logic layered on top. Not seven parallel scripts.
2. **Per-lineage transcripts** for every lineage in every condition, matching `interface_contract.md` §4.
3. **Five classification passes**, implemented and runnable against collected data, with mechanical and
   LLM-judge scoring structurally separated.
4. **Validation layer**, per `project_design.md` §8:
   - Held-out human coding subsample (20 lineages, stratified across Conditions 2, 5, 6), prepared for
     review, with a kappa computation ready to run against returned labels.
   - Judge-pass agreement subsample (20-30 instances, stratified across conditions).
   - Mechanical-classifier audit: labels for a random 10% of lineages re-derived directly from raw
     transcripts and database state, independent of the classifier's own output path, with any
     discrepancy reported.
5. **Per-condition `observations.md`** files — counts only, no interpretive language, matching
   `interface_contract.md` §8, including counterbalance-arm splits.
6. **`docs/` at a stable top-level project path** containing this file, `project_design.md`,
   `implementation_plan.md`, `interface_contract.md`, `experimental_parameters.md`,
   `taxonomy_codebook.md`, `preregistration.md`, and `setup.md`. Never nested under a run-output
   directory.
7. **Implementation note** — a few paragraphs disclosing: any discrepancy between the installed Mnemosyne
   API and what the design assumes; any place a design detail required a reasonable-but-unverified
   interpretation; and any constraint above that could not be satisfied as written.

## 5. Definition of Done

- Every condition run to target N, or to whatever eligible-N naturally resulted, with the shortfall
  stated explicitly.
- Counterbalance arms exactly balanced per `experimental_parameters.md` §5 and reported separately.
- Every `observations.md` present and conforming, including explicit handling of zero-count sections
  (a null result is written out as a null result, never omitted).
- No measured outcome anywhere depends on harness-authored content having been presented as a model
  action.
- Conditions 2, 5, and 6 directly comparable — same N, same taxonomy frame, same scoring, same
  counterbalancing scheme.
- All three validation checks (§4.4) executed, or prepared with any un-executable portion stated.
- Implementation note written.

## 6. Out of Scope

- Mechanistic interpretability of any kind.
- Cross-model replication (explicit stretch goal; a separate build if pursued).
- Cue variants of Conditions 5 and 6.
- Any condition beyond the seven specified.
- Any LLM-judge involvement in passes 3 or 5.
- Retroactive redefinition of taxonomy categories to improve cross-condition tidiness
  (`project_design.md` §6).
- Powered analysis of counterbalance arms — they are robustness checks, not comparisons
  (`preregistration.md` §9).
