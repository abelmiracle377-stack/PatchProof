
"""Central registry of PatchProof benchmark tasks."""

TASKS = {
    "PP-001": {
        "description": "Validate percentage discounts",
        "test_count": 9,
        "test_source": r'''
import pytest
from candidate import final_price

@pytest.mark.parametrize(
    ("price", "discount", "expected"),
    [
        (100, 10, 90.0),
        (19.99, 0, 19.99),
        (10, 100, 0.0),
        (12.50, 20, 10.0),
    ],
)
def test_valid_inputs(price, discount, expected):
    assert final_price(price, discount) == expected

@pytest.mark.parametrize(
    ("price", "discount"),
    [
        (-0.01, 10),
        (100, -1),
        (100, 100.01),
        (100, 150),
    ],
)
def test_invalid_inputs_raise_value_error(price, discount):
    with pytest.raises(ValueError):
        final_price(price, discount)

def test_discount_is_applied_before_rounding():
    assert final_price(1.234, 20) == 0.99
''',
    },
    "PP-002": {
        "description": "Rounding contract",
        "test_count": 12,
        "test_source": r'''
import pytest
from candidate import final_price

@pytest.mark.parametrize(
    ("price", "discount", "expected"),
    [
        (100, 10, 90.0),
        (19.99, 0, 19.99),
        (10, 100, 0.0),
        (12.50, 20, 10.0),
        (1.234, 0, 1.23),
        (1.236, 0, 1.24),
        (2.675, 0, 2.67),
        (2.685, 0, 2.69),
        (1.234, 20, 0.99),
    ],
)
def test_final_price_rounding(price, discount, expected):
    assert final_price(price, discount) == expected

@pytest.mark.parametrize(
    ("price", "discount"),
    [
        (-0.01, 10),
        (100, -1),
        (100, 100.01),
    ],
)
def test_invalid_inputs(price, discount):
    with pytest.raises(ValueError):
        final_price(price, discount)
''',
    },
    "PP-003": {
        "description": "Filter prices by maximum",
        "function": "filter_prices",
        "test_count": 8,
        "test_source": r'''
import pytest
from candidate import filter_prices

def test_keeps_prices_at_or_below_limit():
    assert filter_prices([5, 10, 15, 20], 10) == [5, 10]

def test_preserves_original_order():
    assert filter_prices([9, 3, 8, 1], 8) == [3, 8, 1]

def test_keeps_duplicate_prices():
    assert filter_prices([5, 5, 7, 5], 5) == [5, 5, 5]

def test_empty_input():
    assert filter_prices([], 10) == []

def test_no_matches():
    assert filter_prices([11, 12, 13], 10) == []

def test_all_matches():
    assert filter_prices([1, 2, 3], 3) == [1, 2, 3]

def test_zero_limit():
    assert filter_prices([0, 1, 0], 0) == [0, 0]

def test_does_not_mutate_input():
    prices = [7, 2, 9]
    original = prices.copy()
    filter_prices(prices, 7)
    assert prices == original
''',
    },
}


def validate_registry(tasks: dict | None = None) -> None:
    """Validate task metadata before it is used by the runner."""
    entries = TASKS if tasks is None else tasks

    if not isinstance(entries, dict) or not entries:
        raise ValueError("Task registry must be a non-empty dictionary.")

    for task_id, task in entries.items():
        if not isinstance(task_id, str) or not task_id.strip():
            raise ValueError("Every task must have a non-empty string ID.")

        if not isinstance(task, dict):
            raise ValueError(f"Task {task_id!r} must be a dictionary.")

        description = task.get("description")
        if not isinstance(description, str) or not description.strip():
            raise ValueError(
                f"Task {task_id!r} requires a non-empty description."
            )

        test_count = task.get("test_count")
        if (
            isinstance(test_count, bool)
            or not isinstance(test_count, int)
            or test_count < 1
        ):
            raise ValueError(
                f"Task {task_id!r} requires a positive integer test_count."
            )

        test_source = task.get("test_source")
        if not isinstance(test_source, str) or not test_source.strip():
            raise ValueError(
                f"Task {task_id!r} requires non-empty test_source."
            )

        function_name = task.get("function", "final_price")
        if not isinstance(function_name, str) or not function_name.isidentifier():
            raise ValueError(
                f"Task {task_id!r} requires a valid function name."
            )


def list_tasks(tasks: dict | None = None) -> list[dict]:
    """Return validated task metadata in stable task-ID order."""
    entries = TASKS if tasks is None else tasks
    validate_registry(entries)

    return [
        {
            "task_id": task_id,
            "description": entries[task_id]["description"],
            "test_count": entries[task_id]["test_count"],
        }
        for task_id in sorted(entries)
    ]


validate_registry()
