from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from codebase.backend.retrieval import SlideRetriever
from codebase.backend.sessions import SessionStore
from codebase.backend.gemini import GeminiResponse
from codebase.backend.tutor import TutorService


SLIDE_DATA = (
    REPO_ROOT / "data" / "vlearn-pack" / "processed" / "slide_chunks.jsonl"
)


class RetrievalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.retriever = SlideRetriever(SLIDE_DATA)

    def test_loads_all_pages(self) -> None:
        self.assertEqual(len(self.retriever.chunks), 58)

    def test_temperature_query_finds_day_one(self) -> None:
        results = self.retriever.search("temperature và top_p", limit=3)
        self.assertTrue(results)
        self.assertEqual(results[0].chunk["chunk_id"], "D1-P29-C01")

    def test_document_filter(self) -> None:
        results = self.retriever.search("problem statement", document_id="D2")
        self.assertTrue(results)
        self.assertTrue(all(item.chunk["document_id"] == "D2" for item in results))

    def test_empty_query_has_no_results(self) -> None:
        self.assertEqual(self.retriever.search("là gì?"), [])


class SessionTests(unittest.TestCase):
    def test_create_and_change_level(self) -> None:
        store = SessionStore()
        session = store.create("coban")
        updated = store.set_level(session.session_id, "thongthao")
        self.assertIsNotNone(updated)
        self.assertEqual(updated.level, "thongthao")

    def test_rejects_invalid_level(self) -> None:
        store = SessionStore()
        with self.assertRaises(ValueError):
            store.create("expert")


class FakeGeminiClient:
    def __init__(self, response: dict[str, object]):
        self.response = response

    def generate_json(self, *_args, **_kwargs) -> GeminiResponse:
        return GeminiResponse(
            data=self.response,
            model="fake-model",
            usage={"totalTokenCount": 42},
        )


class TutorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.retriever = SlideRetriever(SLIDE_DATA)

    def test_answer_accepts_retrieved_citation(self) -> None:
        client = FakeGeminiClient(
            {
                "answer_type": "direct",
                "answer": "Temperature điều chỉnh độ ngẫu nhiên khi chọn token.",
                "citation_ids": ["D1-P29-C01"],
                "suggestions": ["Top_p khác temperature thế nào?", "Khi nào dùng T thấp?"],
            }
        )
        result = TutorService(self.retriever, client).answer(
            "temperature ảnh hưởng chọn token thế nào?",
            "coban",
        )
        self.assertEqual(result.status, "answered")
        self.assertEqual(result.citations[0]["citation"], "[D1, trang 29]")

    def test_answer_rejects_invented_citation(self) -> None:
        client = FakeGeminiClient(
            {
                "answer_type": "direct",
                "answer": "Một câu trả lời không có nguồn thật.",
                "citation_ids": ["D9-P99-C99"],
                "suggestions": ["Câu tiếp theo?", "Câu khác?"],
            }
        )
        result = TutorService(self.retriever, client).answer(
            "temperature ảnh hưởng chọn token thế nào?",
            "coban",
        )
        self.assertEqual(result.status, "insufficient_source")
        self.assertEqual(result.citations, [])

    def test_no_source_skips_model(self) -> None:
        result = TutorService(self.retriever, None).answer(
            "xyzzy plugh qwerty",
            "coban",
        )
        self.assertEqual(result.status, "insufficient_source")
        self.assertIsNone(result.model)


class GeminiParserTests(unittest.TestCase):
    def test_ignores_thinking_part_and_reads_final_json(self) -> None:
        from codebase.backend.gemini import GeminiClient

        parsed = GeminiClient._parse_json_parts(
            [
                "Tôi đang suy nghĩ nội bộ.",
                '{"answer":"Phobos và Deimos","citation_ids":["SYN-P01"]}',
            ]
        )
        self.assertEqual(parsed["citation_ids"], ["SYN-P01"])

    def test_accepts_json_code_fence(self) -> None:
        from codebase.backend.gemini import GeminiClient

        parsed = GeminiClient._parse_json_parts(
            ['```json\n{"answer":"ok","citation_ids":[]}\n```']
        )
        self.assertEqual(parsed["answer"], "ok")

    def test_fallback_client_uses_secondary_on_rate_limit(self) -> None:
        from codebase.backend.gemini import (
            FallbackGeminiClient,
            GeminiError,
            GeminiResponse,
        )

        class RateLimitedClient:
            model = "primary"

            def generate_json(self, *_args, **_kwargs):
                raise GeminiError("Gemini HTTP 429: quota")

        class WorkingClient:
            model = "fallback"

            def generate_json(self, *_args, **_kwargs):
                return GeminiResponse(
                    data={"answer": "ok"},
                    model=self.model,
                    usage={},
                )

        result = FallbackGeminiClient(
            RateLimitedClient(),
            WorkingClient(),
        ).generate_json("", "", {})
        self.assertEqual(result.model, "fallback")


if __name__ == "__main__":
    unittest.main()
