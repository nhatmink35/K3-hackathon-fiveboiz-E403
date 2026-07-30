"""Reproducible CP4 evidence mining for the anonymized VLearn chatlog."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = (
    REPO_ROOT
    / "data"
    / "vlearn-pack"
    / "chatlog"
    / "chat_history_anonymized_for_hackathon.csv"
)
REPORT_PATH = REPO_ROOT / "evidence" / "mining-report.md"
EXAMPLE_TURN_IDS = ["T0769", "T0408", "T1258", "T0776", "T0519"]


def parse_json_list(value: str) -> list[object]:
    if not value:
        return []
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return []
    return parsed if isinstance(parsed, list) else []


def compact_quote(value: str, limit: int = 100) -> str:
    compact = " ".join(value.split()).replace("|", "\\|")
    return compact if len(compact) <= limit else compact[: limit - 1] + "…"


def percent(count: int, total: int) -> str:
    return f"{count / total * 100:.1f}%"


def main() -> None:
    with CSV_PATH.open(encoding="utf-8-sig", newline="") as source:
        rows = list(csv.DictReader(source))

    students = [row for row in rows if row["role"] == "student"]
    tutors = [row for row in rows if row["role"] == "tutor"]
    turns: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for row in rows:
        turns[row["turn_id"]][row["role"]] = row

    total = len(tutors)
    no_follow_up = sum(not parse_json_list(row["follow_ups"]) for row in tutors)
    no_misconception = sum(
        not parse_json_list(row["misconceptions"]) for row in tutors
    )
    no_citation = sum(not parse_json_list(row["citations"]) for row in tutors)
    asked_check = sum(
        row["asked_check_question"].strip().lower() == "true" for row in tutors
    )
    rating_counts = Counter(
        row["rating"].strip() for row in tutors if row["rating"].strip()
    )

    metrics = [
        (
            "Tutor không sinh câu hỏi gợi ý tiếp theo",
            no_follow_up,
            percent(no_follow_up, total),
            "`follow_ups` rỗng hoặc `[]`",
        ),
        (
            "Tutor không ghi nhận misconception",
            no_misconception,
            percent(no_misconception, total),
            "`misconceptions` rỗng hoặc `[]`",
        ),
        (
            "Tutor không có citation",
            no_citation,
            percent(no_citation, total),
            "`citations` rỗng hoặc `[]`",
        ),
        (
            "Tutor có hỏi kiểm tra hiểu bài",
            asked_check,
            percent(asked_check, total),
            "`asked_check_question=True`",
        ),
        (
            "Tutor nhận rating down",
            rating_counts.get("down", 0),
            percent(rating_counts.get("down", 0), total),
            "`rating=down`",
        ),
        (
            "Tutor nhận rating up",
            rating_counts.get("up", 0),
            percent(rating_counts.get("up", 0), total),
            "`rating=up`",
        ),
    ]

    lines = [
        "# CP4 Evidence — Mining chatlog VLearn",
        "",
        "## Nguồn và phạm vi",
        "",
        f"- File: `{CSV_PATH.relative_to(REPO_ROOT).as_posix()}`",
        f"- Tổng số dòng: **{len(rows):,}**",
        f"- Student messages: **{len(students):,}**",
        f"- Tutor messages/turn hoàn chỉnh: **{total:,}**",
        f"- Người dùng ẩn danh: **{len({row['user_id'] for row in rows}):,}**",
        f"- Hội thoại: **{len({row['conversation_id'] for row in rows}):,}**",
        "",
        "## Phương pháp có thể kiểm lại",
        "",
        "1. Đọc CSV bằng UTF-8 và tách dòng theo `role`.",
        "2. Mẫu số của các tỷ lệ là toàn bộ tutor messages.",
        "3. Field JSON được xem là rỗng khi giá trị trống hoặc parse thành `[]`.",
        "4. Check question chỉ được tính khi `asked_check_question=True`.",
        "5. Rating được đếm trực tiếp theo `up`/`down`; không suy diễn các dòng null.",
        "6. Ví dụ định tính chọn từ các turn có `rating=down`, giữ mã turn để phúc khảo.",
        "",
        "Chạy lại:",
        "",
        "```powershell",
        "python evidence/mine_chatlog.py",
        "```",
        "",
        "## Kết quả",
        "",
        "| Pattern | Số lượt | Tỷ lệ trên 1.261 lượt tutor | Quy tắc đếm |",
        "|---|---:|---:|---|",
    ]
    for label, count, rate, rule in metrics:
        lines.append(f"| {label} | {count:,} | {rate} | {rule} |")

    lines.extend(
        [
            "",
            "## Năm ví dụ có mã nguồn",
            "",
            "> Các quote dưới đây lấy từ data pack đã ẩn danh. Không dùng để suy ngược danh tính.",
            "",
            "| Turn ID | Câu hỏi học viên (trích ngắn nguyên văn) | Phản hồi tutor (trích ngắn nguyên văn) | Signal |",
            "|---|---|---|---|",
        ]
    )
    for turn_id in EXAMPLE_TURN_IDS:
        pair = turns[turn_id]
        student = pair["student"]
        tutor = pair["tutor"]
        lines.append(
            f"| {turn_id} | “{compact_quote(student['content'])}” "
            f"| “{compact_quote(tutor['content'])}” "
            f"| rating={tutor['rating']}; citations={tutor['citations']}; "
            f"follow_ups={tutor['follow_ups']} |"
        )

    lines.extend(
        [
            "",
            "## Kết luận evidence",
            "",
            f"- **{no_follow_up:,}/{total:,} ({percent(no_follow_up, total)})** lượt tutor "
            "không có follow-up: pain “học viên không có bước học tiếp theo” tồn tại trên toàn bộ mẫu.",
            f"- Chỉ **{asked_check:,}/{total:,} ({percent(asked_check, total)})** lượt tutor "
            "chủ động hỏi để kiểm tra hiểu bài: gần như không có signal để thích ứng độ khó.",
            f"- **{no_citation:,}/{total:,} ({percent(no_citation, total)})** lượt không có "
            "citation: groundedness vẫn là rủi ro quan trọng, nhưng prototype chọn lát cắt "
            "follow-up thích ứng và giữ citation như điều kiện an toàn.",
            f"- Có **{rating_counts.get('down', 0)}** rating down; năm ví dụ cho thấy nhiều "
            "case người học yêu cầu giải thích/tóm tắt nhưng tutor không truy xuất được nguồn "
            "và không đưa ra bước phục hồi đủ hữu ích.",
            "",
            "## Giới hạn",
            "",
            "- Rating chỉ xuất hiện trên một phần nhỏ lượt chat, không dùng để ước lượng mức hài lòng toàn bộ người học.",
            "- `follow_ups=[]` chứng minh feature chưa được sử dụng, không tự nó chứng minh mọi học viên đều muốn follow-up.",
            "- Mining chứng minh pain tồn tại; validation CP5 phải kiểm tra người dùng có thấy gợi ý thích ứng hữu ích hay không.",
        ]
    )

    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {REPORT_PATH}")
    for label, count, rate, _ in metrics:
        print(f"- {label}: {count}/{total} ({rate})")


if __name__ == "__main__":
    main()
