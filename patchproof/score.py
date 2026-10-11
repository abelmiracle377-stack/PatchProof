from dataclasses import dataclass, asdict
from typing import Iterable
import json


@dataclass
class TestResult:
    task_id: str
    model: str
    passed: int
    total: int
    exit_code: int
    notes: str = ""

    @property
    def pass_rate(self) -> float:
        return self.passed / self.total if self.total else 0.0


def summarize(results: Iterable[TestResult]) -> dict:
    rows = list(results)
    return {
        "attempts": len(rows),
        "overall_pass_rate": (
            sum(r.passed for r in rows) / sum(r.total for r in rows)
            if sum(r.total for r in rows) else 0.0
        ),
        "results": [asdict(r) | {"pass_rate": r.pass_rate} for r in rows],
    }


if __name__ == "__main__":
    # Example: python -m patchproof.score
    sample = [TestResult("PP-001", "example-model", 6, 8, 1, "Starter example only")]
    print(json.dumps(summarize(sample), indent=2))
