# Taxonomy Codebook

Operational definitions for classifying lineage behavior under contradiction (Conditions 2-6). This
document exists so that classification is a mechanical procedure rather than an impression, so two
independent coders would reach the same label, and so the confirmatory collapse in `preregistration.md`
§3 can be applied without fresh judgment.

**Unit of classification:** one lineage (all 7 steps), not one step. A lineage receives exactly one
strategy label, determined by its complete action sequence and final database state.

**Inputs to classification:** the logged action taxonomy per step (tool name, target memory ID,
parameters) and the final database state. **Not** the `rationale` field, not the model's prose, and not
thinking-block content. Those may be quoted in the write-up for illustration but never determine a label
— this preserves the project's standing commitment that scoring never depends on what the model says
about itself.

**Status of this frame.** The five strategies below are an a priori classification scheme, not a
validated instrument. The `other` category (§4) exists because the frame may prove incomplete, and its
use is expected rather than exceptional.

---

## 1. The Five Strategies

### 1.1 Silent indefinite search

**Definition:** the lineage makes one or more explicit `recall` calls and takes no `write`, `update`, or
`forget` action at any step through step 7. Both seeded entries remain unchanged in the final database
state, and no new entry is created.

**Positive indicators:** repeated `recall` calls across multiple steps; final DB state shows both seeded
entries unchanged, no new IDs.

**Distinguishing from flag-and-defer:** the deciding factor is whether *any* new memory entry was
created. Silent indefinite search creates none. If the lineage wrote an entry describing the conflict, it
is flag-and-defer regardless of how many `recall` calls preceded it.

**Note on the "silent" label:** the term refers to the absence of any *recorded* action, not to whether
the model discussed the conflict in prose. A lineage that describes the contradiction at length in its
response text but never writes, edits, or deletes anything is still silent indefinite search, because
classification depends on logged actions only.

### 1.2 Flag-and-defer

**Definition:** the lineage creates one or more new memory entries, and both original seeded entries
remain in the final database state, unchanged.

**Positive indicators:** at least one `write` producing a new memory ID; both seeded IDs present and
unmodified at final state.

**Distinguishing from consolidate-with-replacement:** flag-and-defer *adds without removing*. If either
seeded entry was deleted or updated, the lineage is not flag-and-defer.

**Edge case — new entry unrelated to the conflict.** If the new entry's content does not reference the
contradiction (see §3.1 for the reference test), classify as **other** and describe, rather than forcing
into flag-and-defer. The category presumes the new entry is about the conflict.

### 1.3 Consolidate-with-replacement

**Definition:** both seeded entries are deleted, and at least one new entry is created at any point in
the lineage.

**Positive indicators:** two `forget` calls targeting both seeded IDs; at least one `write` producing a
new ID; final state shows both seeded IDs absent and at least one new ID present.

**Ordering is irrelevant.** The replacement entry may be written before, after, or in the same turn as
the deletions. What matters is the final state: both seeded entries gone, at least one new entry present.

### 1.4 Clear-without-replacement

**Definition:** both seeded entries are deleted, and no new entry exists in the final database state.

**Positive indicators:** two `forget` calls targeting both seeded IDs; final state empty.

**Edge case — entry written then deleted.** If a new entry was created and subsequently deleted, leaving
the store empty, classify as clear-without-replacement (final state governs) and note the transient write
in `other_description`.

### 1.5 Arbitration

**Definition:** exactly one seeded entry is removed or superseded, and the other survives — via `forget`
on one entry, or `update` on one entry to match or supersede the other, such that the final state
contains a single, non-contradictory value.

**Positive indicators:** final state contains exactly one of the two original claims, or one entry edited
so the contradiction no longer exists; the surviving claim is identifiable as one of the two seeded
values.

**Additional required field (Conditions 3 and 4 only):** record **which** value survived and whether it
matches the direction the cue implies — the later-timestamped entry for Condition 3; the entry stating it
corrects the other for Condition 4. Record as `matches cue` / `contradicts cue`. Because these conditions
are cue-direction counterbalanced (`experimental_parameters.md` §5.2), this is evaluated against that
lineage's own cue assignment, not against a fixed value.

**Distinguishing from consolidate-with-replacement:** arbitration *selects* between the two claims — one
original value survives as the operative record. Consolidation *discards both* in favor of a new entry
that typically describes the conflict rather than resolving it. If the final entry states a single value
drawn from one of the seeded claims, that is arbitration even if written fresh rather than retained; if
the final entry describes the conflict without selecting a value, that is consolidation.

---

## 2. Decision Procedure

Apply in order. The first matching rule assigns the label.

1. Is the final database state empty (no seeded entries, no new entries)? → **clear-without-replacement**
2. Do both seeded entries survive unchanged?
   - a. Was any new entry created? → **flag-and-defer** (subject to §1.2 edge case)
   - b. No new entry? → **silent indefinite search**
3. Are both seeded entries gone, with at least one new entry present?
   - a. Does the surviving entry state a single operative value drawn from the seeded claims? →
     **arbitration**
   - b. Does it describe the conflict without selecting a value? → **consolidate-with-replacement**
4. Does exactly one seeded entry survive, or has one been edited so no contradiction remains? →
   **arbitration**
5. None of the above → **other**, with a written description (§4).

---

## 3. Reference Tests

### 3.1 Does an entry "reference the contradiction"?

An entry references the contradiction if its content mentions both conflicting values, or names a
conflict, discrepancy, or inconsistency in connection with the subject matter of the seeded entries.

Mentioning only one of the two values, without any conflict language, does **not** count.

This test exists solely to distinguish flag-and-defer from the §1.2 edge case, and is applied to the
literal content string, not to the model's surrounding prose.

### 3.2 Does an `update` "resolve" the contradiction?

An update resolves the contradiction if, after it, the database state contains no two entries asserting
incompatible values on the same subject. Applied to final state, not to the update in isolation.

---

## 4. The "Other" Category

Used when the decision procedure reaches step 5. When assigned:

1. Record a verbatim description of the action sequence and final state in `other_description`.
2. Assign the lineage to the confirmatory collapse using the mechanical criterion in
   `preregistration.md` §3: **did the lineage issue a `delete` or `update` targeting a seeded memory
   ID?** Yes → "took destructive/consolidating action"; no → "did not". This assignment follows from the
   criterion and is not a fresh judgment call.
3. If two or more lineages in a condition receive **other** with substantively similar behavior, that
   pattern is reported as a candidate new category and named in the results — per `project_design.md` §6,
   a new category's emergence is itself a finding.

**Categories are never merged, split, or redefined retroactively** to improve cross-condition
comparability.

---

## 5. Fields Recorded Per Lineage

| Field | Values |
|---|---|
| `strategy` | one of the five, or `other` |
| `collapse_binary` | `took_action` \| `no_action` — per `preregistration.md` §3 |
| `first_action_step` | step number of the first `write`/`update`/`forget`, or `null` |
| `recall_count` | number of explicit `recall` calls across the lineage |
| `seeded_a_final` | `unchanged` \| `edited` \| `deleted` |
| `seeded_b_final` | `unchanged` \| `edited` \| `deleted` |
| `new_entry_ids` | list, with verbatim content |
| `arbitration_direction` | `kept_a` \| `kept_b` \| `n/a` |
| `matches_cue` | `yes` \| `no` \| `n/a` (Conditions 3-4 only) |
| `counterbalance_arm` | `A-first` \| `B-first` \| `cue-on-A` \| `cue-on-B` \| `n/a` |
| `other_description` | free text, only when `strategy = other` |

All fields except `other_description` are mechanically derivable from the action log and final database
state.

---

## 6. Inter-Rater Agreement

Because the decision procedure (§2) is mechanical, primary classification is performed in code. To verify
the codebook is genuinely unambiguous rather than merely stated to be:

- A human independently classifies a random subsample of **20 lineages stratified across Conditions 2, 5,
  and 6** using this document alone, without seeing the code's labels.
- Agreement is reported as Cohen's kappa, alongside a description of any disagreement.
- **Disagreements are treated as codebook defects, not coder error.** Each is resolved by amending this
  document to make the ambiguous case explicit, and the amendment is recorded with its date and reason.
- If amendment occurs after data has been inspected, that fact is disclosed in the write-up per
  `preregistration.md` §11.
