
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
    from .registry import TASKS
except ImportError:
    from registry import TASKS

def evaluate(candidate_path: Path, task_id: str = "PP-001") -> dict:
    """Run a task's contract tests against a candidate Python file."""
    if task_id not in TASKS:
        raise ValueError(f"Unknown task {task_id!r}. Choose from: {', '.join(TASKS)}")

    candidate_path = candidate_path.resolve()
    if not candidate_path.is_file():
        raise FileNotFoundError(f"Candidate file not found: {candidate_path}")

    timestamp = datetime.now(timezone.utc).isoformat()

    with tempfile.TemporaryDirectory(prefix="patchproof_") as temp:
        sandbox = Path(temp)
        shutil.copy2(candidate_path, sandbox / "candidate.py")
        (sandbox / "test_candidate.py").write_text(
            TASKS[task_id]["test_source"], encoding="utf-8"
        )

        try:
            completed = subprocess.run(
                [sys.executable, "-m", "pytest", "-q", "test_candidate.py"],
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
        passed_match = re.search(r"(\d+) passed", output)
        failed_match = re.search(r"(\d+) failed", output)
        error_match = re.search(r"(\d+) errors?", output)

        passed = int(passed_match.group(1)) if passed_match else 0
        failed = int(failed_match.group(1)) if failed_match else 0
        errors = int(error_match.group(1)) if error_match else 0

        summary_found = bool(passed_match or failed_match or error_match)
        if not summary_found and completed.returncode != 0:
            status = "harness_error"
        elif completed.returncode == 0 and failed == 0 and errors == 0:
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
    parser.add_argument(
        "--candidate",
        required=True,
        help="Path to a Python file implementing final_price.",
    )
    parser.add_argument(
        "--task",
        choices=sorted(TASKS),
        default="PP-001",
        help="Contract task to evaluate (default: PP-001).",
    )
    parser.add_argument(
        "--output",
        default="results/latest.json",
        help="Path for the JSON result report.",
    )
    args = parser.parse_args()

    try:
        result = evaluate(Path(args.candidate), args.task)
    except (OSError, ValueError) as exc:
        print(f"Evaluation error: {exc}", file=sys.stderr)
        return 2

    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = Path(__file__).resolve().parent.parent / output_path

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, indent=2),
        encoding="utf-8",
    )

    print(f"Task: {result['task_id']}")
    print(f"Passed: {result['passed']}")
    print(f"Failed: {result['failed']}")
    print(f"Errors: {result['errors']}")
    print(f"Status: {result['status']}")
    print(f"Success: {result['success']}")
    print(f"Report: {output_path}")
    print("\nTest output:\n" + result["output"])

    return 0 if result["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
