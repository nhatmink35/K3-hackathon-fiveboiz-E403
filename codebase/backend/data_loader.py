import os
import glob
import math
import re
import unicodedata
from collections import Counter
from typing import List, Dict, Any


TOKEN_PATTERN = re.compile(r"[a-z0-9]+", re.IGNORECASE)
STOPWORDS = {
    "ai", "ban", "bai", "cac", "cho", "co", "cua", "duoc", "gi", "hay",
    "khong", "la", "mot", "nao", "nhu", "nhung", "theo", "the", "trong",
    "toi", "va", "ve",
}


def _normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text.lower())
    normalized = "".join(
        char for char in decomposed if unicodedata.category(char) != "Mn"
    )
    return normalized.replace("đ", "d")


def _tokenize(text: str) -> List[str]:
    return [
        token
        for token in TOKEN_PATTERN.findall(_normalize(text))
        if len(token) > 1 and token not in STOPWORDS
    ]


class DataLoader:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.chunks: List[Dict[str, Any]] = []
        self.slides: List[Dict[str, Any]] = []
        self._term_frequencies: List[Counter] = []
        self._idf: Dict[str, float] = {}

    def load_all(self):
        self.chunks = []
        self.slides = []
        files = glob.glob(os.path.join(self.data_dir, "transcript-*-clean.md"))
        slide_id_counter = 1

        for file_path in sorted(files):
            filename = os.path.basename(file_path)
            if not os.path.exists(file_path):
                continue
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract file title
            title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
            file_title = title_match.group(1).strip() if title_match else filename

            current_section = file_title
            current_slide: Dict[str, Any] | None = None
            current_chunk_code: str | None = None
            current_chunk_lines: List[str] = []

            lines = content.split('\n')

            for line in lines:
                stripped = line.strip()

                # Skip empty lines, blockquotes (metadata), and top-level title
                if not stripped or stripped.startswith('> ') or stripped.startswith('# '):
                    continue

                # Section header
                if stripped.startswith('## '):
                    # Flush any in-progress chunk
                    if current_chunk_code and current_chunk_lines:
                        chunk_text = ' '.join(current_chunk_lines).strip()
                        self.chunks.append({
                            "code": current_chunk_code,
                            "text": chunk_text,
                            "section": current_section,
                            "source": filename
                        })
                        if current_slide:
                            current_slide["chunk_codes"].append(current_chunk_code)
                            current_slide["content"] += chunk_text + "\n"
                        current_chunk_code = None
                        current_chunk_lines = []

                    # Save previous slide
                    if current_slide and current_slide["chunk_codes"]:
                        self.slides.append(current_slide)

                    current_section = stripped[3:].strip()
                    current_slide = {
                        "id": f"slide-{slide_id_counter}",
                        "title": current_section,
                        "source": filename,
                        "content": "",
                        "chunk_codes": []
                    }
                    slide_id_counter += 1
                    continue

                # Chunk code line: **[Txx-NNN]** text...
                chunk_match = re.match(r'\*\*\[([^\]]+)\]\*\*\s*(.*)', stripped)
                if chunk_match:
                    # Flush previous chunk
                    if current_chunk_code and current_chunk_lines:
                        chunk_text = ' '.join(current_chunk_lines).strip()
                        self.chunks.append({
                            "code": current_chunk_code,
                            "text": chunk_text,
                            "section": current_section,
                            "source": filename
                        })
                        if current_slide:
                            current_slide["chunk_codes"].append(current_chunk_code)
                            current_slide["content"] += chunk_text + "\n"

                    # Start new chunk
                    current_chunk_code = chunk_match.group(1)
                    first_line = chunk_match.group(2).strip()
                    current_chunk_lines = [first_line] if first_line else []

                    # Ensure we have a slide
                    if not current_slide:
                        current_slide = {
                            "id": f"slide-{slide_id_counter}",
                            "title": current_section,
                            "source": filename,
                            "content": "",
                            "chunk_codes": []
                        }
                        slide_id_counter += 1
                    continue

                # Continuation line of current chunk
                if current_chunk_code and stripped:
                    # Skip activity notes like [Hoạt động lớp: ...]
                    if stripped.startswith('[Hoạt động lớp'):
                        continue
                    current_chunk_lines.append(stripped)

            # Flush last chunk in file
            if current_chunk_code and current_chunk_lines:
                chunk_text = ' '.join(current_chunk_lines).strip()
                self.chunks.append({
                    "code": current_chunk_code,
                    "text": chunk_text,
                    "section": current_section,
                    "source": filename
                })
                if current_slide:
                    current_slide["chunk_codes"].append(current_chunk_code)
                    current_slide["content"] += chunk_text + "\n"

            # Flush last slide in file
            if current_slide and current_slide["chunk_codes"]:
                self.slides.append(current_slide)

        self._build_search_index()
        print(f"[DataLoader] Loaded {len(self.chunks)} chunks, {len(self.slides)} slides from {len(files)} files")

    def _build_search_index(self) -> None:
        self._term_frequencies = []
        document_frequency: Counter = Counter()

        for chunk in self.chunks:
            searchable_text = f"{chunk['section']} {chunk['section']} {chunk['text']}"
            frequencies = Counter(_tokenize(searchable_text))
            self._term_frequencies.append(frequencies)
            document_frequency.update(frequencies.keys())

        corpus_size = max(len(self.chunks), 1)
        self._idf = {
            term: math.log(1 + (corpus_size - count + 0.5) / (count + 0.5))
            for term, count in document_frequency.items()
        }

    def get_slides(self, max_slides: int = None) -> List[Dict[str, Any]]:
        return self.slides[:max_slides] if max_slides else self.slides

    def get_context_for_slides(self, slide_ids: List[str] = None, max_chunks: int = 40) -> str:
        if not slide_ids:
            # Return first N chunks as default context
            target_chunks = self.chunks[:max_chunks]
        else:
            target_codes = set()
            for slide in self.slides:
                if slide["id"] in slide_ids:
                    target_codes.update(slide["chunk_codes"])
            target_chunks = [c for c in self.chunks if c["code"] in target_codes]

            # If no matching chunks found, fall back to default
            if not target_chunks:
                target_chunks = self.chunks[:max_chunks]

        context_lines = []
        for c in target_chunks:
            # Truncate very long chunks to save tokens
            text = c['text'][:500] if len(c['text']) > 500 else c['text']
            context_lines.append(f"[{c['code']}] ({c['section']}): {text}")
        return "\n\n".join(context_lines)

    def get_context_for_query(self, query: str, max_chunks: int = 16) -> str:
        """Retrieve the most relevant chunks from the complete transcript corpus."""
        query_tokens = _tokenize(query)
        if not query_tokens:
            return self.get_context_for_slides(max_chunks=max_chunks)

        scored_chunks = []
        for index, (chunk, frequencies) in enumerate(
            zip(self.chunks, self._term_frequencies)
        ):
            score = 0.0
            for token in query_tokens:
                term_frequency = frequencies.get(token, 0)
                if term_frequency:
                    score += self._idf.get(token, 0.0) * (
                        1.0 + math.log(term_frequency)
                    )
            if score > 0:
                scored_chunks.append((score, index, chunk))

        if not scored_chunks:
            return self.get_context_for_slides(max_chunks=max_chunks)

        scored_chunks.sort(key=lambda item: (-item[0], item[1]))
        selected = scored_chunks[:max_chunks]
        context_lines = []
        for _, _, chunk in selected:
            text = chunk["text"][:700]
            context_lines.append(
                f"[{chunk['code']}] ({chunk['section']}): {text}"
            )
        return "\n\n".join(context_lines)

    def search_chunks(self, query: str) -> List[Dict[str, Any]]:
        query_lower = query.lower()
        results = []
        for c in self.chunks:
            if query_lower in c['text'].lower() or query_lower in c['section'].lower():
                results.append(c)
        return results[:20]  # Limit results
