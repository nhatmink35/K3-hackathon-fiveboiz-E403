from __future__ import annotations

from dataclasses import dataclass

from codebase.backend.gemini import GeminiClient, GeminiError
from codebase.backend.retrieval import SearchResult, SlideRetriever


LEVEL_LABELS = {
    "coban": "Cơ bản",
    "thongthao": "Thông thạo",
    "nangcao": "Nâng cao",
}

ANSWER_SCHEMA = {
    "type": "object",
    "properties": {
        "answer_type": {
            "type": "string",
            "enum": ["direct", "inference", "insufficient"],
        },
        "answer": {"type": "string"},
        "citation_ids": {"type": "array", "items": {"type": "string"}},
        "suggestions": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 2,
            "maxItems": 3,
        },
    },
    "required": ["answer_type", "answer", "citation_ids", "suggestions"],
}

SYSTEM_INSTRUCTION = """Bạn là VLearn AI Tutor cho học viên Việt Nam.
Chỉ dùng SOURCE CHUNKS được cung cấp. Không dùng kiến thức có sẵn của model.
Mỗi mệnh đề kiến thức phải truy vết được về ít nhất một chunk.
Nếu nguồn không đủ, answer_type=insufficient và nói rõ giới hạn, không đoán.
Nếu kết luận là suy luận hợp lý nhưng không được viết trực tiếp, dùng
answer_type=inference và nêu rõ đó là suy luận.
citation_ids chỉ chứa chunk_id có trong SOURCE CHUNKS.
Trả lời trực tiếp, dễ hiểu, không chấm điểm chính thức.
Sinh 2-3 câu hỏi tiếp theo đúng LEVEL và có thể trả lời từ SOURCE CHUNKS.
Không suy đoán trình độ từ cách viết câu hỏi của học viên."""


@dataclass(frozen=True)
class TutorAnswer:
    status: str
    answer_type: str
    answer: str
    citations: list[dict[str, object]]
    suggestions: list[str]
    contexts: list[dict[str, object]]
    model: str | None = None
    usage: dict[str, object] | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "answer_type": self.answer_type,
            "answer": self.answer,
            "citations": self.citations,
            "suggestions": self.suggestions,
            "contexts": self.contexts,
            "model": self.model,
            "usage": self.usage or {},
        }


class TutorService:
    def __init__(
        self,
        retriever: SlideRetriever,
        client: GeminiClient | None,
        minimum_score: float = 0.8,
    ):
        self.retriever = retriever
        self.client = client
        self.minimum_score = minimum_score

    def answer(self, query: str, level: str) -> TutorAnswer:
        results = self.retriever.search(query, limit=4)
        context_dicts = [result.to_dict() for result in results]
        if not results or results[0].score < self.minimum_score:
            return self._insufficient(context_dicts)
        if self.client is None:
            raise GeminiError("Gemini is not configured")

        prompt = self._build_prompt(query, level, results)
        generated = self.client.generate_json(
            SYSTEM_INSTRUCTION,
            prompt,
            ANSWER_SCHEMA,
        )
        return self._validate_generated(generated.data, generated.model, generated.usage, results)

    def _build_prompt(
        self,
        query: str,
        level: str,
        results: list[SearchResult],
    ) -> str:
        sources = "\n\n".join(
            f"<SOURCE id=\"{item.chunk['chunk_id']}\" "
            f"citation=\"{item.chunk['citation']}\">\n"
            f"{item.chunk['content']}\n</SOURCE>"
            for item in results
        )
        return (
            f"LEVEL: {LEVEL_LABELS[level]}\n"
            f"USER QUESTION: {query}\n\n"
            f"SOURCE CHUNKS:\n{sources}"
        )

    def _validate_generated(
        self,
        data: dict[str, object],
        model: str,
        usage: dict[str, object],
        results: list[SearchResult],
    ) -> TutorAnswer:
        allowed = {str(item.chunk["chunk_id"]): item for item in results}
        answer_type = str(data.get("answer_type", "insufficient"))
        citation_ids = [
            str(item)
            for item in data.get("citation_ids", [])
            if str(item) in allowed
        ]
        answer = str(data.get("answer", "")).strip()
        suggestions = [
            str(item).strip()
            for item in data.get("suggestions", [])
            if str(item).strip()
        ][:3]

        if answer_type not in {"direct", "inference", "insufficient"}:
            answer_type = "insufficient"
        if answer_type != "insufficient" and not citation_ids:
            return self._insufficient(
                [item.to_dict() for item in results],
                reason="Model không cung cấp citation hợp lệ.",
            )
        if not answer:
            return self._insufficient([item.to_dict() for item in results])

        citations = [
            {
                "chunk_id": chunk_id,
                "citation": allowed[chunk_id].chunk["citation"],
                "document_title": allowed[chunk_id].chunk["document_title"],
                "page": allowed[chunk_id].chunk["page"],
            }
            for chunk_id in citation_ids
        ]
        return TutorAnswer(
            status="answered" if answer_type != "insufficient" else "insufficient_source",
            answer_type=answer_type,
            answer=answer,
            citations=citations,
            suggestions=suggestions,
            contexts=[item.to_dict() for item in results],
            model=model,
            usage=usage,
        )

    def _insufficient(
        self,
        contexts: list[dict[str, object]],
        reason: str | None = None,
    ) -> TutorAnswer:
        message = reason or (
            "Mình chưa tìm thấy căn cứ đủ rõ trong hai bộ slide để trả lời chắc chắn. "
            "Bạn hãy nêu rõ khái niệm hoặc bài học đang hỏi."
        )
        return TutorAnswer(
            status="insufficient_source",
            answer_type="insufficient",
            answer=message,
            citations=[],
            suggestions=[],
            contexts=contexts,
        )
