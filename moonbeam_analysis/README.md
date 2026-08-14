# Project Moonbeam Data + Statistics Pipeline

This package implements the **data/statistics** portion of Project Moonbeam.

## Current input: Richard's scored Markdown run folders

The pipeline now reads Richard's existing per-lineage files directly. You do **not** need Richard to convert them to JSON.

Expected layout:

```text
runs/
├── condition_a/
│   ├── lineage_001.md
│   ├── lineage_002.md
│   └── ...
├── condition_b/
│   └── lineage_*.md
└── condition_c/
    └── lineage_*.md
```

Each Markdown file should look like Richard's scored lineage summaries and contain fields such as Strategy, Collapse binary, Detection, first action step, Recall count, seeded-entry final states, new entries, and arbitration direction.

The condition is inferred from `condition_a`, `condition_b`, or `condition_c`. The counterbalance arm is reconstructed from the preregistered deterministic rule: **even lineage index → A-first; odd lineage index → B-first**.

## Run it

```bash
pip install -r requirements.txt
python run_analysis.py \
  --input /path/to/runs \
  --output /path/to/analysis_output \
  --codebook /path/to/taxonomy_codebook.md
```

`--input-format auto` is the default. It prefers scored Markdown when present and still supports the older normalized-JSON input format.

If you only have one condition folder and its path does not contain `condition_a/b/c`, use:

```bash
python run_analysis.py --input /path/to/folder --condition A --output analysis_output
```

## What it produces

- `lineage_scoring.csv` — one normalized row per lineage
- `condition_a/observations.md`, `condition_b/observations.md`, `condition_c/observations.md`
- `statistics.json`
  - confirmatory two-sided Fisher exact A vs B
  - B − A action-rate difference
  - Newcombe/Wilson 95% CI
  - exploratory A/C and B/C comparisons
  - descriptive 3×5 strategy table
  - permutation test and Cramér's V
  - achieved-power / minimum-detectable-effect calculation
- counterbalance-arm breakdowns
- validation/audit helper files

## Important limitation of the scored `.md` files

Richard's scored Markdown files contain the **result of scoring**, not the complete raw step-by-step tool/action log. The pipeline therefore does not invent information that is absent.

From these Markdown files it can correctly aggregate the strategy labels, collapse binary, recall counts, final seed states, arbitration direction, condition, and counterbalance arm. It can therefore run the main statistical analyses.

However, it **cannot reconstruct exact per-step write/edit/delete/decline/error counts** from the scored summaries alone. The generated `observations.md` files explicitly mark those sections unavailable rather than printing false zeros.

Likewise, the preregistered blind human-coding validation should use the corresponding **raw lineage/action logs**, not an already-scored Markdown file that reveals the classifier's answer. The pipeline still creates a case-selection/label template, but it marks this limitation clearly.

## Statistical conventions

The confirmatory A-vs-B table is `[[A took_action, A no_action], [B took_action, B no_action]]`, with a two-sided Fisher exact test. The reported raw difference is **B − A**. Its 95% interval uses Newcombe's hybrid-score construction from Wilson score intervals.

Condition C comparisons are exploratory only. The 3×5 test is descriptive only and must not be described as an additional confirmatory significance finding.

## Legacy JSON support

The old normalized JSON input is still supported. Use `--input-format json` if needed. For Richard's current run folders, you should normally use the default `auto` mode or `--input-format markdown`.

## Automatic charts

Every successful analysis run now creates an `analysis_output/charts/` folder from `lineage_scoring.csv`.
It attempts to generate:

- `action_rate_by_condition.png`
- `strategy_by_condition.png`
- `first_action_step.png`
- `recall_count.png`
- `counterbalance_action_rate.png`
- `seed_final_states.png`
- `arbitration_direction.png`

`charts/README.md` records which charts were generated or skipped. A chart is skipped rather than fabricated when its source field contains no usable data.

## MoonBeam-master compatibility

This version is aligned to Richard's current repository layout. Point `--input` at the repository's `runs/` directory; the reader prefers `condition_a/scoring/lineage_*.md`, `condition_b/scoring/lineage_*.md`, and `condition_c/scoring/lineage_*.md` and ignores transcript Markdown as primary scoring input.

The current harness defines the preregistered collapse binary independently of the strategy label: a lineage is `took_action` when an update/edit or forget/delete targets either seeded memory, otherwise `no_action`. Current scored Markdown should therefore report only `took_action` or `no_action`. If an older summary instead reports a legacy value such as `non_arbitration`, the parser does **not** treat that as `no_action`; it derives the action binary from the seeded final states and records every such correction in `collapse_binary_normalization_audit.csv`.

With the current `MoonBeam-master` runs used for compatibility testing, all 150 scored Markdown files already used the current binary labels, so the normalization audit contained zero adjusted rows.

## Paper-oriented charts

Every run now creates `analysis_output/charts/` with eight figures and a plain-English `charts/README.md`. The first three are the recommended paper-facing figures:

1. action rate by condition with 95% Wilson intervals;
2. effect-size forest plot for B−A (confirmatory), C−A and C−B (exploratory);
3. 100% stacked strategy composition by condition.

Secondary figures show cumulative timing of first action, recall-count distributions, the counterbalance robustness split, first/second seed final states, and arbitration direction. The generated `charts/README.md` explains what each figure measures and summarizes what the current input data show. If a field is unavailable, that figure is skipped rather than populated with invented values.

## What the charts tell you?

1. Action Rate with 95% CI — Shows the percentage of lineages in each condition that edited or deleted at least one seeded memory. The confidence intervals show how much uncertainty there is around each condition’s observed action rate.

2. Effect-Size Forest Plot — Shows how large the differences in action rates are between conditions, especially the main B−A comparison. The 95% confidence intervals help show whether the observed differences are consistent with no real difference (zero).

3. Strategy Composition — Shows which behavioral strategies the model used in Conditions A, B, and C and what percentage of each condition fell into each strategy. This helps reveal behavioral differences that may be hidden when only looking at the simpler took_action/no_action outcome.

4. Cumulative First Action — Shows how quickly lineages took their first write, edit, or delete action across the seven experimental steps. It helps determine whether one condition caused models to intervene in memory earlier than another.

5. Recall Distribution — Shows how many explicit memory recall calls each lineage made in the different conditions. This helps reveal whether models searched their memory more extensively in some conditions before deciding what to do.

6. Counterbalance Robustness — Compares action rates depending on which contradictory seeded entry was presented first. It checks whether the ordering of the two memories may have influenced behavior, but it should be treated as a robustness check rather than a main finding.

7. Seed Final States — Shows whether the first and second seeded memories ended the lineage unchanged, edited, or deleted. This helps reveal how models treated the individual conflicting memories rather than simply whether they took any action at all.

8. Arbitration Direction — Looks only at lineages classified as arbitration and shows whether the model kept the first or second seeded entry. This helps identify whether models showed a tendency to favor one side of the contradiction, particularly based on presentation order.