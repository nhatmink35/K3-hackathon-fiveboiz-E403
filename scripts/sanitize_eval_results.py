"""Remove generated answer text before evaluation CSV files are committed."""

from __future__ import annotations

import csv
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = REPO_ROOT / "eval" / "results"
PRIVATE_RESULTS_DIR = REPO_ROOT / "eval" / "private-results"


def main() -> None:
    PRIVATE_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    paths = sorted(RESULTS_DIR.glob("run-*.csv"))
    for path in paths:
        rows: list[dict[str, str]]
        with path.open(encoding="utf-8-sig", newline="") as source:
            reader = csv.DictReader(source)
            fieldnames = list(reader.fieldnames or [])
            rows = list(reader)

        private_path = PRIVATE_RESULTS_DIR / path.name
        if not private_path.exists():
            private_path.write_bytes(path.read_bytes())

        for row in rows:
            if "answer" in row:
                row["answer"] = "[omitted from Git; see local private-results]"

        with path.open("w", encoding="utf-8-sig", newline="") as output:
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Sanitized {path.name}")


if __name__ == "__main__":
    main()
