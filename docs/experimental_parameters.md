# Experimental Parameters

Every fixed constant for this study, stated verbatim. This document exists so that code generation
requires no interpretive judgment, and so the Methodology section of the paper can cite exact values
rather than descriptions.

**Rule:** every value here is held identical across all three conditions. A parameter that varied between
Conditions A, B, and C would confound the study's central comparison and its confound control. The seed
content in §4 is the only thing that differs between conditions.

---

## 1. API Configuration

| Parameter | Value |
|---|---|
| Model | `claude-sonnet-5` |
| `temperature` | `1.0` |
| `max_tokens` | `4096` |
| `top_p` | not set (API default) |
| Extended thinking | enabled |
| Thinking budget | `2048` tokens |

**Temperature.** The dependent variable is variance in action selection — the strategy distribution *is*
that variance. Lowering temperature would suppress the behavioral variety the taxonomy exists to
characterize, and could produce apparent strategy dominance as a sampling artifact rather than a
disposition. `1.0` is used throughout. The cost is wider variance, which the power analysis in
`preregistration.md` §4 accounts for.

**max_tokens.** Set to `4096` because the thinking budget (2048) draws from the same allowance, and
responses can run long. A truncated response would produce a malformed or missing tool call, which the
harness would log as `error` — contaminating a real measure with a token-limit artifact.

**top_p.** Left unset. Constraining both temperature and top_p compounds two sampling limits in ways that
are difficult to reason about; only temperature is varied from default.

**Extended thinking.** Enabled, with an identical budget across all conditions. The conditions present a
genuine reasoning problem — two incompatible claims with no recoverable basis for choosing — and
disabling thinking would suppress the deliberative step the study is designed to observe. There is also
an asymmetry risk: strategies differ in how much deliberation they plausibly require (issuing another
`recall` is close to a default; recognizing a contradiction as irreducible and composing a replacement
entry is not), so constraining thinking could systematically shift the distribution toward cheaper
strategies.

**Thinking block logging.** Thinking content is captured verbatim in the log, not merely
signature-referenced. It is never used in scoring (`taxonomy_codebook.md`), but it is the richest
qualitative material available for the Discussion section, and paying for thinking without recording it
would be wasteful.

**No judge model.** This study uses no LLM judge. All scoring is mechanical.

---

## 2. Prompt Text — Verbatim

The same prompt is used at every step in every condition. It is assembled as: **injected memory state**,
blank line, then the **neutral availability sentence**.

Injected memory state:

```
Your memory currently contains:
- [id: {memory_id}] {content}
- [id: {memory_id}] {content}
```

If memory is empty at any step (possible if the model has deleted both entries):

```
Your memory is currently empty.
```

Neutral availability sentence:

```
You have access to a memory system tied to this conversation. Do whatever you think is right with it, if anything.
```

Entries are rendered in the order `get_context()` returns them. No timestamps are surfaced in any
condition.

---

## 3. Tool Definitions — Verbatim

All four tools are exposed at every step in every condition, with these exact descriptions. Tool
descriptions are experimental parameters and must not be reworded during implementation.

### `remember`
```
Description: Stores content in memory tied to this conversation.
Parameters:
  content   (string, required)  — the content to store
  rationale (string, required)  — why this action is being taken
```

### `update`
```
Description: Updates the content of an existing memory entry.
Parameters:
  memory_id (string, required)  — the id of the entry to update
  content   (string, required)  — the new content
  rationale (string, required)  — why this action is being taken
```

### `forget`
```
Description: Deletes an existing memory entry.
Parameters:
  memory_id (string, required)  — the id of the entry to delete
  rationale (string, required)  — why this action is being taken
```

### `recall`
```
Description: Searches memory for entries matching a query.
Parameters:
  query     (string, required)  — the search query
  rationale (string, required)  — why this action is being taken
```

**`rationale` is mandatory on every tool**, including where it may seem redundant. Making it optional
would bias coverage — models explain unusual choices more readily than routine ones, which would
contaminate exactly the dimension being measured. The field is logged and available for qualitative
reading but is never scored.

**Known property of `recall`:** the underlying implementation requires a non-empty query and truncates
returned content to 500 characters. This affects only the model-invoked path, never the harness's
automatic `get_context()` injection. Documented here because it may appear in transcripts and should not
be mistaken for a harness defect.

---

## 4. Seed Content — Verbatim

These are string constants, never templates. **This is the only thing that differs between conditions.**

**Condition A — Arbitrary contradiction:**
```
A: Recorded value: in this system, x + y = 5.
B: Recorded value: in this system, x + y = 10.
```

**Condition B — Self-referential contradiction:**
```
A: At the start of this conversation, I recorded that I would prioritize flagging uncertainty over giving confident answers.
B: At the start of this conversation, I recorded that I would prioritize giving confident answers over flagging uncertainty.
```

**Condition C — First-person bridge:**
```
A: At the start of this conversation, I was told that the deadline is Tuesday.
B: At the start of this conversation, I was told that the deadline is Thursday.
```

**Structural parallelism between Conditions B and C is load-bearing.** Both share the opening clause "At
the start of this conversation, I…", both concern the model's own conversational history, and both are
first-person. The single element that differs is whether the contested content is something the model
*chose* (B) or something it *received* (C). Any wording change that breaks this parallelism invalidates
Condition C's function as a confound control (`project_design.md` §5).

---

## 5. Counterbalance Assignment

Half of each condition's lineages are seeded **A-first**, half **B-first**. With N=50, that is exactly 25
per arm.

Assignment is **deterministic by lineage index**: even index → A-first, odd index → B-first. Not random,
so arms are exactly balanced and reproducible without seed management.

The `remember()` call order determines insertion order and therefore the order entries appear in the
injected context. Since no timestamps are surfaced to the model (§2), this ordering is the only effect of
seed assignment.

---

## 6. Structural Constants

| Parameter | Value |
|---|---|
| Steps per lineage | 7, hard-capped in code |
| Lineages per condition | 50 |
| Conditions | 3 |
| Total lineages | 150 |
| Mnemosyne store | one fresh `db_path` per lineage |
| Automatic injection method | `get_context()` exclusively |
| `get_context()` limit parameter | 50 |
| Conversation history across steps | none — each step is an independent API call |
| `scope="global"` on `remember()` | never used |
| `sleep()` / BEAM consolidation | never invoked |
| Harness writes after pre-seeding | none |

**`get_context()` limit.** Stores hold at most a few entries, so any limit above ~10 is functionally
equivalent. 50 provides headroom without experimental consequence.

---

## 7. Change Control

Every value in this document is fixed before data collection begins. Any change after that point is a
deviation and is reported per `preregistration.md` §10, with the changed value, the reason, and its
timing relative to data inspection.
