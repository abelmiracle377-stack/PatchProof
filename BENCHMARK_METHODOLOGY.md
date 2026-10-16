# PatchProof Benchmark Methodology

## 1. Objective

PatchProof is a prototype benchmark for evaluating AI-generated software patches against explicit contract tests. This experiment checks whether the current harness distinguishes a correct implementation from implementations containing deliberately introduced defects.

## 2. Benchmark tasks

- **PP-001 — Validate percentage discounts:** checks non-negative prices, valid discount percentages, expected calculations, and a calculation-order edge case.
- **PP-002 — Rounding contract:** checks calculation results, two-decimal rounding behavior, and invalid input handling.

PP-001 contains 9 tests. PP-002 contains 12 tests.

## 3. Controlled candidates

Five implementations were evaluated:

1. `reference`: correct implementation used as a positive control.
2. `missing_discount_validation`: does not reject invalid discount percentages.
3. `missing_price_validation`: does not reject negative prices.
4. `wrong_rounding_precision`: rounds results to one decimal place.
5. `rounds_before_discount`: rounds the original price before applying the discount.

## 4. Procedure

Each candidate was evaluated against PP-001 and PP-002 using the PatchProof runner. This produced 10 candidate-task evaluations per experiment run.

The experiment records the task ID, candidate name, passed and failed test counts, errors, status, and success flag in `results/benchmark_experiment.json`.

The experiment was run twice. The displayed candidate/task outcomes and pass/fail counts were identical across both runs.

## 5. Observed results

- The reference implementation passed both tasks.
- All four deliberately faulty candidates failed both tasks.
- PP-002 detected more failures for the wrong-rounding-precision candidate than PP-001.
- The calculation-order defect was detected by both tasks after a discriminating test was added to PP-001.
- Missing price validation was detected by both tasks.

## 6. Limitations

- The experiment uses five hand-written candidates, not a representative sample of AI-generated patches.
- The candidates were designed around defects already addressed by the benchmark contracts.
- The two tasks overlap in functionality and should not be treated as independent measures of general software engineering ability.
- Identical outcomes on the same machine do not establish cross-platform reproducibility.
- These results demonstrate initial defect-detection behavior, not comparative performance of frontier models.

## 7. Next evaluation work

Future work should include independently designed defects, carefully specified task contracts, fresh candidate patches, and evaluations across multiple AI models and repeated attempts. Model comparisons should use consistent prompts, task versions, environments, and scoring rules.

## 8. Current conclusion

The controlled experiment provides initial evidence that PatchProof can reject the four tested defect patterns while accepting the reference implementation. Broader validation is needed before drawing conclusions about AI-model performance.
