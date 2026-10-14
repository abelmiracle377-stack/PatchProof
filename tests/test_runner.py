
from pathlib import Path

import pytest

from patchproof.history import load_history
from patchproof.runner import evaluate, main


def test_buggy_candidate_is_rejected():
    candidate = (
        Path(__file__).resolve().parents[1]
        / "tasks"
        / "price_check"
        / "buggy_solution.py"
    )

    result = evaluate(candidate)

    assert result["passed"] == 5
    assert result["failed"] == 3
    assert result["success"] is False
    assert result["status"] == "failed"


def test_reference_candidate_is_accepted():
    candidate = (
        Path(__file__).resolve().parents[1]
        / "tasks"
        / "price_check"
        / "reference_solution.py"
    )

    result = evaluate(candidate)

    assert result["passed"] == 8
    assert result["failed"] == 0
    assert result["success"] is True
    assert result["status"] == "passed"


def test_missing_candidate_raises_error(tmp_path):
    candidate = tmp_path / "does_not_exist.py"

    with pytest.raises(FileNotFoundError):
        evaluate(candidate)


def test_cli_records_evaluation_history(tmp_path, monkeypatch):
    project_root = Path(__file__).resolve().parents[1]
    candidate = project_root / "src" / "price_check.py"
    output_path = tmp_path / "latest.json"
    history_path = tmp_path / "history.jsonl"

    monkeypatch.setattr(
        "sys.argv",
        [
            "patchproof-runner",
            "--candidate",
            str(candidate),
            "--task",
            "PP-002",
            "--output",
            str(output_path),
            "--history",
            str(history_path),
        ],
    )

    assert main() == 0

    records = load_history(history_path)

    assert len(records) == 1
    assert records[0]["task_id"] == "PP-002"
    assert records[0]["passed"] == 12
    assert records[0]["failed"] == 0
    assert records[0]["success"] is True
    assert output_path.is_file()


def test_cli_appends_history_on_repeated_evaluations(
    tmp_path, monkeypatch
):
    project_root = Path(__file__).resolve().parents[1]
    candidate = project_root / "src" / "price_check.py"
    output_path = tmp_path / "latest.json"
    history_path = tmp_path / "history.jsonl"

    arguments = [
        "patchproof-runner",
        "--candidate",
        str(candidate),
        "--task",
        "PP-001",
        "--output",
        str(output_path),
        "--history",
        str(history_path),
    ]

    monkeypatch.setattr("sys.argv", arguments)
    assert main() == 0

    monkeypatch.setattr("sys.argv", arguments)
    assert main() == 0

    records = load_history(history_path)

    assert len(records) == 2
    assert all(record["task_id"] == "PP-001" for record in records)
    assert all(record["passed"] == 8 for record in records)
