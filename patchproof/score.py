
"""Summarize and export PatchProof benchmark evaluation results."""

import argparse
from collections import defaultdict
from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Iterable

try:
    from .registry import TASKS
except ImportError:
    from registry import TASKS


@dataclass
class TestResult:
    """Results from evaluating one candidate on one benchmark task."""

    task_id: str
    model: str
    passed: int
    total: int
    exit_code: int
    notes: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.task_id, str) or not self.task_id.strip():
            raise ValueError("task_id must be a non-empty string.")
        if not isinstance(self.model, str) or not self.model.strip():
            raise ValueError("model must be a non-empty string.")

        for name in ("passed", "total", "exit_code"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(f"{name} must be an integer.")

        if self.total < 0:
            raise ValueError("total cannot be negative.")
        if not 0 <= self.passed <= self.total:
            raise ValueError("passed must be between 0 and total.")
        if not isinstance(self.notes, str):
            raise ValueError("notes must be a string.")

    @property
    def pass_rate(self) -> float:
        return self.passed / self.total if self.total else 0.0


def _aggregate(results: list[TestResult]) -> dict:
    passed = sum(result.passed for result in results)
    total = sum(result.total for result in results)
    return {
        "attempts": len(results),
        "passed": passed,
        "total": total,
        "pass_rate": passed / total if total else 0.0,
    }


def summarize(results: Iterable[TestResult]) -> dict:
    rows = list(results)
    if any(not isinstance(row, TestResult) for row in rows):
        raise TypeError("Every result must be a TestResult instance.")

    by_model = defaultdict(list)
    by_task = defaultdict(list)

    for result in rows:
        by_model[result.model].append(result)
        by_task[result.task_id].append(result)

    passed = sum(row.passed for row in rows)
    total = sum(row.total for row in rows)

    return {
        "attempts": len(rows),
        "passed": passed,
        "total": total,
        "overall_pass_rate": passed / total if total else 0.0,
        "by_model": {
            name: _aggregate(group)
            for name, group in sorted(by_model.items())
        },
        "by_task": {
            name: _aggregate(group)
            for name, group in sorted(by_task.items())
        },
        "results": [
            asdict(row) | {"pass_rate": row.pass_rate}
            for row in rows
        ],
    }


def load_evaluation_reports(
    input_paths: Iterable[Path],
    model_override: str | None = None,
) -> list[TestResult]:
    """Load individual JSON evaluation reports from the runner."""
    results = []

    for input_path in input_paths:
        path = Path(input_path)

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            raise ValueError(f"Could not read {path}: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in {path}: {exc}") from exc

        if not isinstance(data, dict):
            raise ValueError(f"Expected a JSON object in {path}.")

        task_id = data.get("task_id")
        if not isinstance(task_id, str) or task_id not in TASKS:
            raise ValueError(
                f"Unknown or missing task_id in {path}: {task_id!r}"
            )

        passed = data.get("passed")
        if isinstance(passed, bool) or not isinstance(passed, int):
            raise ValueError(f"Missing or invalid passed count in {path}.")

        total = TASKS[task_id]["test_count"]
        candidate = data.get("candidate")
        inferred_model = (
            Path(candidate).stem
            if isinstance(candidate, str) and candidate
            else path.stem
        )
        model = model_override or data.get("model") or inferred_model

        exit_code = data.get("exit_code")
        if exit_code is None:
            exit_code = -1
        if isinstance(exit_code, bool) or not isinstance(exit_code, int):
            raise ValueError(f"Invalid exit_code in {path}.")

        status = data.get("status", "unknown")

        results.append(
            TestResult(
                task_id=task_id,
                model=model,
                passed=passed,
                total=total,
                exit_code=exit_code,
                notes=str(status),
            )
        )

    if not results:
        raise ValueError("At least one input report is required.")

    return results


def write_summary(summary: dict, output_path: Path) -> Path:
    """Write a benchmark summary to a JSON file."""
    output_path = Path(output_path)

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(summary, indent=2) + "\n",
            encoding="utf-8",
        )
    except OSError as exc:
        raise ValueError(
            f"Could not write summary to {output_path}: {exc}"
        ) from exc

    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a PatchProof benchmark summary from JSON reports."
    )
    parser.add_argument(
        "--input",
        nargs="+",
        type=Path,
        help="One or more JSON reports produced by PatchProof.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/benchmark_summary.json"),
        help="Summary output path.",
    )
    parser.add_argument(
        "--model",
        help="Optional model name to apply to every imported report.",
    )
    args = parser.parse_args()

    if not args.input:
        parser.error("--input is required to generate a summary.")

    try:
        results = load_evaluation_reports(args.input, args.model)
        summary = summarize(results)
        output_path = write_summary(summary, args.output)
    except (ValueError, TypeError) as exc:
        parser.error(str(exc))

    print(f"Attempts: {summary['attempts']}")
    print(f"Passed: {summary['passed']} / {summary['total']}")
    print(f"Overall pass rate: {summary['overall_pass_rate']:.1%}")
    print(f"Summary report: {output_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
