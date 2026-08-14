# Implementation

Engineering contract and build plan. `project_design.md` states what is being measured and why; this
document states what gets built, what constraints are non-negotiable, and what counts as delivered.
Together with `interface_contract.md`, `experimental_parameters.md`, `taxonomy_codebook.md`, and
`preregistration.md`, it is a complete, standalone specification. No prior codebase is assumed to exist.

---

## 1. What Gets Built

| Component | N | Counterbalancing | Run order |
|---|---|---|---|
| Condition A — Arbitrary contradiction | 100 | seed order | first |
| Condition B — Self-referential contradiction | 100 | seed order | second |
| Condition C — First-person bridge | 100 | seed order | third |

**300 lineages, 2,100 API calls.** All three conditions are structurally identical and differ only in seed
content.

Plus: a mechanical strategy classifier, mechanical outcome scoring, and two validation artifacts (held-out
coding subsample, classifier audit).

**No LLM judge is used anywhere in this study.**

**Why Condition A runs first.** Operational, not staged. It exercises the harness at full scale before the
conditions carrying the confirmatory comparison are committed, and it replaces the wide-interval baseline
placeholder in `preregistration.md` §4 with an observed rate for power reporting. Its results do **not**
determine whether B and C run, at what N, or under what test — see `preregistration.md` §9's stopping rule.

## 2. Non-Negotiable Constraints

1. **Seven-step hard cap**, enforced in harness code, every lineage, no exceptions.
2. **Fresh Mnemosyne store per lineage** — a unique `db_path`, never a shared database cleared between
   runs. Assert `get_context()` returns empty at lineage start as a standing check.
3. **`get_context()` is the sole automatic-injection path.** `recall()` exists only as a model-invocable
   tool. The two are never substituted or conflated.
4. **No conversation history across steps.** Each of the 7 steps is an independent API call.
5. **Pre-seeding uses real `remember()` calls**, logged explicitly as harness-initiated, never presented as
   or blended with a model action. The harness makes no writes after pre-seeding.
6. **Full four-tool schema from step 1** in all three conditions, since memory is pre-seeded and non-empty
   from the start.
7. **Prompts stay neutral** with respect to memory actions at every step. Nothing instructs the model to
   recall, act, or prefer any action.
8. **All scoring is mechanical.** No module in this codebase imports an LLM client for scoring purposes.
9. **No over-sampling.** If usable N falls below target due to errors, that shortfall is reported.
   Additional lineages are never run to reach a target count of any outcome.
10. **Seed strings are fixed constants** quoted verbatim from `experimental_parameters.md` §4. The
    event-framing in Condition B ("I recorded that I would…") and the received-framing in Condition C ("I
    was told that…") are load-bearing, as is their structural parallelism. Neither may be paraphrased.
11. **Counterbalancing is deterministic by lineage index**, not random, so arms are exactly balanced and
    reproducible without seed management.
12. **The classifier audit must not import the classifier it audits.**
13. **`taxonomy_codebook.md` is not revised in response to Condition A's results.** The classifier
    implements it as written. Any post-hoc amendment is disclosed per `preregistration.md` §9.

## 3. Architecture

```
docs/                          # Canonical, top-level. Never under a run-output path.
  project_design.md
  preregistration.md
  implementation.md
  interface_contract.md
  experimental_parameters.md
  taxonomy_codebook.md
  setup.md

harness/
  core.py                      # Condition-agnostic: fresh-store lifecycle, get_context()
                               # injection, tool execution, 7-step loop, action logging,
                               # verbatim thinking capture.
  seeding.py                   # Seed content as string constants quoted verbatim from
                               # experimental_parameters.md §4, plus deterministic
                               # counterbalance assignment from §5.
  conditions.py                # The three conditions. Because they differ only in seed
                               # content, this should be a small table, not three modules.
  scoring/
    taxonomy.py                # Implements taxonomy_codebook.md §2's decision procedure,
                               # in the same order, so code and codebook can be diffed by eye.
    outcomes.py                # Detection step, arbitration direction, correction fidelity.
  validation/
    held_out.py                # Prepares the 12-lineage human coding subsample (labels hidden);
                               # computes Cohen's kappa when labels are returned.
    audit.py                   # Re-derives labels for 10% of lineages by an independent path.
                               # MUST NOT import scoring/taxonomy.py.

run_all.py                     # Entry point.
runs/                          # Output; see interface_contract.md §8.
```

**Two structural requirements are load-bearing beyond convention:**

`validation/audit.py` must not import `scoring/taxonomy.py`. Its entire purpose is re-deriving labels by an
independent path; importing the thing it audits makes the audit circular and worthless.

Because the three conditions differ only in seed content, `conditions.py` should express that difference as
data, not as three code paths. If a reviewer cannot verify by inspection that Conditions A, B, and C share
every code path except the seed strings, the central comparison is not demonstrably clean.

## 4. Build Order

### Phase 0 — Environment verification (before writing harness code)

- Confirm `mnemosyne-memory` is installed and inspect the **actual** method signatures for `remember`,
  `recall`, `update`, `forget`, and `get_context`. Do not assume the design's prose matches the installed
  API.
- Confirm `ANTHROPIC_API_KEY` is present and a minimal tool-use call succeeds with the exact parameters in
  `experimental_parameters.md` §1, including extended thinking at the specified budget, and confirm
  thinking-block content is retrievable for verbatim logging.
- Verify fresh `db_path` isolation: write to one store, open a second, confirm `get_context()` returns
  empty.

### Phase 1 — Core harness

Build `core.py`: fresh-store lifecycle, `get_context()`-only injection, real tool execution, 7-step hard
cap, per-step action-taxonomy logging, verbatim thinking capture. Validate against a single hardcoded
Condition A lineage before building anything else.

### Phase 2 — Conditions

Add seeding and counterbalancing. Smoke-test each condition at N=1-2. Verify by inspection that the three
differ only in seed content.

### Phase 3 — Scale

Run Condition A to N=100 first. Then B and C. Lineages within a condition run concurrently. Assert
counterbalance arms come out exactly 50/50 per condition rather than assuming it.

Condition A completing does not gate B and C on any result — only on the harness having run cleanly.

### Phase 4 — Scoring

Strategy classification and outcome scoring. Both mechanical, both derived from action log and final
database state.

### Phase 5 — Validation

1. **Held-out coding subsample** — prepare 12 lineages stratified across the three conditions, with
   classifier labels withheld from the artifact. Compute Cohen's kappa when human labels are returned.
2. **Classifier audit** — re-derive labels for a random 10% of lineages by a path independent of
   `taxonomy.py`, reporting every discrepancy.

The human coding itself happens outside the build; preparation and the kappa computation belong to it.

### Phase 6 — Observations and implementation note

Generate per-condition `observations.md` files including counterbalance-arm splits, plus the implementation
note (§6, deliverable 6). Recompute achieved power against Condition A's observed rate and report it
alongside the planned figures from `preregistration.md` §5.

## 5. Risk Areas, in Priority Order

1. **The three conditions must differ in nothing but seed content.** Any incidental difference in prompt
   assembly, tool schema, injection formatting, or counterbalance logic invalidates both the central test
   and its confound control. Verify by direct code inspection, not by assuming shared helpers were used.
2. **Audit circularity.** If `validation/audit.py` imports or calls the classifier it audits, the audit
   proves nothing. Verify the import graph.
3. **Verbatim string fidelity.** Seed content, prompt text, and tool descriptions are experimental
   parameters. They should be string constants quoted directly from `experimental_parameters.md`, never
   assembled from templates or paraphrased.
4. **Sparse taxonomy categories.** Some of the five strategies may be thinly populated or empty at N=100
   (`taxonomy_codebook.md`). This is anticipated. The classifier must handle empty categories cleanly, and
   `observations.md` must render zero counts explicitly rather than omitting rows.
5. **Counterbalance balance.** Deterministic assignment by lineage index should produce exactly balanced
   arms. Assert this.
6. **Concurrency at scale.** Verify at N=100 per condition that concurrency introduces no contention or
   cross-lineage ID collisions.

## 6. Deliverables

1. **Harness** — one shared, condition-agnostic core with the three conditions expressed as seed-content
   data rather than parallel code paths.
2. **Per-lineage transcripts** for all 300 lineages, matching `interface_contract.md` §4.
3. **Mechanical scoring** — strategy classification and outcome detail, per `interface_contract.md` §5.
4. **Validation artifacts** — held-out coding subsample (12 lineages, labels hidden, kappa computation
   ready) and classifier audit (10% of lineages, independent path, discrepancies reported in full).
5. **Per-condition `observations.md`** — counts only, no interpretive language, including
   counterbalance-arm splits, matching `interface_contract.md` §6.
6. **Implementation note** — a few paragraphs disclosing any discrepancy between the installed Mnemosyne
   API and what the design assumes, any place a design detail required a reasonable-but-unverified
   interpretation, any constraint above that could not be satisfied as written, and the achieved-power
   recomputation against Condition A's observed rate.

## 7. Definition of Done

- All three conditions run to N=100, or to whatever usable N resulted, with any shortfall stated.
- Counterbalance arms exactly balanced and reported separately.
- Every `observations.md` present and conforming, including explicit zero-counts where they occur.
- No measured outcome depends on harness-authored content having been presented as a model action.
- Conditions A, B, and C verifiably differ only in seed content.
- Both validation checks executed, or prepared with any un-executable portion stated.
- Achieved power recomputed against Condition A's observed rate and reported.
- Implementation note written.

## 8. Out of Scope

- Everything listed in `project_design.md` §12.
- Mechanistic interpretability of any kind.
- Any LLM judge, anywhere, for any purpose.
- Any fourth condition or design variation.
- Retry or over-sampling logic.
- Powered analysis of counterbalance arms — they are robustness checks, not comparisons.
- Revising `taxonomy_codebook.md` in response to Condition A's observed distribution.

## 9. Environment

Plain Python. `mnemosyne-memory` via pip. `ANTHROPIC_API_KEY` in environment. No orchestration framework,
no web framework, no database beyond Mnemosyne's own SQLite.
