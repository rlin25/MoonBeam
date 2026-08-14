# Treylon — Project Moonbeam Data + Statistics Pipeline

This package implements Treylon's **data/statistics** portion of Project Moonbeam.

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
  - confirmatory two-sided Fisher exact A vs B on **arbitration vs non_arbitration**
  - **A − B arbitration-rate difference**
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

**Current confirmatory DV:** `arbitration` vs `non_arbitration`, derived mechanically from the final strategy label. `arbitration` means the lineage's strategy is `arbitration`; every other strategy, including `other`, is `non_arbitration`.

The confirmatory A-vs-B table is `[[A arbitration, A non_arbitration], [B arbitration, B non_arbitration]]`, with a two-sided Fisher exact test. The reported raw difference is **A − B**, so A=85% and B=25% is reported as **+60 percentage points**. Its 95% interval uses Newcombe's hybrid-score construction from Wilson score intervals.

Condition C comparisons are exploratory only. The 3×5 test is descriptive only and must not be described as an additional confirmatory significance finding.

The older `took_action/no_action` variable is retained in `lineage_scoring.csv` and `statistics.json` only as a **retired descriptive diagnostic**. It is not used for the confirmatory Fisher test, confirmatory confidence interval, achieved-power/MDE calculation, or counterbalance robustness figure.

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

The parser preserves Richard's older `took_action/no_action` field when present, but the analysis now derives the **current confirmatory DV directly from `strategy`**: `arbitration` versus `non_arbitration`. This prevents an older action-collapse label from silently driving the headline statistics.

`collapse_binary_normalization_audit.csv` still records any legacy action labels that had to be normalized for descriptive action analyses, but those labels do not affect the confirmatory arbitration analysis.

## Paper-oriented charts

Every run now creates `analysis_output/charts/` with eight figures and a plain-English `charts/README.md`. The first three are the recommended paper-facing figures:

1. arbitration rate by condition with 95% Wilson intervals;
2. effect-size forest plot for **A−B** (confirmatory), A−C and B−C (exploratory);
3. 100% stacked strategy composition by condition.

Secondary figures show cumulative timing of first action, recall-count distributions, the counterbalance **arbitration-rate** robustness split, first/second seed final states, and arbitration direction. The generated `charts/README.md` explains what each figure measures and summarizes what the current input data show. If a field is unavailable, that figure is skipped rather than populated with invented values.
