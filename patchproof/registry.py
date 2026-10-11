"""Central registry of PatchProof benchmark tasks."""

TASKS = {
    "PP-001": {
        "description": "Validate percentage discounts",
        "test_count": 8,
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
}
