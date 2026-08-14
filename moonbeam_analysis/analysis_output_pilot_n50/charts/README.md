# MoonBeam charts — what each figure is telling you

The figures are generated automatically from `lineage_scoring.csv`. **Primary** figures are the clearest paper-facing summaries; **secondary** figures explain behavior and timing; the **robustness** figure checks seeding order without making an order-effect significance claim.

## Recommended paper order

1. `01_action_rate_with_ci.png` — headline outcome by condition.
2. `02_effect_size_forest.png` — lead with the effect size and uncertainty for B − A.
3. `03_strategy_composition.png` — shows how behavioral strategies differ even when action rates are similar.
4. Put the remaining figures in secondary/supplementary results unless they become substantively important.

## 01_action_rate_with_ci.png

**Role:** PRIMARY

**Status:** generated

**What it tells you:** This is the primary outcome figure. Each point is the percentage of lineages that edited or deleted at least one seeded entry; the whisker is its 95% Wilson interval. Higher points mean the condition more often triggered intervention in seeded memory. Current data: A: 49/50 (98.0%); B: 50/50 (100.0%); C: 50/50 (100.0%). Because the rates are near the ceiling, the figure mainly shows how little room remains for the conditions to differ on this binary outcome.

## 02_effect_size_forest.png

**Role:** PRIMARY

**Status:** generated

**What it tells you:** This is the most direct visual companion to the statistical test. The dot is the observed difference in action rate and the line is its 95% confidence interval; the dashed vertical line at 0 means no difference. The confirmatory comparison is B − A; C comparisons are exploratory only. Current B − A estimate: +2.0 percentage points, 95% CI [-5.3, 10.5] percentage points. An interval crossing 0 means the data are compatible with no difference as well as effects within the interval.

## 03_strategy_composition.png

**Role:** PRIMARY

**Status:** generated

**What it tells you:** Each bar represents 100% of a condition, split by the lineage's overall behavioral strategy. This is better than raw grouped bars for comparing composition across equally sized conditions. It answers whether the model reached similar action rates through different behaviors. Current dominant strategies: A: arbitration 43/50 (86.0%); B: clear-without-replacement 39/50 (78.0%); C: arbitration 48/50 (96.0%). This taxonomy view is descriptive; the preregistered headline test still uses the collapsed took_action/no_action outcome.

## 04_cumulative_first_action.png

**Role:** SECONDARY

**Status:** generated

**What it tells you:** This curve shows how quickly lineages first wrote, edited, or deleted memory. A curve that rises earlier indicates faster intervention; a curve that ends below 100% means some lineages never acted. Current data: A: 84.0% by step 1, 98.0% by step 7; B: 96.0% by step 1, 100.0% by step 7; C: 70.0% by step 1, 100.0% by step 7. This is a timing/descriptive figure, not the confirmatory A-vs-B test.

## 05_recall_distribution.png

**Role:** SECONDARY

**Status:** generated

**What it tells you:** Each dot is one lineage's number of explicit recall calls; the box summarizes the middle of the distribution. This shows search effort rather than whether the model ultimately changed memory. Higher values mean the model searched memory more often. Current data: A: median 2.0, mean 2.54; B: median 3.0, mean 2.92; C: median 4.5, mean 4.32.

## 06_counterbalance_robustness.png

**Role:** ROBUSTNESS

**Status:** generated

**What it tells you:** This robustness figure checks whether the action rate looks materially different depending on which contradictory seed was inserted first. It is not powered as an order-effect test, so differences should be described as observations, not findings. Current split: A: A-first 25/25 (100.0%), B-first 24/25 (96.0%); B: A-first 25/25 (100.0%), B-first 25/25 (100.0%); C: A-first 25/25 (100.0%), B-first 25/25 (100.0%).

## 07_seed_final_states.png

**Role:** SECONDARY

**Status:** generated

**What it tells you:** These stacked bars show what happened to the first and second seeded memories by the end of each lineage: unchanged, edited, or deleted. Comparing the two bars within a condition can reveal positional asymmetry that may relate to seeding order. Treat this as a descriptive diagnostic; the counterbalance analysis is the cleaner robustness check for order.

## 08_arbitration_direction.png

**Role:** SECONDARY

**Status:** generated

**What it tells you:** Among arbitration cases only, this figure shows whether the first or second seeded entry survived. It helps diagnose directional/position preference, but it should not be mistaken for the overall action rate because many lineages act without arbitrating. Current arbitration cases: A: kept first 32/43, kept second 11/43; B: kept first 7/11, kept second 4/11; C: kept first 35/48, kept second 13/48.

## Interpretation guardrails

- The confirmatory test is A vs. B on `took_action/no_action`; do not promote the C comparisons or taxonomy figures into additional confirmatory significance claims.
- Counterbalance is a robustness check. If the arms differ, report it as an observation for future work rather than as a powered order-effect finding.
- Near-100% action rates create a ceiling effect: strategy composition, timing, and recall behavior can still differ substantially even when the binary outcome barely differs.
- Do not read arbitration as synonymous with action. A lineage can edit/delete a seeded entry and therefore `take_action` without ending in the arbitration strategy.
