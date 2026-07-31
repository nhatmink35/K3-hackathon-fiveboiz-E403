import os
import json
import asyncio
import sys
import urllib.request
from typing import List, Dict, Any

try:
    from google import genai
    USE_NEW_SDK = True
except ImportError:
    import google.generativeai as genai_old
    USE_NEW_SDK = False


def _log(message: str) -> None:
    """Write diagnostics without crashing on legacy Windows console encodings."""
    try:
        print(message, flush=True)
    except UnicodeEncodeError:
        encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
        safe_message = message.encode(encoding, errors="replace").decode(encoding)
        print(safe_message, flush=True)


class AITutor:
    def __init__(self, api_key: str = None):

        if not api_key:
            api_key = os.getenv("GEMINI_API_KEY", "")

        self.api_key = api_key
        self.fallback_api_key = os.getenv("GEMINI_FALLBACK_API_KEY", os.getenv("GEMINI_API_KEY_FALLBACK", self.api_key))
        self.claude_api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.claude_model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
        
        # Read model names with typo tolerance (GENMINI_ vs GEMINI_)
        self.fallback_model_name = os.getenv("GEMINI_FALLBACK_MODEL", os.getenv("GENMINI_FALLBACK_MODEL", "gemini-3.5-flash-lite"))
        if self.fallback_model_name.startswith("genmini"):
            self.fallback_model_name = self.fallback_model_name.replace("genmini", "gemini")

        self.primary_model_name = os.getenv("GEMINI_PRIMARY_MODEL", os.getenv("GEMINI_MODEL", "gemini-3.5-flash"))
        if self.primary_model_name.startswith("genmini"):
            self.primary_model_name = self.primary_model_name.replace("genmini", "gemini")

        if USE_NEW_SDK:
            self.client = genai.Client(api_key=self.api_key) if self.api_key else None
            self.fallback_client = genai.Client(api_key=self.fallback_api_key) if self.fallback_api_key else self.client
        else:
            if self.api_key:
                genai_old.configure(api_key=self.api_key)
                self.model = genai_old.GenerativeModel(self.primary_model_name)
                self.fallback_model = genai_old.GenerativeModel(self.fallback_model_name)

    async def _call_claude(self, prompt: str) -> str:
        """Call Anthropic Claude API via direct HTTP request"""
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.claude_api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        payload = {
            "model": self.claude_model,
            "max_tokens": 2048,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers)
        loop = asyncio.get_event_loop()
        
        def _execute():
            with urllib.request.urlopen(req, timeout=40) as resp:
                return resp.read()

        response_bytes = await loop.run_in_executor(None, _execute)
        data = json.loads(response_bytes.decode('utf-8'))
        
        if "content" in data and len(data["content"]) > 0:
            return data["content"][0]["text"]
        raise RuntimeError(f"Invalid Claude API response: {data}")

    async def _generate(self, prompt: str) -> str:
        """Generate content prioritizing Claude Code / Anthropic API, then falling back to Gemini"""
        # If Claude API Key is present, try Claude first!
        if self.claude_api_key:
            try:
                _log(f"[AITutor] Calling Claude API ({self.claude_model})...")
                return await self._call_claude(prompt)
            except Exception as claude_err:
                _log(f"[AITutor] Claude API error: {claude_err}. Falling back to Gemini...")

        # Try Primary Gemini Model & Alternatives
        models_to_try = [
            self.primary_model_name,      # gemini-3.5-flash
            self.fallback_model_name,     # gemini-3.5-flash-lite
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-1.5-flash",
            "gemini-1.5-flash-lite"
        ]
        
        # Deduplicate while preserving order
        seen = set()
        models_to_try = [m for m in models_to_try if not (m in seen or seen.add(m))]

        last_exception = None

        for model_name in models_to_try:
            try:
                if USE_NEW_SDK:
                    if not self.client:
                        continue
                    response = self.client.models.generate_content(
                        model=model_name,
                        contents=prompt
                    )
                    return response.text
                else:
                    model_obj = genai_old.GenerativeModel(model_name)
                    response = await model_obj.generate_content_async(prompt)
                    return response.text
            except Exception as err:
                last_exception = err
                err_str = str(err)
                _log(f"[AITutor] Model '{model_name}' error: {err_str[:120]}")
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "Quota" in err_str:
                    _log("[AITutor] Rate limit hit. Waiting 1.5s before fallback...")
                    await asyncio.sleep(1.5)
                continue

        # Fallback to secondary API Key if available
        if self.fallback_api_key and self.fallback_api_key != self.api_key and USE_NEW_SDK and self.fallback_client:
            _log("[AITutor] Switching to secondary Gemini key...")
            try:
                response = self.fallback_client.models.generate_content(
                    model=self.fallback_model_name,
                    contents=prompt
                )
                return response.text
            except Exception as fb_err:
                _log(f"[AITutor] Secondary key error: {fb_err}")

        raise last_exception or RuntimeError("All LLM providers (Claude & Gemini) failed")

    def _parse_json(self, text: str) -> Any:
        """Extract and parse JSON from LLM response"""
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            parts = text.split("```")
            if len(parts) >= 3:
                text = parts[1]

        text = text.strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            for start_char, end_char in [('{', '}'), ('[', ']')]:
                start_idx = text.find(start_char)
                end_idx = text.rfind(end_char)
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    try:
                        return json.loads(text[start_idx:end_idx + 1])
                    except json.JSONDecodeError:
                        continue
            raise ValueError(f"Cannot parse JSON from: {text[:200]}")

    async def chat(self, message: str, context: str, level: str = None) -> Dict[str, Any]:
        msg_clean = message.strip().lower()
        
        # 1. Zero-Quota Greeting Interceptor for casual greetings
        greetings = ['hello', 'hi', 'chào', 'xin chào', 'alo', 'chao', 'helo', 'hey', 'start']
        if msg_clean in greetings or msg_clean.startswith('chào '):
            return {
                "answer": "Chào bạn! Mình là <b>VLearn AI Tutor</b>. Bạn có thắc mắc gì về nội dung bài giảng bên trái không? Bạn có thể bấm chọn câu hỏi gợi ý bên trên hoặc gõ câu hỏi cụ thể để mình hỗ trợ nhé! 😊",
                "citations": [],
                "badge": {"class": "badge-tutor", "label": "AI Tutor"},
                "is_out_of_scope": False
            }

        level_desc = {
            'coban': 'cơ bản — giải thích đơn giản, dùng ví dụ dễ hiểu',
            'thongthao': 'thông thạo — phân tích mối quan hệ, so sánh, ứng dụng',
            'nangcao': 'nâng cao — phân tích chuyên sâu, edge case, hạn chế'
        }
        level_text = level_desc.get(level, level_desc['coban'])

        prompt = f"""Bạn là AI Tutor trên VLearn. Trả lời câu hỏi của học viên bằng tiếng Việt.
CHỈ trả lời dựa trên nội dung transcript bài giảng bên dưới. Kèm trích dẫn [Căn cứ Txx-NNN] tương ứng.
Mức độ trả lời: {level_text}

4 quy tắc xử lý chỗ khó:
1. Nếu KHÔNG có thông tin trong tài liệu → nói rõ: "Nội dung này không có trong tài liệu bài giảng hiện tại. Mình chỉ hỗ trợ nội dung trong tài liệu đã cung cấp."
2. Nếu câu hỏi MƠ HỒ → hỏi lại để làm rõ: "Bạn muốn hỏi về phần nào cụ thể?"
3. Nếu NGOÀI PHẠM VI (làm bài hộ, cá nhân, không liên quan) → từ chối khéo + gợi ý chủ đề liên quan
4. Nếu phát hiện HIỂU SAI kiến thức → sửa lại kèm trích dẫn nguồn

Trả về JSON (KHÔNG thêm text ngoài JSON):
{{"answer": "câu trả lời HTML", "citations": ["T01-001", ...], "badge": {{"class": "badge-coban", "label": "Cơ bản"}}, "is_out_of_scope": false}}

=== NỘI DUNG BÀI GIẢNG ===
{context[:8000]}

=== CÂU HỎI HỌC VIÊN ===
{message}"""

        try:
            text = await self._generate(prompt)
            result = self._parse_json(text)
            return result
        except Exception as e:
            err_str = str(e)
            _log(f"[AITutor] Chat error: {err_str}")
            
            # Smart Offline RAG Fallback when Quota 429 is hit
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "Quota" in err_str:
                return {
                    "answer": "⚠️ <b>Hạn mức API Key hiện tại đã chạm giới hạn (Quota 429).</b><br>Bạn có thể dán <code>ANTHROPIC_API_KEY</code> hoặc <code>GEMINI_API_KEY</code> mới vào file <code>.env</code>.<br><br>📖 <b>Nội dung tham khảo bài giảng:</b> Theo giảng viên [T01-001], kỹ năng quan trọng nhất khi đưa AI vào doanh nghiệp là khả năng xác định ra bài toán từ các yêu cầu mơ hồ.",
                    "citations": ["T01-001"],
                    "badge": {"class": "badge-test", "label": "Thông báo Hạn mức"},
                    "is_out_of_scope": False
                }
                
            return {
                "answer": "Xin lỗi, đã có lỗi khi xử lý câu hỏi. Vui lòng thử lại sau giây lát.",
                "citations": [],
                "badge": {"class": "badge-tutor", "label": "AI Tutor"},
                "is_out_of_scope": False
            }

    async def suggest_questions(self, context: str, level: str) -> List[str]:
        level_desc = {
            'coban': 'CƠ BẢN: câu hỏi định nghĩa, liệt kê, giải thích đơn giản (VD: "...là gì?", "Liệt kê...", "Định nghĩa...")',
            'thongthao': 'THÔNG THẠO: câu hỏi về mối quan hệ, so sánh, tại sao (VD: "Mối quan hệ giữa...?", "So sánh...", "Tại sao...?")',
            'nangcao': 'NÂNG CAO: câu hỏi phân tích, phản biện, edge case (VD: "Hạn chế của...?", "Nếu...thì sao?", "Khi nào...không đúng?")'
        }

        prompt = f"""Dựa trên nội dung bài giảng dưới đây, tạo đúng 5 câu hỏi tiếng Việt cho mức {level_desc.get(level, level_desc['coban'])}.

Trả về JSON array (KHÔNG thêm text ngoài JSON):
["Câu hỏi 1?", "Câu hỏi 2?", "Câu hỏi 3?", "Câu hỏi 4?", "Câu hỏi 5?"]

=== NỘI DUNG BÀI GIẢNG ===
{context[:6000]}"""

        try:
            text = await self._generate(prompt)
            result = self._parse_json(text)
            if isinstance(result, list):
                return result[:5]
            return ["Không thể tạo câu hỏi gợi ý. Vui lòng thử lại."]
        except Exception as e:
            _log(f"[AITutor] Suggest error: {e}")
            return [
                "Kỹ năng xác định bài toán từ yêu cầu mơ hồ là gì?",
                "Product manager khác project manager như thế nào?",
                "Tại sao 70% việc đưa AI vào doanh nghiệp đến từ con người?",
                "Chi phí chuyển đổi sản phẩm AI hiện nay thay đổi ra sao?",
                "Tư duy hệ thống 1 và hệ thống 2 khác nhau thế nào?"
            ]

    async def generate_quiz(self, context: str, level: str) -> Dict[str, Any]:
        prompt = f"""Dựa trên nội dung bài giảng, tạo 1 câu hỏi trắc nghiệm tiếng Việt mức {level}.
Câu hỏi phải kiểm tra hiểu biết thực sự, đáp án sai phải là lỗi hiểu nhầm phổ biến.

Trả về JSON (KHÔNG thêm text ngoài JSON):
{{"question": "Nội dung câu hỏi?", "options": ["Đáp án A", "Đáp án B", "Đáp án C", "Đáp án D"], "correct_index": 0, "slide_target": "Tên phần bài giảng liên quan", "slide_name": "Tên hiển thị", "feedback_wrong": "Giải thích tại sao sai + hướng dẫn ôn lại", "feedback_correct": "Giải thích tại sao đúng"}}

=== NỘI DUNG BÀI GIẢNG ===
{context[:6000]}"""

        try:
            text = await self._generate(prompt)
            result = self._parse_json(text)
            return result
        except Exception as e:
            _log(f"[AITutor] Quiz error: {e}")
            return {
                "question": "Theo nội dung bài giảng, kỹ năng nào được đánh giá là quan trọng nhất khi đưa AI vào doanh nghiệp?",
                "options": [
                    "Kỹ năng lập trình AI nâng cao",
                    "Kỹ năng xác định bài toán từ yêu cầu mơ hồ",
                    "Kỹ năng thiết kế giao diện người dùng",
                    "Kỹ năng quản lý dự án Agile"
                ],
                "correct_index": 1,
                "slide_target": "Kỹ năng xác định bài toán từ yêu cầu mơ hồ",
                "slide_name": "Xác định bài toán kinh doanh cho AI",
                "feedback_wrong": "Theo giảng viên [T01-001], kỹ năng quan trọng nhất là khả năng xác định ra bài toán từ yêu cầu mơ hồ — đây là vị trí đang rất thiếu trong thị trường.",
                "feedback_correct": "Chính xác! Giảng viên nhấn mạnh [T01-001] rằng đây là kỹ năng quan trọng nhất và đang rất thiếu trong thị trường AI."
            }
