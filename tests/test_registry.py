
import pytest

from patchproof.registry import TASKS, list_tasks, validate_registry
from patchproof.runner import main


def test_list_tasks_returns_sorted_metadata():
    tasks = list_tasks()

    assert [task["task_id"] for task in tasks] == ["PP-001", "PP-002"]
    assert tasks[0]["description"] == "Validate percentage discounts"
    assert tasks[0]["test_count"] == 9
    assert tasks[1]["test_count"] == 12


def test_validate_registry_rejects_empty_registry():
    with pytest.raises(ValueError, match="non-empty"):
        validate_registry({})


def test_validate_registry_rejects_missing_test_source():
    malformed = {
        "PP-999": {
            "description": "Example task",
            "test_count": 1,
        }
    }

    with pytest.raises(ValueError, match="test_source"):
        validate_registry(malformed)


def test_validate_registry_rejects_invalid_test_count():
    malformed = {
        "PP-999": {
            "description": "Example task",
            "test_count": 0,
            "test_source": "def test_example(): pass",
        }
    }

    with pytest.raises(ValueError, match="test_count"):
        validate_registry(malformed)


def test_list_tasks_cli(capsys, monkeypatch):
    monkeypatch.setattr("sys.argv", ["patchproof-runner", "--list-tasks"])

    assert main() == 0
    output = capsys.readouterr().out
    assert "PP-001" in output
    assert "PP-002" in output
    assert "9 tests" in output
    assert "12 tests" in output


def test_registry_has_expected_tasks():
    validate_registry(TASKS)
