"""Replace embedded private slide cards with a safe loading placeholder."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = REPO_ROOT / "index.html"


def main() -> None:
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
    safe_container = """      <div class="slides-container" id="slides-container">
        <div class="slide-card">
          <div class="slide-header">
            <span>Đang tải nội dung bài học...</span>
            <span class="slide-number">VLearn</span>
          </div>
          <div class="slide-content">
            <p>Slide được tải cục bộ từ backend để không đưa data pack riêng tư vào Git.</p>
          </div>
        </div>
      </div>"""
    source = source[:container_start] + safe_container + source[container_end:]
    INDEX_PATH.write_text(source, encoding="utf-8", newline="\n")
    print("Removed private slide contents from index.html")


if __name__ == "__main__":
    main()
