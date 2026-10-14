
"""Summarize and compare PatchProof benchmark evaluation results."""

from collections import defaultdict
from dataclasses import asdict, dataclass
from typing import Iterable
import json


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

        for field_name in ("passed", "total", "exit_code"):
            value = getattr(self, field_name)
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(f"{field_name} must be an integer.")

        if self.total < 0:
            raise ValueError("total cannot be negative.")

        if self.passed < 0 or self.passed > self.total:
            raise ValueError("passed must be between 0 and total.")

        if not isinstance(self.notes, str):
            raise ValueError("notes must be a string.")

    @property
    def pass_rate(self) -> float:
        """Return the fraction of tests passed, from 0.0 to 1.0."""
        return self.passed / self.total if self.total else 0.0


def _aggregate(results: list[TestResult]) -> dict:
    """Calculate a test-weighted aggregate for a group of results."""
    passed = sum(result.passed for result in results)
    total = sum(result.total for result in results)

    return {
        "attempts": len(results),
        "passed": passed,
        "total": total,
        "pass_rate": passed / total if total else 0.0,
    }


def summarize(results: Iterable[TestResult]) -> dict:
    """Summarize results overall, by model, and by task.

    The overall pass rate is weighted by the number of tests,
    rather than averaging each attempt's pass rate equally.
    """
    rows = list(results)

    if any(not isinstance(row, TestResult) for row in rows):
        raise TypeError("Every result must be a TestResult instance.")

    by_model = defaultdict(list)
    by_task = defaultdict(list)

    for result in rows:
        by_model[result.model].append(result)
        by_task[result.task_id].append(result)

    total_passed = sum(row.passed for row in rows)
    total_tests = sum(row.total for row in rows)

    return {
        "attempts": len(rows),
        "passed": total_passed,
        "total": total_tests,
        "overall_pass_rate": (
            total_passed / total_tests if total_tests else 0.0
        ),
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


if __name__ == "__main__":
    sample = [
        TestResult("PP-001", "model-a", 6, 8, 1, "Three contract checks failed."),
        TestResult("PP-001", "model-b", 8, 8, 0, "All checks passed."),
        TestResult("PP-002", "model-a", 11, 12, 1, "One rounding check failed."),
        TestResult("PP-002", "model-b", 12, 12, 0, "All checks passed."),
    ]

    print(json.dumps(summarize(sample), indent=2))
