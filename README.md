# PatchProof — AI Software Patch Evaluation

PatchProof is a Python prototype for evaluating software patches against explicit task contracts and executable tests. It records evaluation results and runs controlled experiments to check whether reference implementations pass and selected injected defects are detected.

## Current capabilities

- Three registered benchmark tasks: PP-001, PP-002, and PP-003.
- Executable contract tests for each task.
- Evaluation of candidate implementations against benchmark tests.
- Controlled experiments with reference and deliberately faulty candidates.
- JSON output containing benchmark outcomes.
- Recorded AI patch evaluations and a summary report.
- Automated tests for the project.

## Benchmark tasks

| Task | Description | Tests |
|---|---|---:|
| PP-001 | Validate percentage discounts | 9 |
| PP-002 | Rounding contract | 12 |
| PP-003 | Filter prices by maximum | 8 |

PP-001 and PP-002 overlap in functionality. They should not be treated as independent measures of general software engineering ability.

## Requirements

- Python 3.10+
- pytest
- The project dependencies declared in `pyproject.toml`

## Setup

From the project root, create and activate a virtual environment.

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

If the virtual environment already exists and is activated, you can skip its creation and activation.

## Run the automated tests

```powershell
pytest -q
```

The current verified result was **47 passed**. Run the command again to verify the result in your own environment.

## Run the controlled benchmark experiment

```powershell
python .\run_benchmark_experiment.py
```

The experiment evaluates six configured candidates against all three tasks, producing 18 candidate-task evaluations.

The JSON report is written to:

`results/benchmark_experiment.json`

The controlled candidates include a reference implementation and five deliberately faulty implementations. The current experiment showed that the reference candidate passed all three tasks and that each injected defect was detected on its intended task.

## Run the AI patch evaluation summary

To summarize the existing AI evaluation records:

```powershell
python .\report_ai_patch_evaluations.py
```

The summary is written to:

`results/ai_patch_summary.json`

The summary currently contains seven records: five model-labelled attempts and two excluded control records.

The model-labelled candidates have not been independently verified as model-generated. The current records therefore must not be presented as a definitive comparison of AI models.

## Methodology

See `BENCHMARK_METHODOLOGY.md` for the experiment procedure, controlled candidates, observed results, and limitations.

## Limitations

- The benchmark currently covers only three tasks.
- PP-001 and PP-002 overlap in functionality.
- The controlled defects are hand-written examples, not a representative sample of real-world bugs.
- The existing model-labelled records do not establish independently verified model performance.
- Passing the available tests does not prove that a patch is free from all defects.
- Cross-platform reproducibility has not been established by the current experiment.

## Benchmark integrity

For future AI-generated patch evaluations:

- Keep evaluator-only tests out of prompts given to evaluated models.
- Use consistent task versions, prompts, test environments, and scoring rules.
- Preserve the model and version, prompt, generated patch, test command, exit code, and result report.
- Distinguish actual model-generated patches from manually supplied or controlled candidates.
- Report per-task outcomes and sample counts.
- Never include confidential employer or client code or data.

## Current status

PatchProof is a working prototype with a passing automated test suite and a controlled benchmark experiment. Further evaluation with independently generated patches and additional tasks is required before making broader claims about AI software engineering performance.