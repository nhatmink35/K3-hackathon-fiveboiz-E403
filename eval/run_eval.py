from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from codebase.backend.config import load_dotenv, require_setting
from codebase.backend.gemini import GeminiClient, GeminiError
from codebase.backend.retrieval import SlideRetriever
from codebase.backend.tutor import TutorService


SLIDE_DATA = (
    REPO_ROOT / "data" / "vlearn-pack" / "processed" / "slide_chunks.jsonl"
)
GOLDEN_SET = REPO_ROOT / "eval" / "golden_set.json"
RESULTS_DIR = REPO_ROOT / "eval" / "results"


def grade(case: dict[str, object], result: dict[str, object]) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    expected_status = str(case["expected_status"])
    actual_status = str(result["status"])
    if expected_status != actual_status:
        reasons.append(f"status {actual_status}, expected {expected_status}")

    expected_citations = set(case["expected_citations"])
    actual_citations = {
        str(item["chunk_id"]) for item in result.get("citations", [])
    }
    if expected_status == "answered":
        if expected_citations and not actual_citations.intersection(expected_citations):
            reasons.append("no expected citation")
        if len(result.get("suggestions", [])) < 2:
            reasons.append("fewer than 2 suggestions")
    elif actual_citations:
        reasons.append("insufficient case must not cite a source")

    return not reasons, reasons


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Run only the first N cases for a smoke test.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=5.0,
        help="Seconds between cases to reduce free-tier rate-limit errors.",
    )
    args = parser.parse_args()

    load_dotenv(REPO_ROOT / ".env")
    client = GeminiClient(
        api_key=require_setting("GEMINI_API_KEY"),
        model=require_setting("GEMINI_MODEL"),
    )
    service = TutorService(SlideRetriever(SLIDE_DATA), client)
    payload = json.loads(GOLDEN_SET.read_text(encoding="utf-8"))
    cases = payload["cases"][: args.limit]

    started_at = datetime.now(timezone.utc)
    rows: list[dict[str, object]] = []
    for index, case in enumerate(cases, start=1):
        started = time.perf_counter()
        try:
            answer = service.answer(str(case["question"]), str(case["level"]))
            result = answer.to_dict()
            passed, reasons = grade(case, result)
            error = ""
        except GeminiError as exc:
            result = {
                "status": "ai_error",
                "answer_type": "",
                "answer": "",
                "citations": [],
                "suggestions": [],
                "model": "",
                "usage": {},
            }
            passed = False
            reasons = ["AI request failed"]
            error = str(exc)[:300]

        latency_ms = round((time.perf_counter() - started) * 1000)
        citation_ids = [
            item["chunk_id"] for item in result.get("citations", [])
        ]
        usage = result.get("usage", {})
        row = {
            "case_id": case["id"],
            "source": case["source"],
            "class": case["class"],
            "question": case["question"],
            "expected_status": case["expected_status"],
            "actual_status": result["status"],
            "answer_type": result["answer_type"],
            "citation_ids": "|".join(citation_ids),
            "suggestion_count": len(result.get("suggestions", [])),
            "pass": passed,
            "failure_reason": "; ".join(reasons),
            "latency_ms": latency_ms,
            "model": result.get("model") or "",
            "input_tokens": usage.get("promptTokenCount", ""),
            "output_tokens": usage.get("candidatesTokenCount", ""),
            "total_tokens": usage.get("totalTokenCount", ""),
            "answer": result.get("answer", ""),
            "error": error,
        }
        rows.append(row)
        print(
            f"[{index:02d}/{len(cases):02d}] {case['id']} "
            f"{'PASS' if passed else 'FAIL'} ({latency_ms} ms)"
        )
        if index < len(cases) and args.delay > 0:
            time.sleep(args.delay)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    run_id = started_at.strftime("%Y%m%dT%H%M%SZ")
    csv_path = RESULTS_DIR / f"run-{run_id}.csv"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    passed_count = sum(bool(row["pass"]) for row in rows)
    summary = {
        "run_id": run_id,
        "started_at": started_at.isoformat(),
        "model": client.model,
        "case_count": len(rows),
        "passed": passed_count,
        "failed": len(rows) - passed_count,
        "pass_rate": round(passed_count / len(rows) * 100, 2),
        "quality_bar": 85,
        "quality_bar_met": passed_count / len(rows) >= 0.85,
        "result_file": csv_path.name,
    }
    summary_path = RESULTS_DIR / f"run-{run_id}-summary.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
