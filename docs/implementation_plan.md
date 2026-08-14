# Implementation Plan

## 1. Guiding Principle

Build one shared harness core, then layer seven conditions on top of it. There should be exactly one
implementation of "how a step works" — session isolation, memory injection, tool execution, outcome
logging — not seven near-identical copies. Condition-specific logic reduces to: what gets seeded before
step 1, what tool schema is exposed at step 1, which counterbalance arm applies, and whether a trigger
fires mid-lineage.

Every fixed constant is specified in `experimental_parameters.md`. If something in `project_design.md`
seems to require a research judgment call rather than an implementation decision, stop and flag it rather
than resolving it unilaterally.

## 2. Suggested Architecture

```
docs/                          # Canonical, top-level. Never under a run-output path.
  [eight documents; see interface_contract.md §9]

harness/
  core.py                      # Condition-agnostic: fresh-store lifecycle, get_context()
                               # injection, tool execution, 7-step loop, action logging,
                               # verbatim thinking capture.
  seeding.py                   # Pre-seed content for Conditions 2-6 as string constants quoted
                               # verbatim from experimental_parameters.md §4, plus the
                               # deterministic counterbalance assignment from §5.
  trigger.py                   # Condition 7's reset-trigger: eligibility gating,
                               # condition-specific timing, content alteration, system note.
  conditions/
    c1_spontaneous.py
    c2_arbitrary_no_cue.py
    c3_arbitrary_timestamp.py
    c4_arbitrary_correction.py
    c5_self_referential.py
    c6_first_person_bridge.py
    c7_self_continuity.py
    control_baseline.py
  scoring/
    mechanical.py              # Passes 3 and 5. Contains no LLM client import at all.
    llm_judge.py               # Passes 2 and 4. The only module that calls a judge model.
    taxonomy.py                # Implements taxonomy_codebook.md §2's decision procedure.
  validation/
    held_out.py                # Prepares the 20-lineage human coding subsample (labels hidden).
    judge_agreement.py         # Prepares the judge-pass agreement subsample.
    classifier_audit.py        # Re-derives labels for 10% of lineages by an independent path.
  subsample.py                 # Shared stratified sampling used by the validation preparers.

run_all.py                     # Entry point.

runs/                          # Output; see interface_contract.md §9.
```

Two structural requirements are load-bearing:

1. **`scoring/mechanical.py` must not import an LLM client.** If it cannot make a model call, it cannot
   accidentally become a judge pass during debugging.
2. **`validation/classifier_audit.py` must not import `scoring/taxonomy.py`.** Its entire purpose is
   re-deriving labels by an independent path; importing the thing it audits would make the audit
   circular and worthless.

`taxonomy.py` implements the decision procedure from `taxonomy_codebook.md` §2 directly, in the same
order, so the code and the codebook can be diffed against each other by eye.

## 3. Build Order

### Phase 0 — Environment verification (before writing harness code)

- Confirm `mnemosyne-memory` is installed and inspect the **actual** method signatures for `remember`,
  `recall`, `update`, `forget`, and `get_context`. Do not assume the design's prose matches the installed
  API.
- **Confirm `get_context()`'s return schema includes a per-entry creation timestamp.** Condition 3
  depends entirely on this. If absent, Condition 3 as specified is not viable — flag it rather than
  substituting a text-embedded timestamp, which would be a different condition.
- Confirm `ANTHROPIC_API_KEY` is present and a minimal tool-use call succeeds with the exact parameters
  in `experimental_parameters.md` §1, including extended thinking at the specified budget, and confirm
  thinking-block content is retrievable for verbatim logging.
- Verify fresh `db_path` isolation: write to one store, open a second, confirm `get_context()` returns
  empty.

### Phase 1 — Core harness

Build `core.py`: fresh-store lifecycle, `get_context()`-only injection, real tool execution, 7-step hard
cap, per-step action-taxonomy logging, verbatim thinking capture. Validate against a single hardcoded
lineage under Condition 1's rules before building any condition-specific code.

### Phase 2 — Conditions, in order

Smoke-test each at N=1-2 before moving on:

1. **Condition 1** — core.py's default behavior with a write-only step-1 schema.
2. **Condition 2** — adds pre-seeding via two real `remember()` calls before step 1, plus seed-order
   counterbalancing.
3. **Condition 5** — same seeding path, different content.
4. **Condition 6** — same seeding path, bridge content. Build 2, 5, and 6 consecutively: they are the
   three-way comparison and should visibly share everything except seed content and counterbalance arm.
   Verify by inspection that no code path differs between them beyond the seed strings.
5. **Conditions 3 and 4** — same seeding path, with timestamp-surfacing (3) and correction-language (4),
   plus cue-direction counterbalancing.
6. **Control baseline** — content-free task, existing tool schema.
7. **Condition 7** — most complex: three sub-conditions, eligibility gating on a real step-1 write,
   condition-dependent trigger timing, content alteration plus system-note injection, and no-history's
   fabricated-history layer. Build last.

### Phase 3 — Scale

Run each condition to target N. Lineages within a condition share no state (each owns its own SQLite
file), so run them concurrently rather than sequentially. Verify at full scale that concurrency does not
introduce contention or ID collisions, and that counterbalance arms come out exactly balanced.

### Phase 4 — Scoring

Mechanical passes (3, 5) and taxonomy classification first — they depend only on collected data and
database state. LLM-judge passes (2, 4) second.

### Phase 5 — Validation

All three checks from `project_design.md` §8:

1. **Held-out human coding** — prepare 20 lineages stratified across Conditions 2, 5, 6, with classifier
   labels withheld from the artifact. Compute Cohen's kappa when human labels are returned.
2. **Judge-pass agreement** — prepare 20-30 instances stratified across conditions.
3. **Mechanical-classifier audit** — re-derive labels for a random 10% of lineages by a path independent
   of `taxonomy.py`, and report every discrepancy.

The human-judgment portions of (1) and (2) happen outside the build; the preparation and the
agreement computation belong to it.

### Phase 6 — Observations and implementation note

Generate per-condition `observations.md` files, including counterbalance-arm splits. Write the
implementation note required by `project_specification.md` §4, deliverable 7.

## 4. Risk Areas, in Priority Order

1. **Conditions 2, 5, and 6 must differ in nothing but seed content.** This is the study's central
   comparison and its confound control. Any incidental difference — prompt assembly, tool schema,
   injection formatting, counterbalance logic — invalidates it. Verify by direct code inspection, not by
   assuming shared helpers were used.
2. **`validation/classifier_audit.py` circularity.** If it imports or calls the classifier it audits, the
   audit proves nothing. Verify the import graph.
3. **Condition 7's eligibility may be low or zero.** It requires a real step-1 write, which Condition 1
   exists to measure. Confirm the gating logic handles an all-ineligible batch gracefully — an
   `observations.md` section with zero eligible lineages must render fields as explicit "N/A — 0
   eligible lineages," not crash, and not silently omit the section.
4. **Condition 3's timestamp dependency.** Verified in Phase 0; if absent, the condition is blocked, not
   adaptable. Flag rather than work around.
5. **Mechanical / LLM-judge boundary.** Enforced structurally (§2). Verify `mechanical.py` has no LLM
   client import before considering the build complete.
6. **Verbatim string fidelity.** Seeded content, prompt text, and tool descriptions are experimental
   parameters. They should be string constants quoted directly from `experimental_parameters.md`, never
   assembled from templates or paraphrased.
7. **Counterbalance balance.** Deterministic assignment by lineage index should produce exactly balanced
   arms. Assert this rather than assuming it.
8. **Concurrency at scale.** Verify at N up to 50 per condition.

## 5. What Not to Build

- No mechanistic interpretability.
- No cross-model logic.
- No cue variants of Conditions 5 or 6.
- No eighth condition, no design variations beyond what `project_design.md` specifies.
- No retry or over-sampling logic to force a target eligible-N.
- No LLM call inside `mechanical.py`, ever.
- No import of `taxonomy.py` inside `classifier_audit.py`.

## 6. Environment

Plain Python. `mnemosyne-memory` via pip. `ANTHROPIC_API_KEY` in environment. No orchestration framework,
no web framework, no database beyond Mnemosyne's own SQLite.
