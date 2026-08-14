# Interface Contract

Exact required shapes for tool schemas, seeded content, logging, scoring output, and file layout.
Applies uniformly across all conditions unless a condition-specific exception is stated.

## 1. Action Taxonomy

| Outcome | Definition |
|---|---|
| `write` | Model called `remember`. |
| `edit` | Model called `update`. |
| `delete` | Model called `forget`. |
| `recall` | Model called `recall` explicitly — distinct from the harness's automatic `get_context()` injection, which is not a model action and is never logged as one. |
| `decline` | No tool call in that step's response. |
| `error` | Structural failure: API error, or a malformed tool call the harness could not parse. Distinct from a genuine `decline`. |

A single step may produce several logged events (e.g. `recall` then `delete` in one turn). Log each in
order under that step.

Every tool schema includes a required `rationale: string` parameter. It is logged and available for
qualitative reading, but is never scored as primary evidence — only action category, target memory ID,
and content diffs are scored.

## 2. Tool Schema by Condition and Step

| Condition | Step 1 | Steps 2-7 |
|---|---|---|
| 1 — Spontaneous initiation | write-only | full |
| 2 — Arbitrary, no cue | full | full |
| 3 — Arbitrary, timestamp cue | full | full |
| 4 — Arbitrary, correction cue | full | full |
| 5 — Self-referential, no cue | full | full |
| 6 — First-person bridge | full | full |
| 7 — Self-continuity (all three sub-conditions) | write-only | full |
| Control baseline | write-only | full |

"Full" = `remember`, `update`, `forget`, `recall`. Write-only at step 1 applies where memory starts
empty and edit/delete would be meaningless; full-from-step-1 applies where memory is pre-seeded.

## 3. Seeded and Injected Content

All verbatim strings are specified in `experimental_parameters.md` §4 and are reproduced there as the
single source of truth. This section specifies only the *mechanics* of seeding.

- Conditions 2-6 are pre-seeded before step 1 via two real `remember()` calls, logged explicitly as
  harness actions, never as model turns.
- Seed order is determined by the counterbalancing scheme in `experimental_parameters.md` §5,
  deterministically by lineage index.
- Condition 7's reset trigger fires at the condition-specific step for eligible lineages only, altering
  the stored content of the model's own step-1 write and injecting a system note.

## 4. Per-Lineage Transcript

One Markdown file per lineage.

```
# Lineage {NN} — Condition: {condition_name}

- Mnemosyne store path: {db_path}
- Started: {ISO timestamp}
- Status: {complete | errored at step N}
- Counterbalance arm: {A-first | B-first | cue-on-A | cue-on-B | n/a}
- Eligibility: {yes | no | n/a}
      <!-- n/a for Conditions 2-6 (always pre-seeded); yes/no for Conditions 1 and 7,
           determined by whether step 1 produced a real write -->

## Pre-Seeding (harness action, not a model turn)
      <!-- Conditions 2-6 only -->
- Memory ID {first} (seeded {ISO timestamp}): "{verbatim content}"
- Memory ID {second} (seeded {ISO timestamp}): "{verbatim content}"

---

## Step {N}

**Injected context (verbatim):**
{exact text injected, or "Your memory is currently empty."}

**Prompt sent to model:**
{verbatim}

**Tools available:** {list}

**Thinking (verbatim):**
{thinking block content, or "none"}

**Model response (raw):**
{full response text plus any tool calls with exact parameters}

**Logged outcome(s):** {outcome(s) in order, with tool name and target memory ID where applicable}

---

## Reset Trigger (harness action, not a model turn)
      <!-- Condition 7 eligible lineages only, at the condition-specific step, placed
           immediately before that step's own entry -->
- Original step-1 content (verbatim): "{...}"
- Altered content injected from this step onward (verbatim): "{...}"
- System note injected (verbatim): "{...}"

---

## Final DB State
- Memory ID {first}: {unchanged | edited — current content: "{...}" | deleted}
- Memory ID {second}: {same}
- New memory IDs created during the lineage: {list, with verbatim content, or "none"}
```

Every field is literal and verbatim. No paraphrasing, no truncation without explicit notation. A step
that errors still gets a full entry. No interpretive commentary inside transcript files.

## 5. Mechanical Scoring Output (Passes 3 and 5)

```markdown
## Mechanical Scoring — Lineage {NN}

### Pass 3 — Recall accuracy
      <!-- Condition 7 only, where a step-1 ground truth exists -->
- Recall-step statement vs. step-1 logged action: {similarity score or category}

### Pass 5 — Contradiction outcome and fidelity
      <!-- Conditions 2-6, and Condition 7's eligible lineages -->
- Detection: did any tool call reference a seeded/altered memory ID? {yes | no}
- If yes, first at step: {N}
- Strategy (per taxonomy_codebook.md): {silent indefinite search | flag-and-defer |
  consolidate-with-replacement | clear-without-replacement | arbitration | other}
- Collapse binary (per preregistration.md §3): {took_action | no_action}
- If arbitration: which entry was kept? {kept_A | kept_B}
- If arbitration in Conditions 3-4: does the kept entry match the cue direction?
  {matches cue | contradicts cue | n/a}
- Fidelity, where an edit or consolidation occurred: does the change affect only the contradicted
  claim, leaving unrelated true content intact? {yes | no | n/a}
```

Derived entirely from database-state diffs and tool-call parameters. Rationale text and thinking content
may be quoted alongside for context but never determine a field's value.

## 6. LLM-Judge Scoring Output (Passes 2 and 4)

```markdown
## LLM-Judge Scoring — Lineage {NN}

### Pass 2 — Intent-action match
      <!-- Condition 7, baseline and persona-swap sub-conditions -->
- Coherence pre-check: {pass | fail}   <!-- fail excludes from downstream scoring -->
- Category: {exact | partial | unrelated | contradictory}

### Pass 4 — Ownership/continuity language
      <!-- All conditions -->
- Category: {first_person_ownership | third_person_disownership | mixed | neutral}
```

Both passes use forced structured output — never free-text parsing of judge responses.

## 7. Validation Artifacts

### 7.1 Held-out human coding subsample

```markdown
# Held-Out Coding Subsample — {date}

Lineages sampled: 20, stratified across Conditions 2, 5, 6
Codebook version: {file hash of taxonomy_codebook.md}

## Instances
      <!-- Per lineage: the raw transcript and final DB state, with NO classifier label shown -->
```

Returned human labels are compared against classifier output; Cohen's kappa is reported.

### 7.2 Judge-pass agreement subsample

```markdown
# Judge Agreement Subsample — {date}

Target size: 20-30
Actual size: {N}   <!-- if below target, state the shortfall and its cause -->

## Allocation by condition
| Condition | Instances sampled |
|---|---|

## Instances
      <!-- Per instance: judge output beside the verbatim transcript excerpt it scored -->
```

### 7.3 Mechanical-classifier audit

```markdown
# Mechanical Classifier Audit — {date}

Lineages audited: {10% of total, randomly selected}
Re-derivation path: independent of scoring/taxonomy.py output

| Lineage | Classifier label | Re-derived label | Match |
|---|---|---|---|

Discrepancies: {count} — each described in full below, or "none"
```

Never padded with synthetic instances. Shortfalls are stated.

## 8. Per-Condition `observations.md`

Counts only. No interpretive language — if a sentence begins "the model seemed to" or "this suggests,"
it does not belong in this file.

```markdown
# Observations — {Condition Name}

Run date: {date}
Lineages attempted: {N}
Completed without error: {N}
Errored (and at which step): {list | "none"}

## Action taxonomy by step position
| Step | write | edit | delete | recall | decline | error |
|------|-------|------|--------|--------|---------|-------|

## Pooled totals
{same columns, summed}

## Strategy distribution
| Strategy | Count | Collapse binary |
|---|---|---|

## By counterbalance arm
      <!-- Conditions 2-6 only -->
| Arm | N | Strategy distribution | Collapse binary (took_action / no_action) |
|---|---|---|---|

## Condition-specific section
      <!-- Conditions 1 and 7: eligibility counts.
           Conditions 2-6: final DB state table.
           Conditions 3-4: additionally, arbitration direction relative to the cue. -->

## Malformed / errored tool calls
- Total: {count}
- Error types encountered, by literal message: {list | "none"}
```

Any zero count is written out explicitly as zero. A null result is a result and is never omitted.

## 9. File Layout

```
docs/
  project_design.md
  project_specification.md
  implementation_plan.md
  interface_contract.md
  experimental_parameters.md
  taxonomy_codebook.md
  preregistration.md
  setup.md

harness/
  [per implementation_plan.md §2]

runs/
  c1_spontaneous/            {dbs/, transcripts/, observations.md}
  c2_arbitrary_no_cue/       {dbs/, transcripts/, observations.md}
  c3_arbitrary_timestamp/    {dbs/, transcripts/, observations.md}
  c4_arbitrary_correction/   {dbs/, transcripts/, observations.md}
  c5_self_referential/       {dbs/, transcripts/, observations.md}
  c6_first_person_bridge/    {dbs/, transcripts/, observations.md}
  c7_self_continuity/
    baseline/                {dbs/, transcripts/, observations.md}
    no_history/              {dbs/, transcripts/, observations.md}
    persona_swap/            {dbs/, transcripts/, observations.md}
  control_baseline/          {dbs/, transcripts/, observations.md}
  scoring/                   {mechanical/, llm_judge/}
  validation/                {held_out_coding.md, judge_agreement.md, classifier_audit.md}
```

`docs/` sits at the project root — never nested inside `runs/` or any condition's output directory.
