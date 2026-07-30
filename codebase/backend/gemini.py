from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass


class GeminiError(RuntimeError):
    pass


@dataclass(frozen=True)
class GeminiResponse:
    data: dict[str, object]
    model: str
    usage: dict[str, object]


class GeminiClient:
    API_ROOT = "https://generativelanguage.googleapis.com/v1beta/models"

    def __init__(self, api_key: str, model: str, timeout_seconds: int = 45):
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds

    def generate_json(
        self,
        system_instruction: str,
        prompt: str,
        schema: dict[str, object],
    ) -> GeminiResponse:
        url = f"{self.API_ROOT}/{self.model}:generateContent"
        payload = {
            "system_instruction": {"parts": [{"text": system_instruction}]},
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 1200,
                "responseMimeType": "application/json",
                "responseSchema": schema,
            },
        }
        request = urllib.request.Request(
            url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "x-goog-api-key": self.api_key,
            },
            method="POST",
        )
        raw_response: dict[str, object] | None = None
        for attempt in range(2):
            try:
                with urllib.request.urlopen(
                    request,
                    timeout=self.timeout_seconds,
                ) as response:
                    raw_response = json.loads(response.read().decode("utf-8"))
                    break
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="replace")
                if exc.code in {429, 503} and attempt == 0:
                    retry_after = exc.headers.get("Retry-After")
                    delay = min(float(retry_after or 8), 30)
                    time.sleep(delay)
                    continue
                raise GeminiError(f"Gemini HTTP {exc.code}: {detail[:500]}") from exc
            except (urllib.error.URLError, TimeoutError) as exc:
                if attempt == 0:
                    time.sleep(2)
                    continue
                raise GeminiError(f"Gemini connection failed: {exc}") from exc

        if raw_response is None:
            raise GeminiError("Gemini request failed without a response")

        candidates = raw_response.get("candidates") or []
        if not candidates:
            feedback = raw_response.get("promptFeedback", {})
            raise GeminiError(f"Gemini returned no candidate: {feedback}")
        try:
            parts = candidates[0]["content"]["parts"]
            texts = [
                part["text"]
                for part in parts
                if isinstance(part, dict)
                and isinstance(part.get("text"), str)
                and not part.get("thought", False)
            ]
            parsed = self._parse_json_parts(texts)
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise GeminiError("Gemini returned an invalid structured response") from exc
        if not isinstance(parsed, dict):
            raise GeminiError("Gemini structured response must be an object")

        return GeminiResponse(
            data=parsed,
            model=self.model,
            usage=raw_response.get("usageMetadata", {}),
        )

    @staticmethod
    def _parse_json_parts(texts: list[str]) -> dict[str, object]:
        for text in reversed(texts):
            candidate = text.strip()
            if candidate.startswith("```"):
                candidate = candidate.removeprefix("```json").removeprefix("```")
                candidate = candidate.removesuffix("```").strip()
            try:
                parsed = json.loads(candidate)
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, dict):
                return parsed

        combined = "".join(texts).strip()
        parsed = json.loads(combined)
        if not isinstance(parsed, dict):
            raise json.JSONDecodeError("Expected object", combined, 0)
        return parsed


class FallbackGeminiClient:
    """Try the flagship model first, then a configured lower-quota fallback."""

    def __init__(self, primary: GeminiClient, fallback: GeminiClient):
        self.primary = primary
        self.fallback = fallback
        self.model = primary.model

    def generate_json(
        self,
        system_instruction: str,
        prompt: str,
        schema: dict[str, object],
    ) -> GeminiResponse:
        try:
            return self.primary.generate_json(system_instruction, prompt, schema)
        except GeminiError as exc:
            message = str(exc)
            retryable = any(
                marker in message
                for marker in ("HTTP 429", "HTTP 503", "connection failed")
            )
            if not retryable:
                raise
            return self.fallback.generate_json(system_instruction, prompt, schema)
