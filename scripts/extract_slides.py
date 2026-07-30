"""Extract the private VLearn slide pack into page-aware JSONL chunks.

Run from the repository root:
    python scripts/extract_slides.py

The generated files stay inside data/vlearn-pack/processed because they are
derived from the private hackathon data pack and must not be published.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

from pypdf import PdfReader


REPO_ROOT = Path(__file__).resolve().parents[1]
SLIDES_DIR = REPO_ROOT / "data" / "vlearn-pack" / "slides"
OUTPUT_DIR = REPO_ROOT / "data" / "vlearn-pack" / "processed"
MAX_CHUNK_CHARS = 1_500

DOCUMENTS = {
    "d1-slide-hackathon.pdf": {
        "document_id": "D1",
        "course_day": 1,
        "document_title": "AI & LLM Foundation",
    },
    "d2-slide-hackathon.pdf": {
        "document_id": "D2",
        "course_day": 2,
        "document_title": "Xác định bài toán cho AI",
    },
}

REPEATED_LINES = {
    "AI IN ACTION - HACKATHON",
    "AI IN ACTION · DAY 02",
}


def clean_text(raw_text: str) -> str:
    """Remove PDF artifacts while preserving Vietnamese and paragraph breaks."""
    cleaned_chars: list[str] = []
    for char in raw_text.replace("\x00", " "):
        category = unicodedata.category(char)
        if category == "Co":
            cleaned_chars.append(" ")
        elif category.startswith("C") and char not in "\n\t":
            cleaned_chars.append(" ")
        else:
            cleaned_chars.append(char)

    lines: list[str] = []
    for raw_line in "".join(cleaned_chars).splitlines():
        line = re.sub(r"[ \t]+", " ", raw_line).strip()
        if not line or line in REPEATED_LINES:
            continue
        lines.append(line)

    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return unicodedata.normalize("NFC", text).strip()


def infer_title(text: str, fallback: str) -> str:
    """Pick the first useful short line as a human-readable page title."""
    ignored_prefixes = ("AI IN ACTION", "DAY 0")
    for line in text.splitlines():
        candidate = line.strip("•·—- ")
        if (
            4 <= len(candidate) <= 120
            and not candidate.upper().startswith(ignored_prefixes)
            and not re.fullmatch(r"\d+", candidate)
        ):
            return candidate
    return fallback


def split_page(text: str, max_chars: int = MAX_CHUNK_CHARS) -> list[str]:
    """Split long pages on line boundaries without crossing page boundaries."""
    if len(text) <= max_chars:
        return [text] if text else []

    chunks: list[str] = []
    current: list[str] = []
    current_length = 0
    for line in text.splitlines():
        projected = current_length + len(line) + (1 if current else 0)
        if current and projected > max_chars:
            chunks.append("\n".join(current))
            current = []
            current_length = 0

        if len(line) > max_chars:
            if current:
                chunks.append("\n".join(current))
                current = []
                current_length = 0
            for start in range(0, len(line), max_chars):
                chunks.append(line[start : start + max_chars])
            continue

        current.append(line)
        current_length += len(line) + (1 if current_length else 0)

    if current:
        chunks.append("\n".join(current))
    return chunks


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    chunks: list[dict[str, object]] = []
    documents: list[dict[str, object]] = []

    for filename, metadata in DOCUMENTS.items():
        pdf_path = SLIDES_DIR / filename
        if not pdf_path.exists():
            raise FileNotFoundError(f"Missing slide deck: {pdf_path}")

        reader = PdfReader(pdf_path)
        document_chunk_count = 0
        pages_with_text = 0

        for page_index, page in enumerate(reader.pages, start=1):
            page_text = clean_text(page.extract_text() or "")
            if not page_text:
                continue
            pages_with_text += 1
            page_title = infer_title(
                page_text,
                f"{metadata['document_title']} — trang {page_index}",
            )
            page_chunks = split_page(page_text)

            for chunk_index, content in enumerate(page_chunks, start=1):
                chunk_id = (
                    f"{metadata['document_id']}-P{page_index:02d}-C{chunk_index:02d}"
                )
                chunks.append(
                    {
                        "chunk_id": chunk_id,
                        "document_id": metadata["document_id"],
                        "document_title": metadata["document_title"],
                        "source_file": filename,
                        "course_day": metadata["course_day"],
                        "page": page_index,
                        "page_title": page_title,
                        "chunk_index": chunk_index,
                        "citation": f"[{metadata['document_id']}, trang {page_index}]",
                        "content": content,
                        "char_count": len(content),
                    }
                )
                document_chunk_count += 1

        documents.append(
            {
                **metadata,
                "source_file": filename,
                "page_count": len(reader.pages),
                "pages_with_text": pages_with_text,
                "chunk_count": document_chunk_count,
                "sha256": sha256(pdf_path),
            }
        )

    jsonl_path = OUTPUT_DIR / "slide_chunks.jsonl"
    with jsonl_path.open("w", encoding="utf-8", newline="\n") as output:
        for chunk in chunks:
            output.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    manifest = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "max_chunk_chars": MAX_CHUNK_CHARS,
        "chunk_count": len(chunks),
        "documents": documents,
    }
    manifest_path = OUTPUT_DIR / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Wrote {len(chunks)} chunks to {jsonl_path}")
    for document in documents:
        print(
            f"- {document['document_id']}: {document['page_count']} pages, "
            f"{document['chunk_count']} chunks"
        )


if __name__ == "__main__":
    main()
