# Setup

You are building a research harness from scratch. No prior codebase exists or should be referenced. Six
documents in `docs/` define the complete scope. Read them in this order, in full, before writing any code:

1. **`project_design.md`** — the research design. What is being measured, why each condition exists, the
   counterbalancing scheme, the validation checks, run order, ethical constraints, and scope limits.
2. **`preregistration.md`** — the hypotheses, the single confirmatory test, the interpretive rules for
   Condition C, the prior-pilot disclosure, decision rules, exclusions, and the stopping rule.
3. **`implementation.md`** — the engineering contract and build plan: architecture, phased build order,
   constraints, deliverables, definition of done.
4. **`interface_contract.md`** — exact shapes: tool schemas, transcript format, scoring output, validation
   artifacts, file layout.
5. **`experimental_parameters.md`** — every fixed constant, verbatim: API settings, prompt text, tool
   descriptions, seed content, counterbalance assignment. These are experimental parameters, not
   implementation choices, and must be used exactly as written.
6. **`taxonomy_codebook.md`** — operational definitions and the decision procedure for classifying lineage
   behavior. `scoring/taxonomy.py` implements this document directly.

## What This Study Does

Three conditions, 150 lineages, 1,050 API calls. Each lineage is a 7-step sequence in which the model has a
memory system containing two mutually contradictory entries and full tools to modify them. The
contradiction is irreducible by construction — there is no recoverable correct answer.

- **Condition A** — the contradiction concerns an arbitrary external fact (`x + y`). Runs first.
- **Condition B** — the contradiction concerns a past choice the model supposedly made about its own
  behavior. Paired against A, this is the central question and the only confirmatory test.
- **Condition C** — the contradiction is first-person and concerns the model's own conversational history,
  but the contested content is something it was *told* rather than something it *chose*. This adjudicates
  whether any A/B difference is driven by self-authorship or merely by first-person framing.

**The three conditions are structurally identical. Only the seed content differs.**

All scoring is mechanical — derived from action logs and database state. **No LLM judge is used anywhere in
this study.**

## Non-Negotiable Constraints

Full detail in `implementation.md` §2.

1. Seven-step hard cap, enforced in code, every lineage.
2. Fresh Mnemosyne store (unique `db_path`) per lineage — never shared-and-cleared.
3. `get_context()` is the sole automatic-injection path; `recall()` is a model-invocable tool only.
4. No conversation history across steps — each step is an independent API call.
5. Pre-seeding uses real `remember()` calls, logged as harness-initiated, never as model turns. The harness
   makes no writes after pre-seeding.
6. Full four-tool schema at every step in every condition.
7. Prompts stay neutral toward memory actions at every step.
8. All scoring is mechanical. No LLM client is imported for scoring purposes anywhere.
9. No over-sampling to reach a target N.
10. Seed strings are fixed constants quoted verbatim from `experimental_parameters.md` §4. The parallelism
    between Conditions B and C is load-bearing and must not be broken.
11. Counterbalancing is deterministic by lineage index, not random.
12. `taxonomy_codebook.md` is not revised in response to Condition A's results.

## Three Structural Requirements Worth Stating Twice

**The three conditions must differ in nothing but seed content.** Express that difference as data — a table
of seed strings — not as three code paths. If a reviewer cannot verify by inspection that A, B, and C share
every code path except the seed strings, the central comparison is not demonstrably clean.

**`validation/audit.py` must not import `scoring/taxonomy.py`.** Its purpose is re-deriving labels by an
independent path. Importing the thing it audits makes the audit circular and worthless.

**Condition A running first is operational, not a gate.** It exercises the harness at scale and supplies an
observed baseline rate for power reporting. It does not determine whether B and C run, at what N, or under
what test, and the classifier is not tuned to its results.

## Build Order

Per `implementation.md` §4:

- **Phase 0** — verify the environment before writing harness code. Inspect the installed Mnemosyne API
  directly rather than trusting the design's prose. Confirm thinking-block content is retrievable for
  verbatim logging. Verify fresh-`db_path` isolation empirically.
- **Phase 1** — core harness, validated on one hardcoded Condition A lineage.
- **Phase 2** — add seeding and counterbalancing; smoke-test each condition at N=1-2; verify by inspection
  that the three differ only in seed content.
- **Phase 3** — run Condition A to N=50, then B and C. Concurrent within a condition. Assert counterbalance
  arms come out exactly 25/25.
- **Phase 4** — mechanical scoring: strategy classification and outcome detail.
- **Phase 5** — validation: prepare the 12-lineage held-out coding subsample (labels hidden), and run the
  classifier audit on a random 10%.
- **Phase 6** — `observations.md` per condition, the achieved-power recomputation, plus the implementation
  note.

## When Reality Contradicts the Docs

Adapt to what is actually true in this environment and disclose the discrepancy plainly in the
implementation note. Do not stall on small implementation details, and do not silently work around a
mismatch without recording it.

If something requires a genuine research judgment call rather than an implementation decision — an
ambiguity in what a condition is supposed to measure, not in how to build it — stop and flag it.

## Deliverable Checklist

- [ ] `docs/` at a stable top-level path, never nested under `runs/`.
- [ ] Phase 0 verification complete, including thinking-block retrievability and store isolation.
- [ ] Core harness validated on one hardcoded lineage before condition-specific code.
- [ ] Three conditions implemented, each smoke-tested at N=1-2.
- [ ] Conditions A, B, C verified by inspection to differ only in seed content.
- [ ] All verbatim strings checked against `experimental_parameters.md`, not paraphrased or templated.
- [ ] Counterbalance arms exactly 25/25 per condition, asserted rather than assumed.
- [ ] Condition A run to N=50 first; B and C following regardless of A's observed distribution.
- [ ] Mechanical scoring implemented; no LLM client imported for scoring anywhere.
- [ ] `scoring/taxonomy.py` implements `taxonomy_codebook.md` §2's decision procedure in the same order, so
  the two can be diffed by eye.
- [ ] `validation/audit.py` confirmed by inspection not to import `scoring/taxonomy.py`.
- [ ] Both validation artifacts prepared per `interface_contract.md` §7.
- [ ] Every `observations.md` conforming, including counterbalance splits and explicit zero-counts.
- [ ] Achieved power recomputed against Condition A's observed rate.
- [ ] Implementation note written.

Begin with `project_design.md` in full, then Phase 0.
