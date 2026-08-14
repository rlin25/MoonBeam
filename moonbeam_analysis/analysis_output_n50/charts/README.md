# MoonBeam charts — what each figure is telling you

The figures are generated automatically from `lineage_scoring.csv`. **Primary** figures are the clearest paper-facing summaries; **secondary** figures explain behavior and timing; the **robustness** figure checks seeding order without making an order-effect significance claim.

## Recommended paper order

1. `01_arbitration_rate_with_ci.png` — current confirmatory DV by condition.
2. `02_effect_size_forest.png` — lead with the effect size and uncertainty for A − B.
3. `03_strategy_composition.png` — shows the full taxonomy behind arbitration vs. non_arbitration.
4. Put the remaining figures in secondary/supplementary results unless they become substantively important.

## 01_arbitration_rate_with_ci.png

**Role:** PRIMARY

**Status:** generated

**What it tells you:** This is the current primary dependent-variable figure. Each point is the percentage of lineages classified as arbitration, and each whisker is a 95% Wilson interval. Higher values mean the model more often resolved the contradiction by preserving one claim and eliminating the competing one. Current data: A: 43/50 (86.0%); B: 11/50 (22.0%); C: 48/50 (96.0%).

## 02_effect_size_forest.png

**Role:** PRIMARY

**Status:** generated

**What it tells you:** This is the visual companion to the confirmatory Fisher test. The dot is the difference in arbitration rate and the line is its 95% confidence interval; 0 means no difference. The confirmatory direction is A − B. Current A − B estimate: +64.0 percentage points, 95% CI [46.0, 75.6] percentage points; Fisher p=1.06e-10. The C comparisons are exploratory only.

## 03_strategy_composition.png

**Role:** PRIMARY

**Status:** generated

**What it tells you:** Each bar represents 100% of a condition, split by the lineage's overall behavioral strategy. This is better than raw grouped bars for comparing composition across equally sized conditions. It shows the full behavioral composition underlying the binary arbitration/non-arbitration DV. Current dominant strategies: A: arbitration 43/50 (86.0%); B: clear-without-replacement 39/50 (78.0%); C: arbitration 48/50 (96.0%). This taxonomy view is descriptive; the current preregistered headline test collapses it to arbitration versus non_arbitration.

## 04_cumulative_first_action.png

**Role:** SECONDARY

**Status:** generated

**What it tells you:** This curve shows how quickly lineages first wrote, edited, or deleted memory. A curve that rises earlier indicates faster intervention; a curve that ends below 100% means some lineages never acted. Current data: A: 84.0% by step 1, 98.0% by step 7; B: 96.0% by step 1, 100.0% by step 7; C: 70.0% by step 1, 100.0% by step 7. This is a timing/descriptive figure, not the confirmatory A-vs-B test.

## 05_recall_distribution.png

**Role:** SECONDARY

**Status:** generated

**What it tells you:** Each dot is one lineage's number of explicit recall calls; the box summarizes the middle of the distribution. This shows search effort rather than whether the model ultimately changed memory. Higher values mean the model searched memory more often. Current data: A: median 2.0, mean 2.54; B: median 3.0, mean 2.92; C: median 4.5, mean 4.32.

## 06_counterbalance_arbitration_robustness.png

**Role:** ROBUSTNESS

**Status:** generated

**What it tells you:** This robustness figure checks whether arbitration rates differ depending on which contradictory seed was inserted first. It is not powered as an order-effect test, so arm differences are observations rather than confirmatory findings. Current split: A: A-first 23/25 (92.0%), B-first 20/25 (80.0%); B: A-first 7/25 (28.0%), B-first 4/25 (16.0%); C: A-first 25/25 (100.0%), B-first 23/25 (92.0%).

## 07_seed_final_states.png

**Role:** SECONDARY

**Status:** generated

**What it tells you:** These stacked bars show what happened to the first and second seeded memories by the end of each lineage: unchanged, edited, or deleted. Comparing the two bars within a condition can reveal positional asymmetry that may relate to seeding order. Treat this as a descriptive diagnostic; the counterbalance analysis is the cleaner robustness check for order.

## 08_arbitration_direction.png

**Role:** SECONDARY

**Status:** generated

**What it tells you:** Among arbitration cases only, this figure shows whether the first or second seeded entry survived. It helps diagnose directional/position preference, but it is conditional on already being in the arbitration category and therefore answers a different question from the overall arbitration rate. Current arbitration cases: A: kept first 32/43, kept second 11/43; B: kept first 7/11, kept second 4/11; C: kept first 35/48, kept second 13/48.

## Interpretation guardrails

- The current confirmatory test is A vs. B on `arbitration/non_arbitration`; do not promote the C comparisons or taxonomy figures into additional confirmatory significance claims.
- Counterbalance is a robustness check. If the arms differ, report it as an observation for future work rather than as a powered order-effect finding.
- `took_action/no_action` is retained only as a retired descriptive diagnostic; it must not be reported as the confirmatory DV.
- Arbitration and action remain distinct: a lineage can edit/delete a seeded entry and therefore `take_action` without ending in the arbitration strategy.
