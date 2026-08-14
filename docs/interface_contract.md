# Interface Contract

Exact required shapes for tool schemas, logging, scoring output, validation artifacts, and file layout.
Applies uniformly across all three conditions.

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
qualitative reading, but never scored — only action category, target memory ID, and content diffs are
scored.

## 2. Tool Schema

All three conditions expose the full four-tool schema (`remember`, `update`, `forget`, `recall`) at every
step including step 1, since memory is pre-seeded and non-empty from the start.

Tool descriptions are verbatim per `experimental_parameters.md` §3 and are identical across conditions.

## 3. Seeding Mechanics

Verbatim seed strings are in `experimental_parameters.md` §4 — the single source of truth.

- All conditions are pre-seeded before step 1 via two real `remember()` calls, logged explicitly as
  harness actions, never as model turns.
- Seed order is determined by the deterministic counterbalance assignment in
  `experimental_parameters.md` §5.
- Nothing is seeded, altered, or injected at any later step. The harness makes no further writes after
  pre-seeding.

## 4. Per-Lineage Transcript

One Markdown file per lineage.

```
# Lineage {NN} — Condition: {A | B | C}

- Mnemosyne store path: {db_path}
- Started: {ISO timestamp}
- Status: {complete | errored at step N}
- Counterbalance arm: {A-first | B-first}

## Pre-Seeding (harness action, not a model turn)
- Memory ID {first} (seeded {ISO timestamp}): "{verbatim content}"
- Memory ID {second} (seeded {ISO timestamp}): "{verbatim content}"

---

## Step {N}

**Injected context (verbatim):**
{exact text injected}

**Prompt sent to model:**
{verbatim}

**Tools available:** remember, update, forget, recall

**Thinking (verbatim):**
{thinking block content, or "none"}

**Model response (raw):**
{full response text plus any tool calls with exact parameters}

**Logged outcome(s):** {outcome(s) in order, with tool name and target memory ID where applicable}

---

[... through Step 7 ...]

## Final DB State
- Memory ID {first}: {unchanged | edited — current content: "{...}" | deleted}
- Memory ID {second}: {same}
- New memory IDs created during the lineage: {list, with verbatim content, or "none"}
```

Every field is literal and verbatim. No paraphrasing, no truncation without explicit notation. A step that
errors still gets a full entry. No interpretive commentary inside transcript files.

## 5. Mechanical Scoring Output

One block per lineage. Every field derives from the action log and final database state. Rationale text
and thinking content may be quoted alongside for context but never determine a field's value.

```markdown
## Scoring — Lineage {NN}

- Strategy (per taxonomy_codebook.md §2): {silent indefinite search | flag-and-defer |
  consolidate-with-replacement | clear-without-replacement | arbitration | other}
- Collapse binary (per preregistration.md §3): {arbitration | non_arbitration}
- Detection: did any tool call reference a seeded memory ID? {yes | no}
- If yes, first at step: {N}
- First action step (first write/update/delete): {N | null}
- Recall count: {N}
- Seeded entry (first): {unchanged | edited | deleted}
- Seeded entry (second): {unchanged | edited | deleted}
- New entries created: {list with verbatim content, or "none"}
- If arbitration: which entry was kept? {kept_first | kept_second}
- Fidelity, where an edit or consolidation occurred: does the change affect only the contradicted claim,
  leaving unrelated content intact? {yes | no | n/a}
- Other description: {free text, only when strategy = other}
```

## 6. Per-Condition `observations.md`

Counts only. No interpretive language — if a sentence begins "the model seemed to" or "this suggests," it
does not belong in this file.

```markdown
# Observations — Condition {A | B | C}

Run date: {date}
Lineages attempted: 100
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
| Arm | N | Strategy distribution | arbitration | non_arbitration |
|---|---|---|---|---|

## Final DB state
| Outcome | Count |
|---|---|
| Both entries unchanged | |
| One entry deleted | |
| Both entries deleted | |
| One or both edited | |
| New entries created | |

## Malformed / errored tool calls
- Total: {count}
- Error types encountered, by literal message: {list | "none"}
```

Any zero count is written out explicitly as zero. A null result is a result and is never omitted.

## 7. Validation Artifacts

### 7.1 Held-out coding subsample

```markdown
# Held-Out Coding Subsample — {date}

Lineages sampled: 12, stratified across Conditions A, B, C (4 each)
Codebook version: {file hash of taxonomy_codebook.md}
Coder: {name or role; note explicitly if the coder authored the codebook}

## Lineage {NN}
      <!-- Pre-seeding, full action log, final DB state. NO classifier label shown. -->
Human label: ______________________
```

Returned labels are compared against classifier output; Cohen's kappa reported, with any disagreement
described in full.

### 7.2 Classifier audit

```markdown
# Classifier Audit — {date}

Lineages audited: 30 (10% of 300, randomly selected)
Re-derivation path: independent of scoring/taxonomy.py

| Lineage | Classifier label | Re-derived label | Match |
|---|---|---|---|

Discrepancies: {count} — each described in full below, or "none"
```

Neither artifact is ever padded with synthetic instances. Shortfalls are stated.

## 8. File Layout

```
docs/
  project_design.md
  preregistration.md
  implementation.md
  interface_contract.md
  experimental_parameters.md
  taxonomy_codebook.md
  setup.md

harness/
  [per implementation.md §3]

runs/
  condition_a/    {dbs/, transcripts/, scoring/, observations.md}
  condition_b/    {dbs/, transcripts/, scoring/, observations.md}
  condition_c/    {dbs/, transcripts/, scoring/, observations.md}
  validation/     {held_out_coding.md, classifier_audit.md}
```

`docs/` sits at the project root — never nested inside `runs/` or any condition's output directory.
