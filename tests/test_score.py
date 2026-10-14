
import pytest

from patchproof.score import TestResult as ScoreResult, summarize


def test_pass_rate():
    result = ScoreResult("PP-001", "model-a", 6, 8, 1)
    assert result.pass_rate == 0.75


def test_zero_test_pass_rate():
    result = ScoreResult("PP-001", "model-a", 0, 0, 0)
    assert result.pass_rate == 0.0


def test_rejects_invalid_passed_count():
    with pytest.raises(ValueError):
        ScoreResult("PP-001", "model-a", 9, 8, 1)


def test_rejects_negative_total():
    with pytest.raises(ValueError):
        ScoreResult("PP-001", "model-a", 0, -1, 1)


def test_rejects_empty_model():
    with pytest.raises(ValueError):
        ScoreResult("PP-001", "", 0, 8, 1)


def test_summarize_weights_by_test_count():
    results = [
        ScoreResult("PP-001", "model-a", 1, 2, 1),
        ScoreResult("PP-002", "model-a", 8, 8, 0),
    ]

    report = summarize(results)

    assert report["attempts"] == 2
    assert report["passed"] == 9
    assert report["total"] == 10
    assert report["overall_pass_rate"] == 0.9


def test_summarize_groups_by_model_and_task():
    results = [
        ScoreResult("PP-001", "model-a", 6, 8, 1),
        ScoreResult("PP-001", "model-b", 8, 8, 0),
        ScoreResult("PP-002", "model-a", 12, 12, 0),
    ]

    report = summarize(results)

    assert report["by_model"]["model-a"]["passed"] == 18
    assert report["by_model"]["model-a"]["total"] == 20
    assert report["by_model"]["model-b"]["pass_rate"] == 1.0
    assert report["by_task"]["PP-001"]["passed"] == 14
    assert report["by_task"]["PP-001"]["total"] == 16


def test_summarize_empty_results():
    report = summarize([])

    assert report["attempts"] == 0
    assert report["overall_pass_rate"] == 0.0
    assert report["results"] == []


def test_summarize_rejects_non_test_result():
    with pytest.raises(TypeError):
        summarize([{"task_id": "PP-001"}])
