
"""Evaluate saved AI-generated patches against PatchProof task contracts.

Each patch must be saved as a Python file. The script records the model,
model version, task, prompt, patch path, test results, and timestamp.
It does not call an AI provider or claim that a patch was AI-generated.
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from patchproof.registry import TASKS
from patchproof.runner import evaluate


ROOT = Path(__file__).resolve().parent


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate a saved AI-generated patch."
    )
    parser.add_argument("--candidate", required=True, help="Python patch file")
    parser.add_argument("--task", required=True, choices=sorted(TASKS))
    parser.add_argument("--model", required=True, help="Model name")
    parser.add_argument(
        "--model-version",
        required=True,
        help="Exact model version or 'unknown' if unavailable",
    )
    parser.add_argument(
        "--prompt-file",
        required=True,
        help="Text file containing the exact prompt given to the model",
    )
    parser.add_argument(
        "--attempt-id",
        required=True,
        help="Unique identifier for this model attempt",
    )
    parser.add_argument(
        "--output",
        default="results/ai_patch_evaluations.jsonl",
        help="JSON Lines output file",
    )
    args = parser.parse_args()

    candidate_path = Path(args.candidate).resolve()
    prompt_path = Path(args.prompt_file).resolve()

    if not candidate_path.is_file():
        parser.error(f"Candidate file does not exist: {candidate_path}")
    if not prompt_path.is_file():
        parser.error(f"Prompt file does not exist: {prompt_path}")

    prompt = prompt_path.read_text(encoding="utf-8")
    if not prompt.strip():
        parser.error("Prompt file is empty.")

    result = evaluate(candidate_path, args.task)

    record = {
        "attempt_id": args.attempt_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "model": args.model,
        "model_version": args.model_version,
        "task_id": args.task,
        "prompt_file": str(prompt_path),
        "prompt": prompt,
        "candidate_file": str(candidate_path),
        "passed": result["passed"],
        "failed": result["failed"],
        "errors": result["errors"],
        "exit_code": result["exit_code"],
        "status": result["status"],
        "success": result["success"],
        "test_output": result["output"],
    }

    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = ROOT / output_path

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"Attempt: {record['attempt_id']}")
    print(f"Model: {record['model']} ({record['model_version']})")
    print(f"Task: {record['task_id']}")
    print(f"Passed: {record['passed']}")
    print(f"Failed: {record['failed']}")
    print(f"Errors: {record['errors']}")
    print(f"Status: {record['status']}")
    print(f"Record: {output_path}")

    return 0 if result["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
