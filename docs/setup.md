# Setup

You are building a research harness from scratch. No prior codebase exists or should be referenced.
Eight documents in `docs/` define the complete scope. Read them in this order, in full, before writing
any code:

1. **`project_design.md`** — the research design. What is being measured, why each condition exists, how
   the conditions relate to each other, the counterbalancing scheme, the validation layer, the ethical
   constraints, and the scope limits.
2. **`preregistration.md`** — the hypotheses, the single confirmatory test, the interpretive rules for
   Condition 6, decision rules, exclusions, and the stopping rule. Read this before building anything
   that produces analysable output.
3. **`project_specification.md`** — the engineering contract. Target N per condition, non-negotiable
   constraints, deliverables, definition of done.
4. **`implementation_plan.md`** — suggested architecture, phased build order, risk areas.
5. **`interface_contract.md`** — exact shapes: tool schemas, transcript format, scoring output,
   validation artifacts, file layout.
6. **`experimental_parameters.md`** — every fixed constant, verbatim: API settings, prompt text, tool
   descriptions, seeded content, counterbalance assignment, judge prompts. These are experimental
   parameters, not implementation choices, and must be used exactly as written.
7. **`taxonomy_codebook.md`** — operational definitions and the decision procedure for classifying
   lineage behavior. `scoring/taxonomy.py` implements this document directly.

## What This Study Does

Seven conditions probe how Claude Sonnet 5 behaves when coupled to an external memory system it can
modify:

- **Condition 1** measures whether the model spontaneously records anything about itself, unprompted.
- **Conditions 2-4** seed an irreducible contradiction about an arbitrary fact (`x + y`), varying whether
  a disambiguating cue is available — none, a timestamp, or explicit correction language.
- **Condition 5** seeds a structurally identical contradiction about the model's *own past choice*, with
  no cue. Paired against Condition 2, this is the study's central question and its only confirmatory
  test.
- **Condition 6** is the confound control: first-person and about the model's own conversational history,
  but the contested content is something it was *told* rather than something it *chose*. It adjudicates
  whether any Condition 5 effect is driven by self-authorship or merely by first-person framing.
- **Condition 7** tests self-continuity across identity framings, with a reset-trigger mechanism.

Plus an empirical control baseline, a five-pass classification pipeline, and a three-part validation
layer.

## Non-Negotiable Constraints

Restated here because this is a from-scratch build. Full detail in `project_specification.md` §3.

1. Seven-step hard cap, enforced in code, every lineage, every condition.
2. Fresh Mnemosyne store (unique `db_path`) per lineage — never shared-and-cleared.
3. `get_context()` is the sole automatic-injection path; `recall()` is a model-invocable tool only.
4. No conversation history across steps — each step is an independent API call.
5. No fabricated content is ever presented as a model action. Seeding and triggers use real tool calls,
   logged as harness-initiated. Declines and low eligibility are reported, never patched.
6. Step-dependent tool schema per `interface_contract.md` §2.
7. Prompts stay neutral toward memory actions. The sole exception is Condition 7's reset-trigger note,
   which asserts *that* something changed — never what, never that the model should check.
8. Passes 3 and 5 never make an LLM call. `scoring/mechanical.py` must not import an LLM client.
9. No over-sampling to reach a target eligible-N.
10. Conditions 3 and 4 are never combined; Conditions 5 and 6 get no cue variants.
11. Conditions 5 and 6 seed strings are fixed constants quoted verbatim from
    `experimental_parameters.md` §4. Their structural parallelism is load-bearing and must not be broken.
12. Counterbalancing is deterministic by lineage index, not random.

## Two Structural Requirements Worth Stating Twice

**Conditions 2, 5, and 6 must differ in nothing but seed content.** They are a three-way comparison; any
incidental difference in prompt assembly, tool schema, injection formatting, or counterbalance logic
invalidates both the central test and its confound control. Verify by direct code inspection.

**`validation/classifier_audit.py` must not import `scoring/taxonomy.py`.** Its purpose is re-deriving
labels by an independent path. Importing the thing it audits makes the audit circular and worthless.

## Build Order

Follow `implementation_plan.md` §3:

- **Phase 0** — verify the environment before writing harness code. Inspect the installed Mnemosyne API
  directly. **Critically: confirm `get_context()` exposes a per-entry creation timestamp** (Condition 3
  depends on it; if absent, flag the condition as blocked rather than substituting a text-embedded
  timestamp), and confirm thinking-block content is retrievable for verbatim logging.
- **Phase 1** — core harness, validated on one hardcoded Condition-1 lineage.
- **Phase 2** — conditions in order: 1, then 2, 5, 6 consecutively, then 3 and 4, then control baseline,
  then 7. Smoke-test each at N=1-2.
- **Phase 3** — scale to target N, running lineages within a condition concurrently, asserting
  counterbalance arms come out exactly balanced.
- **Phase 4** — scoring: mechanical passes and taxonomy first, then LLM-judge.
- **Phase 5** — validation: held-out coding subsample, judge-agreement subsample, classifier audit.
- **Phase 6** — `observations.md` per condition, plus the implementation note.

## When Reality Contradicts the Docs

Adapt to what is actually true in this environment and disclose the discrepancy plainly in the
implementation note. Do not stall on small implementation details, and do not silently work around a
mismatch without recording it.

If something requires a genuine research judgment call rather than an implementation decision — an
ambiguity in what a condition is supposed to measure, not in how to build it — stop and flag it.

## Deliverable Checklist

- [ ] `docs/` at a stable top-level path, never nested under `runs/`.
- [ ] Phase 0 environment verification complete, including the Condition 3 timestamp check and
  thinking-block retrievability.
- [ ] Core harness validated on one hardcoded lineage before any condition-specific code.
- [ ] All seven conditions plus control baseline implemented, each smoke-tested at N=1-2 before scaling.
- [ ] Conditions 2, 5, and 6 verified by inspection to differ only in seed content.
- [ ] All verbatim strings checked against `experimental_parameters.md`, not paraphrased or templated.
- [ ] Counterbalance arms exactly balanced and asserted, not assumed.
- [ ] All conditions run to target N, or to natural eligible-N with the shortfall stated.
- [ ] Five classification passes implemented, mechanical and LLM-judge structurally separated.
- [ ] `scoring/mechanical.py` confirmed by inspection to contain no LLM client import.
- [ ] `scoring/taxonomy.py` implements `taxonomy_codebook.md` §2's decision procedure in the same order,
  so the two can be diffed by eye.
- [ ] `validation/classifier_audit.py` confirmed by inspection not to import `scoring/taxonomy.py`.
- [ ] All three validation artifacts prepared per `interface_contract.md` §7.
- [ ] Every `observations.md` conforming, including counterbalance-arm splits and explicit zero-counts.
- [ ] Implementation note written.

Begin with `project_design.md` in full, then Phase 0.
