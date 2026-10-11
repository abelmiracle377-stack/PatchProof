# PatchProof — starter benchmark

PatchProof is a small, reproducible benchmark for evaluating AI-generated software patches.
This starter includes one deliberately flawed Python task so you can validate the evaluation loop before adding more tasks.

## Requirements
- Python 3.10+
- pytest

## Quick start
```bash
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
pytest -q
```

The initial task is expected to fail some tests because `src/price_check.py` contains a bug.
That is intentional: the benchmark runner should detect the defect, and an evaluated model should propose a patch.

## First milestone
1. Run `pytest -q` and confirm the starter task fails.
2. Inspect `tasks/price_check/task.md`.
3. Fix the bug in `src/price_check.py`.
4. Run `pytest -q` again and confirm all tests pass.
5. Add a second task only after this loop is reliable.

## Benchmark integrity
- Keep evaluator-only tests out of prompts given to evaluated models.
- Use a clean copy of the task repository for each model/attempt.
- Record model name/version, task ID, prompt, patch, test command, exit code, and test summary.
- Never include confidential employer/client code or data.
- This starter is a prototype, not evidence of model performance by itself.
