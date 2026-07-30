from __future__ import annotations

import json
import os
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from codebase.backend.retrieval import SlideRetriever
from codebase.backend.config import load_dotenv
from codebase.backend.gemini import FallbackGeminiClient, GeminiClient, GeminiError
from codebase.backend.sessions import SessionStore
from codebase.backend.tutor import TutorService


REPO_ROOT = Path(__file__).resolve().parents[2]
SLIDE_DATA = (
    REPO_ROOT
    / "data"
    / "vlearn-pack"
    / "processed"
    / "slide_chunks.jsonl"
)
load_dotenv(REPO_ROOT / ".env")
retriever = SlideRetriever(SLIDE_DATA)
sessions = SessionStore()
gemini_model = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash").strip()
gemini_fallback_model = os.environ.get(
    "GEMINI_FALLBACK_MODEL",
    "gemini-3.5-flash-lite",
).strip()
gemini_api_key = os.environ.get("GEMINI_API_KEY", "").strip()
gemini_client = (
    FallbackGeminiClient(
        primary=GeminiClient(api_key=gemini_api_key, model=gemini_model),
        fallback=GeminiClient(
            api_key=gemini_api_key,
            model=gemini_fallback_model,
        ),
    )
    if gemini_api_key
    else None
)
tutor = TutorService(retriever=retriever, client=gemini_client)


class TutorAPIHandler(BaseHTTPRequestHandler):
    server_version = "VLearnTutor/0.1"

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"[api] {self.address_string()} - {fmt % args}")

    def _send(
        self,
        status: HTTPStatus,
        payload: dict[str, object],
    ) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict[str, object] | None:
        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(length)
            payload = json.loads(raw_body.decode("utf-8-sig") if raw_body else "{}")
            if not isinstance(payload, dict):
                raise ValueError
            return payload
        except (ValueError, json.JSONDecodeError):
            self._send(
                HTTPStatus.BAD_REQUEST,
                {"error": {"code": "invalid_json", "message": "Body must be a JSON object."}},
            )
            return None

    def do_OPTIONS(self) -> None:
        self._send(HTTPStatus.NO_CONTENT, {})

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/health":
            self._send(
                HTTPStatus.OK,
                {
                    "status": "ok",
                    "service": "vlearn-tutor-api",
                    "slide_chunks": len(retriever.chunks),
                    "ai_provider": "gemini" if gemini_client else "not_configured",
                    "ai_model": gemini_model if gemini_client else None,
                    "ai_fallback_model": (
                        gemini_fallback_model if gemini_client else None
                    ),
                },
            )
            return

        if path == "/api/slides":
            self._send(
                HTTPStatus.OK,
                {
                    "count": len(retriever.chunks),
                    "slides": [
                        {
                            "chunk_id": chunk["chunk_id"],
                            "document_id": chunk["document_id"],
                            "document_title": chunk["document_title"],
                            "page": chunk["page"],
                            "page_title": chunk["page_title"],
                            "citation": chunk["citation"],
                            "content": chunk["content"],
                        }
                        for chunk in retriever.chunks
                    ],
                },
            )
            return

        if path.startswith("/api/sessions/"):
            session_id = path.removeprefix("/api/sessions/")
            session = sessions.get(session_id)
            if not session:
                self._send(
                    HTTPStatus.NOT_FOUND,
                    {"error": {"code": "session_not_found", "message": "Session not found."}},
                )
                return
            self._send(HTTPStatus.OK, {"session": session.to_dict()})
            return

        self._not_found()

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        payload = self._read_json()
        if payload is None:
            return

        if path == "/api/sessions":
            initial_level = str(payload.get("initial_level", "coban"))
            try:
                session = sessions.create(initial_level)
            except ValueError as exc:
                self._validation_error(str(exc))
                return
            self._send(HTTPStatus.CREATED, {"session": session.to_dict()})
            return

        if path == "/api/slides/search":
            query = str(payload.get("query", "")).strip()
            if not query:
                self._validation_error("query is required")
                return
            limit = payload.get("limit", 4)
            if not isinstance(limit, int) or not 1 <= limit <= 10:
                self._validation_error("limit must be an integer from 1 to 10")
                return
            document_id = payload.get("document_id")
            if document_id not in {None, "D1", "D2"}:
                self._validation_error("document_id must be D1 or D2")
                return
            results = retriever.search(query, limit, document_id)
            self._send(
                HTTPStatus.OK,
                {
                    "query": query,
                    "count": len(results),
                    "results": [result.to_dict() for result in results],
                },
            )
            return

        if path == "/api/chat":
            self._handle_chat(payload)
            return

        self._not_found()

    def do_PATCH(self) -> None:
        path = urlparse(self.path).path
        payload = self._read_json()
        if payload is None:
            return

        if path.startswith("/api/sessions/"):
            session_id = path.removeprefix("/api/sessions/")
            level = str(payload.get("level", ""))
            try:
                session = sessions.set_level(session_id, level)
            except ValueError as exc:
                self._validation_error(str(exc))
                return
            if not session:
                self._send(
                    HTTPStatus.NOT_FOUND,
                    {"error": {"code": "session_not_found", "message": "Session not found."}},
                )
                return
            self._send(HTTPStatus.OK, {"session": session.to_dict()})
            return

        self._not_found()

    def _handle_chat(self, payload: dict[str, object]) -> None:
        query = str(payload.get("message", "")).strip()
        session_id = str(payload.get("session_id", "")).strip()
        if not query or not session_id:
            self._validation_error("message and session_id are required")
            return
        session = sessions.get(session_id)
        if not session:
            self._send(
                HTTPStatus.NOT_FOUND,
                {"error": {"code": "session_not_found", "message": "Session not found."}},
            )
            return

        try:
            result = tutor.answer(query, session.level)
        except GeminiError as exc:
            print(f"[gemini] {exc}")
            self._send(
                HTTPStatus.BAD_GATEWAY,
                {
                    "error": {
                        "code": "ai_service_error",
                        "message": "Dịch vụ AI đang lỗi hoặc chưa sẵn sàng. Hãy thử lại.",
                    }
                },
            )
            return
        self._send(
            HTTPStatus.OK,
            {
                **result.to_dict(),
                "message": query,
                "session": session.to_dict(),
            },
        )

    def _validation_error(self, message: str) -> None:
        self._send(
            HTTPStatus.UNPROCESSABLE_ENTITY,
            {"error": {"code": "validation_error", "message": message}},
        )

    def _not_found(self) -> None:
        self._send(
            HTTPStatus.NOT_FOUND,
            {"error": {"code": "not_found", "message": "Endpoint not found."}},
        )


def run(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), TutorAPIHandler)
    print(f"VLearn Tutor API listening on http://{host}:{port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    run()
