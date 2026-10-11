# Evaluation protocol (initial draft)

## Per attempt
1. Create a fresh copy of the task repository.
2. Give the model only the task statement and allowed repository files.
3. Save the generated diff and execution log.
4. Apply the patch to the clean copy.
5. Run public tests and evaluator-only tests separately.
6. Record exit code, pass counts, regressions, and any test manipulation.
7. Inspect failures before labelling them as model failures.

## Minimum result fields
- benchmark_version
- task_id
- model_name_and_version
- attempt_number
- prompt_hash
- patch_hash
- public_test_result
- evaluator_test_result
- regression_test_result
- exit_code
- notes

## Scoring principles
- Functional correctness is primary.
- Do not treat a fluent explanation as evidence of correctness.
- Keep task ambiguity, harness failures, and model failures separate.
- Report per-task results as well as aggregate scores.
- Do not publish a model ranking from one toy task.
