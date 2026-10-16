
"""Run controlled candidate experiments against PatchProof tasks."""

import json
import tempfile
from pathlib import Path

from patchproof.runner import evaluate


ROOT = Path(__file__).resolve().parent

CANDIDATES = {
    "reference": """
def final_price(price: float, discount_percent: float) -> float:
    if price < 0:
        raise ValueError("price must be non-negative")
    if not 0 <= discount_percent <= 100:
        raise ValueError("discount must be between 0 and 100")
    return round(price * (1 - discount_percent / 100), 2)

def filter_prices(prices, max_price):
    return [price for price in prices if price <= max_price]
""",
    "missing_discount_validation": """
def final_price(price: float, discount_percent: float) -> float:
    if price < 0:
        raise ValueError("price must be non-negative")
    return round(price * (1 - discount_percent / 100), 2)

def filter_prices(prices, max_price):
    return [price for price in prices if price <= max_price]
""",
    "missing_price_validation": """
def final_price(price: float, discount_percent: float) -> float:
    if not 0 <= discount_percent <= 100:
        raise ValueError("discount must be between 0 and 100")
    return round(price * (1 - discount_percent / 100), 2)

def filter_prices(prices, max_price):
    return [price for price in prices if price <= max_price]
""",
    "wrong_rounding_precision": """
def final_price(price: float, discount_percent: float) -> float:
    if price < 0:
        raise ValueError("price must be non-negative")
    if not 0 <= discount_percent <= 100:
        raise ValueError("discount must be between 0 and 100")
    return round(price * (1 - discount_percent / 100), 1)

def filter_prices(prices, max_price):
    return [price for price in prices if price <= max_price]
""",
    "rounds_before_discount": """
def final_price(price: float, discount_percent: float) -> float:
    if price < 0:
        raise ValueError("price must be non-negative")
    if not 0 <= discount_percent <= 100:
        raise ValueError("discount must be between 0 and 100")
    rounded_price = round(price, 2)
    return round(rounded_price * (1 - discount_percent / 100), 2)

def filter_prices(prices, max_price):
    return [price for price in prices if price <= max_price]
""",
}

TASK_IDS = ("PP-001", "PP-002", "PP-003")


def main():
    rows = []

    with tempfile.TemporaryDirectory(prefix="patchproof_experiment_") as temp:
        temp_path = Path(temp)

        for candidate_name, source in CANDIDATES.items():
            candidate_path = temp_path / f"{candidate_name}.py"
            candidate_path.write_text(
                source.strip() + "\n",
                encoding="utf-8",
            )

            for task_id in TASK_IDS:
                result = evaluate(candidate_path, task_id)
                rows.append({
                    "candidate": candidate_name,
                    "task_id": task_id,
                    "passed": result["passed"],
                    "failed": result["failed"],
                    "errors": result["errors"],
                    "status": result["status"],
                    "success": result["success"],
                })

    output_path = ROOT / "results" / "benchmark_experiment.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(rows, indent=2),
        encoding="utf-8",
    )

    print("Controlled benchmark experiment")
    print("-" * 78)

    for row in rows:
        print(
            f"{row['candidate']:28} "
            f"{row['task_id']:6} "
            f"passed={row['passed']:2} "
            f"failed={row['failed']:2} "
            f"status={row['status']}"
        )

    print(f"\nCandidates tested: {len(CANDIDATES)}")
    print(f"Tasks tested: {len(TASK_IDS)}")
    print(f"Evaluations completed: {len(rows)}")
    print(f"Experiment report: {output_path}")


if __name__ == "__main__":
    main()
