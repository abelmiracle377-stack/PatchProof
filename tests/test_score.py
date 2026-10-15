
import json

import pytest

from patchproof.score import (
    TestResult as ScoreResult,
    load_evaluation_reports,
    summarize,
    write_summary,
)


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


def test_load_evaluation_report(tmp_path):
    report_path = tmp_path / "latest.json"
    report_path.write_text(
        json.dumps(
            {
                "task_id": "PP-001",
                "candidate": "candidate.py",
                "passed": 8,
                "failed": 0,
                "errors": 0,
                "exit_code": 0,
                "status": "passed",
            }
        ),
        encoding="utf-8",
    )

    results = load_evaluation_reports([report_path])

    assert len(results) == 1
    assert results[0].task_id == "PP-001"
    assert results[0].model == "candidate"
    assert results[0].passed == 8
    assert results[0].total == 9
    assert results[0].notes == "passed"


def test_load_report_with_model_override(tmp_path):
    report_path = tmp_path / "latest.json"
    report_path.write_text(
        json.dumps(
            {
                "task_id": "PP-002",
                "passed": 11,
                "exit_code": 1,
                "status": "failed",
            }
        ),
        encoding="utf-8",
    )

    results = load_evaluation_reports([report_path], "my-model")

    assert results[0].model == "my-model"
    assert results[0].total == 12


def test_load_report_rejects_unknown_task(tmp_path):
    report_path = tmp_path / "bad.json"
    report_path.write_text(
        json.dumps({"task_id": "PP-999", "passed": 0}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Unknown or missing task_id"):
        load_evaluation_reports([report_path])


def test_load_report_rejects_invalid_json(tmp_path):
    report_path = tmp_path / "bad.json"
    report_path.write_text("{not valid JSON", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid JSON"):
        load_evaluation_reports([report_path])


def test_write_summary_creates_directory(tmp_path):
    output_path = tmp_path / "reports" / "summary.json"
    summary = {"attempts": 0, "results": []}

    saved_path = write_summary(summary, output_path)

    assert saved_path == output_path
    assert json.loads(output_path.read_text(encoding="utf-8")) == summary
