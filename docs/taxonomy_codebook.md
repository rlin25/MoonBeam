# Taxonomy Codebook

Operational definitions for classifying lineage behavior under contradiction. This document exists so that
classification is a mechanical procedure rather than an impression, so two independent coders reach the
same label, and so the confirmatory collapse in `preregistration.md` §3 can be applied without fresh
judgment.

**Unit of classification:** one lineage (all 7 steps), not one step. A lineage receives exactly one
strategy label, determined by its complete action sequence and final database state.

**Inputs to classification:** the logged action taxonomy per step (tool name, target memory ID, parameters)
and the final database state. **Not** the `rationale` field, not the model's prose, and not thinking-block
content. Those may be quoted in the write-up for illustration but never determine a label. This is what
makes the procedure replicable by a human coder rather than an interpretive exercise.

**Status of this frame.** The five strategies below are an a priori classification scheme, not a validated
instrument. The `other` category (§4) exists because the frame may prove incomplete, and its use is
expected rather than exceptional.

**Expect sparse categories.** A prior 150-lineage run (N=50 per condition) found two of the five categories
— flag-and-defer, consolidate-with-replacement — entirely unpopulated across all three conditions combined
(`preregistration.md` §4). At N=100 some categories may remain thinly populated or empty. This is
anticipated, not a defect: the taxonomy's contribution is describing *what strategies
exist*, not estimating their proportions. The confirmatory analysis rests on the collapsed binary
(`preregistration.md` §3), which is unaffected by how sparsely the five categories populate.

**This document is fixed before data collection and is not revised in response to Condition A.** Condition
A runs first for operational reasons (`project_design.md` §9); the categories and decision procedure below
were fixed beforehand. Any amendment after data inspection is disclosed per `preregistration.md` §9.

**Naming note.** The two seeded entries are referred to as *first* and *second* by seeding order, which
varies by counterbalance arm (`experimental_parameters.md` §5). Classification never depends on which
content occupies which position.

---

## 1. The Five Strategies

### 1.1 Silent indefinite search

**Definition:** the lineage takes no `write`, `update`, or `forget` action at any step through step 7. Both
seeded entries remain unchanged in the final database state, and no new entry is created.

**Positive indicators:** repeated `recall` calls across multiple steps; final DB state shows both seeded
entries unchanged, no new IDs.

**Distinguishing from flag-and-defer:** the deciding factor is whether *any* new memory entry was created.
Silent indefinite search creates none. If the lineage wrote an entry describing the conflict, it is
flag-and-defer regardless of how many `recall` calls preceded it.

**Note on "silent":** the term refers to the absence of any *recorded* action, not to whether the model
discussed the conflict in prose. A lineage that describes the contradiction at length in its response text
but never writes, edits, or deletes anything is still silent indefinite search, because classification
depends on logged actions only.

**Edge case — no recall calls at all.** A lineage that takes no action and makes no `recall` calls
(declining at every step) is still classified here. The definition requires no action; `recall` activity is
a positive indicator, not a requirement.

### 1.2 Flag-and-defer

**Definition:** the lineage creates one or more new memory entries, and both original seeded entries remain
in the final database state, unchanged.

**Positive indicators:** at least one `write` producing a new memory ID; both seeded IDs present and
unmodified at final state.

**Distinguishing from consolidate-with-replacement:** flag-and-defer *adds without removing*. If either
seeded entry was deleted or updated, the lineage is not flag-and-defer.

**Edge case — new entry unrelated to the conflict.** If the new entry's content does not reference the
contradiction (see §3.1 for the reference test), classify as **other** and describe. The category presumes
the new entry is about the conflict.

### 1.3 Consolidate-with-replacement

**Definition:** both seeded entries are deleted, and at least one new entry is created at any point in the
lineage.

**Positive indicators:** two `forget` calls targeting both seeded IDs; at least one `write` producing a new
ID; final state shows both seeded IDs absent and at least one new ID present.

**Ordering is irrelevant.** The replacement may be written before, after, or in the same turn as the
deletions. What matters is the final state: both seeded entries gone, at least one new entry present.

### 1.4 Clear-without-replacement

**Definition:** both seeded entries are deleted, and no new entry exists in the final database state.

**Positive indicators:** two `forget` calls targeting both seeded IDs; final state empty.

**Edge case — entry written then deleted.** If a new entry was created and subsequently deleted, leaving
the store empty, classify as clear-without-replacement (final state governs) and note the transient write
in `other_description`.

### 1.5 Arbitration

**Definition:** exactly one seeded entry is removed or superseded, and the other survives — via `forget` on
one entry, or `update` on one entry to match or supersede the other, such that the final state contains a
single, non-contradictory claim.

**Positive indicators:** final state contains exactly one of the two original claims, or one entry edited
so the contradiction no longer exists; the surviving claim is identifiable as one of the two seeded values.

**Distinguishing from consolidate-with-replacement:** arbitration *selects* between the two claims — one
original claim survives as the operative record. Consolidation *discards both* in favor of a new entry that
typically describes the conflict rather than resolving it. If the final entry states a single claim drawn
from one of the seeded entries, that is arbitration even if written fresh rather than retained; if the
final entry describes the conflict without selecting, that is consolidation.

---

## 2. Decision Procedure

Apply in order. The first matching rule assigns the label.

1. Is the final database state empty (no seeded entries, no new entries)? → **clear-without-replacement**
2. Do both seeded entries survive unchanged?
   - a. Was any new entry created? → **flag-and-defer** (subject to §1.2 edge case)
   - b. No new entry? → **silent indefinite search**
3. Are both seeded entries gone, with at least one new entry present?
   - a. Does the surviving entry state a single operative claim drawn from the seeded entries? →
     **arbitration**
   - b. Does it describe the conflict without selecting? → **consolidate-with-replacement**
4. Does exactly one seeded entry survive, or has one been edited so no contradiction remains? →
   **arbitration**
5. None of the above → **other**, with a written description (§4).

---

## 3. Reference Tests

### 3.1 Does an entry "reference the contradiction"?

An entry references the contradiction if its content mentions both conflicting claims, or names a conflict,
discrepancy, or inconsistency in connection with the subject matter of the seeded entries.

Mentioning only one of the two claims, without any conflict language, does **not** count.

This test exists solely to distinguish flag-and-defer from the §1.2 edge case, and is applied to the
literal content string, not to the model's surrounding prose.

### 3.2 Does an `update` "resolve" the contradiction?

An update resolves the contradiction if, after it, the database state contains no two entries asserting
incompatible claims on the same subject. Applied to final state, not to the update in isolation.

---

## 4. The "Other" Category

Used when the decision procedure reaches step 5. When assigned:

1. Record a verbatim description of the action sequence and final state in `other_description`.
2. Assign the lineage to the confirmatory collapse using the mechanical criterion in `preregistration.md`
   §3: **does the lineage's final state contain exactly one operative claim drawn from the seeded
   entries?** Yes → `arbitration`; no → `non_arbitration`. This follows from the criterion and is not a
   fresh judgment call — by construction, `other` almost always resolves to `non_arbitration`, since
   reaching step 5 of the decision procedure means the lineage did not fit the operative-claim pattern any
   of the earlier steps already check for.
3. If two or more lineages receive **other** with substantively similar behavior, that pattern is reported
   as a candidate new category and named in the results — per `project_design.md` §6, a new category's
   emergence is itself a finding.

**Categories are never merged, split, or redefined retroactively** to improve cross-condition comparability.

---

## 5. Fields Recorded Per Lineage

| Field | Values |
|---|---|
| `strategy` | one of the five, or `other` |
| `collapse_binary` | `arbitration` \| `non_arbitration` — per `preregistration.md` §3 |
| `first_action_step` | step number of the first `write`/`update`/`forget`, or `null` |
| `recall_count` | number of explicit `recall` calls across the lineage |
| `seeded_first_final` | `unchanged` \| `edited` \| `deleted` |
| `seeded_second_final` | `unchanged` \| `edited` \| `deleted` |
| `new_entry_ids` | list, with verbatim content |
| `arbitration_direction` | `kept_first` \| `kept_second` \| `n/a` |
| `counterbalance_arm` | `A-first` \| `B-first` |
| `other_description` | free text, only when `strategy = other` |

All fields except `other_description` are mechanically derivable from the action log and final database
state.

---

## 6. Held-Out Human Coding

Because the decision procedure (§2) is mechanical, primary classification is performed in code. To verify
the codebook is genuinely unambiguous rather than merely stated to be:

- A human independently classifies **12 lineages, stratified across the three conditions** (4 each), using
  this document alone and without seeing the classifier's labels.
- Each presented lineage shows: the pre-seeded entries, the full per-step action log (tool name, target
  memory ID, parameters), and the final database state. No prose, no rationale text, no thinking content —
  the same inputs the classifier uses.
- Agreement is reported as Cohen's kappa, alongside a description of any disagreement.
- **Disagreements are treated as codebook defects, not coder error.** Each is resolved by amending this
  document to make the ambiguous case explicit, and the amendment is recorded with its reason and its
  timing relative to data inspection (`preregistration.md` §9).
- Where possible the coder should not be this document's author, since knowing the intent behind a
  definition produces more consistent application than a stranger would achieve. If that is not possible,
  the limitation is stated plainly in the write-up.

Expected effort: roughly 40-60 minutes including reading this document.
