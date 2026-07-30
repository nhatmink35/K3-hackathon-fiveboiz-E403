"""Create a private HTML copy with processed slide text embedded.

This keeps the CP2 single-file UI usable without a slide-fetch API. The output
inherits the data pack's privacy restrictions and must not be published.
"""

from __future__ import annotations

import html
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = REPO_ROOT / "index.html"
PRIVATE_INDEX_PATH = REPO_ROOT / "index.private.html"
SLIDE_DATA = (
    REPO_ROOT / "data" / "vlearn-pack" / "processed" / "slide_chunks.jsonl"
)


KNOWLEDGE_BASE = r"""const knowledgeBase = {
      coban: {
        badgeClass: "badge-coban",
        label: "Cơ bản",
        questions: [
          "AI, Machine Learning, Deep Learning, GenAI và LLM khác nhau thế nào?",
          "Token là gì và vì sao model không đọc nguyên từng từ?",
          "Một problem statement một câu cần mô tả những gì?"
        ],
        answers: {},
        test: {
          question: "Theo bài Day 1, LLM nằm ở đâu trong hệ các khái niệm AI?",
          options: [
            "A. LLM là chiếc ô lớn nhất bao trùm toàn bộ AI",
            "B. LLM là model nền chuyên ngôn ngữ thuộc Generative AI",
            "C. LLM hoàn toàn không liên quan đến Deep Learning",
            "D. LLM chỉ là một tên gọi khác của chatbot"
          ],
          correctIndex: 1,
          slideTarget: "slide-D1-3",
          slideName: "Day 1 · Trang 3: Bức tranh AI, ML, Deep Learning, GenAI và LLM",
          feedbackWrong: "LLM là model nền chuyên ngôn ngữ trong hệ Generative AI; chatbot chỉ là một dạng sản phẩm được đóng gói quanh model nền."
        }
      },
      thongthao: {
        badgeClass: "badge-thongthao",
        label: "Thông thạo",
        questions: [
          "Context và attention giữ vai trò gì khi LLM xử lý câu hỏi?",
          "Từ LLM đến agent có những mức năng lực nào?",
          "Baseline, target và measurement liên hệ với nhau thế nào?"
        ],
        answers: {},
        test: {
          question: "Điểm khác biệt cốt lõi khi chuyển từ LLM sang agent là gì?",
          options: [
            "A. Agent chỉ đổi màu giao diện của chatbot",
            "B. Agent thêm khả năng dùng công cụ, nhớ trạng thái và lặp để đạt mục tiêu",
            "C. Agent không cần model ngôn ngữ",
            "D. Agent luôn chính xác và không cần kiểm soát"
          ],
          correctIndex: 1,
          slideTarget: "slide-D1-23",
          slideName: "Day 1 · Trang 23: Từ LLM đến agent",
          feedbackWrong: "Agent bổ sung năng lực hành động, công cụ, trạng thái và vòng lặp; điều đó không đồng nghĩa agent luôn đúng."
        }
      },
      nangcao: {
        badgeClass: "badge-nangcao",
        label: "Nâng cao",
        questions: [
          "Khi nào automate hoàn toàn rủi ro hơn augment?",
          "Vì sao nên chọn model theo tầng thay vì chỉ nhìn tên model?",
          "Temperature và top_p tạo ra những đánh đổi nào?"
        ],
        answers: {},
        test: {
          question: "Khi sai sót có hậu quả cao và cần con người kiểm tra, mức automation phù hợp nhất là gì?",
          options: [
            "A. Automate hoàn toàn mọi trường hợp",
            "B. Augment hoặc conditional automation với điểm kiểm soát của con người",
            "C. Luôn dùng agent tự chủ nhiều bước",
            "D. Bỏ toàn bộ bước đo lường"
          ],
          correctIndex: 1,
          slideTarget: "slide-D2-17",
          slideName: "Day 2 · Trang 17: Automate và Augment",
          feedbackWrong: "Khi cost-of-error cao, nên giữ quyền quyết định hoặc điểm kiểm soát cho con người thay vì tự động hóa hoàn toàn."
        }
      }
    };"""


def render_slide(chunk: dict[str, object], total: int) -> str:
    document_id = str(chunk["document_id"])
    page = int(chunk["page"])
    title = html.escape(str(chunk["page_title"]))
    citation = html.escape(str(chunk["citation"]))
    content_lines = [
        html.escape(line.strip())
        for line in str(chunk["content"]).splitlines()
        if line.strip()
    ]
    content = "\n".join(f"              <p>{line}</p>" for line in content_lines)
    return f"""        <div class="slide-card" id="slide-{document_id}-{page}">
          <div class="slide-header">
            <span>{title}</span>
            <span class="slide-number">{citation} · {page} / {total}</span>
          </div>
          <div class="slide-content">
{content}
          </div>
        </div>"""


def main() -> None:
    chunks = [
        json.loads(line)
        for line in SLIDE_DATA.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    totals: dict[str, int] = {}
    for chunk in chunks:
        document_id = str(chunk["document_id"])
        totals[document_id] = max(totals.get(document_id, 0), int(chunk["page"]))

    rendered = "\n\n".join(
        render_slide(chunk, totals[str(chunk["document_id"])]) for chunk in chunks
    )
    new_container = (
        '      <div class="slides-container" id="slides-container">\n'
        f"{rendered}\n"
        "      </div>"
    )

    source = INDEX_PATH.read_text(encoding="utf-8")
    container_start = source.index(
        '      <div class="slides-container" id="slides-container">'
    )
    section_marker = "\n    </div>\n\n    <!-- KHU VỰC 2:"
    doc_section_end = source.index(section_marker, container_start)
    container_end = source.rfind("\n      </div>", container_start, doc_section_end)
    if container_end < 0:
        raise RuntimeError("Could not locate slides-container closing tag")
    container_end += len("\n      </div>")
    source = source[:container_start] + new_container + source[container_end:]

    kb_start = source.index("const knowledgeBase = {")
    kb_end_marker = "\n\n    let isMinimized"
    kb_end = source.index(kb_end_marker, kb_start)
    source = source[:kb_start] + KNOWLEDGE_BASE + source[kb_end:]

    PRIVATE_INDEX_PATH.write_text(source, encoding="utf-8", newline="\n")
    print(f"Embedded {len(chunks)} slide pages into {PRIVATE_INDEX_PATH}")


if __name__ == "__main__":
    main()
