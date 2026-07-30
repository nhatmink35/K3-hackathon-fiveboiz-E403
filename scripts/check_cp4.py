"""Fail-fast validation for CP4 artifacts."""

from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC = REPO_ROOT / "spec.md"
REPORT = REPO_ROOT / "evidence" / "mining-report.md"
MINER = REPO_ROOT / "evidence" / "mine_chatlog.py"
GOLDEN_SET = REPO_ROOT / "eval" / "golden_set.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"CP4 FAIL: {message}")


def main() -> None:
    for path in (SPEC, REPORT, MINER, GOLDEN_SET):
        require(path.exists(), f"missing {path.relative_to(REPO_ROOT)}")

    spec = SPEC.read_text(encoding="utf-8")
    report = REPORT.read_text(encoding="utf-8")
    cases = json.loads(GOLDEN_SET.read_text(encoding="utf-8"))["cases"]

    require("Chưa chốt ở mốc 1" not in spec, "spec still contains old placeholder")
    require("Chưa thực hiện ở mốc 1" not in spec, "research is not finalized")
    require("1.261/1.261" in spec, "missing quantitative evidence")
    require("Ứng viên" in spec and spec.count("| A.") == 1, "impact table missing")
    require("ChatGPT Study Mode" in spec and "NotebookLM" in spec, "research missing")
    require(spec.count("| R") >= 10, "fewer than 8 risk scenarios")
    require("85%" in spec, "quality bar missing")
    require(len(cases) >= 20, "golden set has fewer than 20 cases")
    require(
        sum(str(case["source"]).startswith("chatlog:") for case in cases) >= 10,
        "golden set has fewer than 10 chatlog-derived cases",
    )
    require(report.count("| T") >= 5, "evidence report has fewer than 5 turn examples")

    print("CP4 PASS: evidence, impact, research, risks, quality bar and golden set are present")


if __name__ == "__main__":
    main()
