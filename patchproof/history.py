
"""Persistent evaluation history and regression detection for PatchProof."""

import json
from pathlib import Path
from typing import Any


DEFAULT_HISTORY_PATH = Path("results/history.jsonl")


def append_result(
    result: dict[str, Any],
    history_path: Path = DEFAULT_HISTORY_PATH,
) -> Path:
    """Append one evaluation result to a JSON Lines history file."""
    if not isinstance(result, dict):
        raise TypeError("result must be a dictionary.")

    task_id = result.get("task_id")
    if not isinstance(task_id, str) or not task_id.strip():
        raise ValueError("result must contain a non-empty task_id.")

    history_path = Path(history_path)

    try:
        history_path.parent.mkdir(parents=True, exist_ok=True)
        with history_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(result) + "\n")
    except OSError as exc:
        raise ValueError(
            f"Could not append history to {history_path}: {exc}"
        ) from exc

    return history_path


def load_history(
    history_path: Path = DEFAULT_HISTORY_PATH,
) -> list[dict[str, Any]]:
    """Load evaluation records, preserving their chronological order."""
    history_path = Path(history_path)

    if not history_path.exists():
        return []

    records = []

    try:
        with history_path.open("r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                if not line.strip():
                    continue

                try:
                    record = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(
                        f"Invalid JSON in {history_path}, "
                        f"line {line_number}."
                    ) from exc

                if not isinstance(record, dict):
                    raise ValueError(
                        f"Expected a JSON object in {history_path}, "
                        f"line {line_number}."
                    )

                records.append(record)
    except OSError as exc:
        raise ValueError(
            f"Could not read history from {history_path}: {exc}"
        ) from exc

    return records


def detect_regression(
    current: dict[str, Any],
    history: list[dict[str, Any]],
) -> dict[str, Any]:
    """Compare a result with the latest earlier run of the same candidate/task.

    A regression is reported only when the current passed-test count is
    lower than the previous run. A higher count is an improvement.
    Equal counts are unchanged.
    """
    task_id = current.get("task_id")
    candidate = current.get("candidate")
    passed = current.get("passed")

    if not isinstance(task_id, str) or not task_id.strip():
        raise ValueError("current result must contain a non-empty task_id.")

    if not isinstance(candidate, str) or not candidate.strip():
        raise ValueError("current result must contain a candidate path.")

    if isinstance(passed, bool) or not isinstance(passed, int) or passed < 0:
        raise ValueError("current result must contain a non-negative passed count.")

    previous = None

    for record in reversed(history):
        if (
            record.get("task_id") == task_id
            and record.get("candidate") == candidate
        ):
            previous = record
            break

    if previous is None:
        return {
            "comparison": "no_baseline",
            "regression": False,
            "previous_passed": None,
            "current_passed": passed,
            "change": None,
        }

    previous_passed = previous.get("passed")
    if (
        isinstance(previous_passed, bool)
        or not isinstance(previous_passed, int)
        or previous_passed < 0
    ):
        raise ValueError("Previous history record has an invalid passed count.")

    change = passed - previous_passed

    if change < 0:
        comparison = "regression"
    elif change > 0:
        comparison = "improvement"
    else:
        comparison = "unchanged"

    return {
        "comparison": comparison,
        "regression": change < 0,
        "previous_passed": previous_passed,
        "current_passed": passed,
        "change": change,
    }
