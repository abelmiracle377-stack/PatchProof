
"""Summarize PatchProof AI patch evaluation records."""

import argparse
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DEFAULT_INPUT = ROOT / "results" / "ai_patch_evaluations.jsonl"
DEFAULT_OUTPUT = ROOT / "results" / "ai_patch_summary.json"


def load_records(path: Path) -> list[dict]:
    """Load JSON Lines records and validate their basic structure."""
    records = []

    if not path.is_file():
        raise FileNotFoundError(f"Evaluation records not found: {path}")

    with path.open("r", encoding="utf-8-sig") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON on line {line_number} of {path}"
                ) from exc

            if not isinstance(record, dict):
                raise ValueError(
                    f"Expected a JSON object on line {line_number}"
                )

            required = (
                "attempt_id",
                "model",
                "model_version",
                "task_id",
                "passed",
                "failed",
                "status",
            )
            missing = [key for key in required if key not in record]
            if missing:
                raise ValueError(
                    f"Line {line_number} is missing fields: "
                    + ", ".join(missing)
                )

            for field in ("passed", "failed"):
                value = record[field]
                if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                    raise ValueError(
                        f"Line {line_number} has invalid {field}: {value!r}"
                    )

            records.append(record)

    return records


def summarize(records: list[dict]) -> dict:
    """Summarize model attempts separately from controlled/reference runs."""
    model_groups = defaultdict(list)
    task_groups = defaultdict(list)
    excluded = []

    for record in records:
        model = str(record["model"])
        task_id = str(record["task_id"])

        if model in {"controlled-reference", "Controlled-Fault"}:
            excluded.append(record)
            continue

        key = (model, str(record["model_version"]))
        model_groups[key].append(record)
        task_groups[(model, str(record["model_version"]), task_id)].append(record)

    def group_summary(items: list[dict]) -> dict:
        passed = sum(item["passed"] for item in items)
        failed = sum(item["failed"] for item in items)
        total = passed + failed
        return {
            "attempts": len(items),
            "passed": passed,
            "failed": failed,
            "tests_total": total,
            "pass_rate": round(passed / total, 4) if total else 0.0,
            "successful_attempts": sum(item["status"] == "passed" for item in items),
            "failed_attempts": sum(item["status"] != "passed" for item in items),
        }

    by_model = {
        f"{model} ({version})": group_summary(items)
        for (model, version), items in sorted(model_groups.items())
    }
    by_task = {
        f"{model} ({version}) / {task_id}": group_summary(items)
        for (model, version, task_id), items in sorted(task_groups.items())
    }

    return {
        "record_count": len(records),
        "model_attempt_count": sum(len(items) for items in model_groups.values()),
        "excluded_control_count": len(excluded),
        "by_model": by_model,
        "by_model_and_task": by_task,
        "excluded_controls": [
            {
                "attempt_id": item["attempt_id"],
                "model": item["model"],
                "task_id": item["task_id"],
                "passed": item["passed"],
                "failed": item["failed"],
                "status": item["status"],
            }
            for item in excluded
        ],
        "limitations": [
            "Records labelled with model names are not independently verified as model-generated.",
            "Repeated attempts may use the same candidate and are not independent samples.",
            "Pass rates describe these recorded tests only, not general software engineering ability.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Summarize PatchProof AI patch evaluation records."
    )
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.is_absolute():
        input_path = ROOT / input_path
    if not output_path.is_absolute():
        output_path = ROOT / output_path

    try:
        records = load_records(input_path)
        report = summarize(records)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    except (OSError, ValueError) as exc:
        parser.exit(2, f"Report error: {exc}\n")

    print(f"Records loaded: {report['record_count']}")
    print(f"Model-labelled attempts: {report['model_attempt_count']}")
    print(f"Excluded control records: {report['excluded_control_count']}")

    for name, stats in report["by_model"].items():
        print(
            f"{name}: {stats['passed']}/{stats['tests_total']} tests passed "
            f"({stats['pass_rate']:.1%}); "
            f"{stats['successful_attempts']} passing attempts, "
            f"{stats['failed_attempts']} failing attempts"
        )

    print(f"Report saved: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
