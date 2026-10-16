
from pathlib import Path

import pytest

from patchproof.runner import evaluate


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "tasks" / "price_filter" / "reference_solution.py"
BUGGY = ROOT / "tasks" / "price_filter" / "buggy_solution.py"


def test_reference_price_filter_passes_all_contract_tests():
    result = evaluate(REFERENCE, "PP-003")

    assert result["passed"] == 8
    assert result["failed"] == 0
    assert result["success"] is True
    assert result["status"] == "passed"


def test_buggy_price_filter_is_rejected():
    result = evaluate(BUGGY, "PP-003")

    assert result["passed"] == 3
    assert result["failed"] == 5
    assert result["success"] is False
    assert result["status"] == "failed"
