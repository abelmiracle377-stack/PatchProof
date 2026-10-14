
import json

import pytest

from patchproof.history import (
    append_result,
    detect_regression,
    load_history,
)


def make_result(passed, task_id="PP-001", candidate="candidate.py"):
    return {
        "task_id": task_id,
        "candidate": candidate,
        "passed": passed,
        "failed": 8 - passed,
        "status": "passed" if passed == 8 else "failed",
    }


def test_append_and_load_history(tmp_path):
    history_path = tmp_path / "results" / "history.jsonl"
    first = make_result(5)
    second = make_result(7)

    append_result(first, history_path)
    append_result(second, history_path)

    records = load_history(history_path)

    assert records == [first, second]


def test_missing_history_returns_empty_list(tmp_path):
    assert load_history(tmp_path / "missing.jsonl") == []


def test_append_rejects_non_dictionary(tmp_path):
    with pytest.raises(TypeError):
        append_result("not a dictionary", tmp_path / "history.jsonl")


def test_append_requires_task_id(tmp_path):
    with pytest.raises(ValueError, match="task_id"):
        append_result({"passed": 2}, tmp_path / "history.jsonl")


def test_load_rejects_invalid_json(tmp_path):
    history_path = tmp_path / "history.jsonl"
    history_path.write_text("{invalid json}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid JSON"):
        load_history(history_path)


def test_detects_regression(tmp_path):
    current = make_result(4)
    history = [make_result(7)]

    report = detect_regression(current, history)

    assert report["comparison"] == "regression"
    assert report["regression"] is True
    assert report["previous_passed"] == 7
    assert report["current_passed"] == 4
    assert report["change"] == -3


def test_detects_improvement():
    current = make_result(8)
    history = [make_result(5)]

    report = detect_regression(current, history)

    assert report["comparison"] == "improvement"
    assert report["regression"] is False
    assert report["change"] == 3


def test_detects_unchanged_result():
    current = make_result(5)
    history = [make_result(5)]

    report = detect_regression(current, history)

    assert report["comparison"] == "unchanged"
    assert report["regression"] is False
    assert report["change"] == 0


def test_first_result_has_no_baseline():
    report = detect_regression(make_result(5), [])

    assert report["comparison"] == "no_baseline"
    assert report["regression"] is False
    assert report["change"] is None


def test_ignores_different_candidates():
    current = make_result(4, candidate="candidate_b.py")
    history = [make_result(7, candidate="candidate_a.py")]

    report = detect_regression(current, history)

    assert report["comparison"] == "no_baseline"


def test_uses_latest_matching_history_record():
    current = make_result(6)
    history = [
        make_result(3),
        make_result(7),
    ]

    report = detect_regression(current, history)

    assert report["previous_passed"] == 7
    assert report["change"] == -1


def test_history_is_valid_json_lines(tmp_path):
    history_path = tmp_path / "history.jsonl"
    result = make_result(5)

    append_result(result, history_path)

    lines = history_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0]) == result
