
"""PatchProof: evaluate candidate implementations against contract tests."""

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

try:
    from .history import append_result
    from .registry import TASKS, list_tasks
except ImportError:
    from history import append_result
    from registry import TASKS, list_tasks


def evaluate(candidate_path: Path, task_id: str = "PP-001") -> dict:
    """Run a task's contract tests against a candidate Python file."""
    if task_id not in TASKS:
        raise ValueError(
            f"Unknown task {task_id!r}. "
            f"Choose from: {', '.join(TASKS)}"
        )

    candidate_path = candidate_path.resolve()
    if not candidate_path.is_file():
        raise FileNotFoundError(
            f"Candidate file not found: {candidate_path}"
        )

    timestamp = datetime.now(timezone.utc).isoformat()
    task = TASKS[task_id]
    expected_count = task["test_count"]

    with tempfile.TemporaryDirectory(prefix="patchproof_") as temp:
        sandbox = Path(temp)
        shutil.copy2(candidate_path, sandbox / "candidate.py")
        (sandbox / "test_candidate.py").write_text(
            task["test_source"], encoding="utf-8"
        )

        try:
            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "-q",
                    "test_candidate.py",
                ],
                cwd=sandbox,
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            return {
                "task_id": task_id,
                "candidate": str(candidate_path),
                "timestamp_utc": timestamp,
                "passed": 0,
                "failed": 0,
                "errors": 0,
                "exit_code": None,
                "success": False,
                "status": "timeout",
                "output": str(exc),
            }

        output = completed.stdout + "\n" + completed.stderr
        passed_match = re.search(r"\b(\d+)\s+passed\b", output)
        failed_match = re.search(r"\b(\d+)\s+failed\b", output)
        error_match = re.search(r"\b(\d+)\s+errors?\b", output)

        passed = int(passed_match.group(1)) if passed_match else 0
        failed = int(failed_match.group(1)) if failed_match else 0
        errors = int(error_match.group(1)) if error_match else 0
        summary_found = bool(
            passed_match or failed_match or error_match
        )
        reported_count = passed + failed + errors

        if not summary_found:
            status = (
                "harness_error"
                if completed.returncode != 0
                else "invalid_result"
            )
        elif (
            completed.returncode == 0
            and passed == expected_count
            and failed == 0
            and errors == 0
            and reported_count == expected_count
        ):
            status = "passed"
        else:
            status = "failed"

        return {
            "task_id": task_id,
            "candidate": str(candidate_path),
            "timestamp_utc": timestamp,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "exit_code": completed.returncode,
            "success": status == "passed",
            "status": status,
            "output": output.strip(),
        }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate a candidate implementation with PatchProof."
    )
    parser.add_argument("--candidate", help="Candidate Python file.")
    parser.add_argument(
        "--task",
        choices=sorted(TASKS),
        default="PP-001",
        help="Contract task to evaluate.",
    )
    parser.add_argument(
        "--list-tasks",
        action="store_true",
        help="List registered tasks and exit.",
    )
    parser.add_argument(
        "--output",
        default="results/latest.json",
        help="Path for the latest JSON report.",
    )
    parser.add_argument(
        "--history",
        default="results/history.jsonl",
        help="Path for persistent JSON Lines evaluation history.",
    )
    args = parser.parse_args()

    if args.list_tasks:
        for task in list_tasks():
            print(
                f"{task['task_id']}\t"
                f"{task['description']} ({task['test_count']} tests)"
            )
        return 0

    if not args.candidate:
        parser.error("--candidate is required unless --list-tasks is used")

    try:
        result = evaluate(Path(args.candidate), args.task)
    except (OSError, ValueError) as exc:
        print(f"Evaluation error: {exc}", file=sys.stderr)
        return 2

    project_root = Path(__file__).resolve().parent.parent
    output_path = Path(args.output)
    history_path = Path(args.history)

    if not output_path.is_absolute():
        output_path = project_root / output_path
    if not history_path.is_absolute():
        history_path = project_root / history_path

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(result, indent=2), encoding="utf-8"
        )
        append_result(result, history_path)
    except (OSError, ValueError, TypeError) as exc:
        print(f"Could not save evaluation results: {exc}", file=sys.stderr)
        return 2

    print(f"Task: {result['task_id']}")
    print(f"Passed: {result['passed']}")
    print(f"Failed: {result['failed']}")
    print(f"Errors: {result['errors']}")
    print(f"Status: {result['status']}")
    print(f"Success: {result['success']}")
    print(f"Report: {output_path}")
    print(f"History: {history_path}")
    print("\nTest output:\n" + result["output"])

    return 0 if result["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
