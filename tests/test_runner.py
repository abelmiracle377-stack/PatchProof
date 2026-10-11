
import pytest

from patchproof.runner import evaluate


def test_buggy_candidate_is_rejected():
    from pathlib import Path

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
    from pathlib import Path

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
