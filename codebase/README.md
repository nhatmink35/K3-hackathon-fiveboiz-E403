# VLearn AI Tutor — Hướng dẫn chạy web

## 1. Yêu cầu

- Python 3.10 trở lên.
- Gemini API key.
- Thư mục dữ liệu transcript nằm tại:

```text
data/vlearn-pack/transcript/
├── transcript-01-clean.md
├── transcript-02-clean.md
├── transcript-03-clean.md
├── transcript-04-clean.md
├── transcript-05-clean.md
└── transcript-06-clean.md
```

`data/vlearn-pack/` không được đưa lên GitHub. Khi clone repo sang máy mới, cần
chép data pack vào đúng đường dẫn trên trước khi chạy.

## 2. Cài dependency

Mở PowerShell tại thư mục gốc của repo:

```powershell
cd codebase\backend
python -m pip install -r requirements.txt
```

## 3. Cấu hình Gemini

Tạo file `.env` tại **thư mục gốc của repo**, cùng cấp với `spec.md`:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.5-flash
GEMINI_FALLBACK_MODEL=gemini-3.5-flash-lite
```

Không commit file `.env` hoặc API key lên GitHub.

## 4. Chạy web

Từ thư mục `codebase/backend`:

```powershell
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Mở trình duyệt tại:

```text
http://127.0.0.1:8000
```

Trong môi trường phát triển, có thể bật tự động tải lại:

```powershell
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

## 5. Kiểm tra hệ thống

Health check:

```text
http://127.0.0.1:8000/api/health
```

Kết quả bình thường có dạng:

```json
{
  "status": "ok",
  "ai_configured": true,
  "primary_model": "gemini-3.5-flash",
  "fallback_model": "gemini-3.5-flash-lite",
  "chunks": 700,
  "slides": 98
}
```

Nếu `ai_configured` là `false`, kiểm tra lại vị trí file `.env` và
`GEMINI_API_KEY`.

Nếu `chunks` hoặc `slides` bằng `0`, kiểm tra lại thư mục
`data/vlearn-pack/transcript/`.

## 6. Chạy test

Từ thư mục `codebase/backend`:

```powershell
python -m unittest test_backend test_data_loader -v
node --check ..\frontend\js\app.js
```

Lệnh kiểm tra JavaScript yêu cầu Node.js. Nếu máy không có Node.js, có thể bỏ qua
lệnh này; web vẫn chạy bằng Python.

## 7. Các API chính

- `GET /api/health`: kiểm tra server, AI và data.
- `GET /api/slides`: tải nội dung bài giảng.
- `POST /api/suggest-questions`: sinh 5 câu hỏi theo mức.
- `POST /api/chat`: trả lời câu hỏi tự nhập kèm citation.
- `POST /api/generate-quiz`: sinh một câu quiz theo mức.

## 8. Lỗi thường gặp

### Cổng 8000 đang được sử dụng

Chạy bằng cổng khác:

```powershell
python -m uvicorn main:app --host 127.0.0.1 --port 8001
```

Sau đó mở `http://127.0.0.1:8001`.

### Gemini báo quota 429

Backend sẽ thử model dự phòng. Nếu cả hai model đều hết quota, chờ quota được
reset hoặc thay API key hợp lệ trong `.env`, rồi khởi động lại server.

### Web mở được nhưng agent không trả lời

Kiểm tra lần lượt:

1. `/api/health` có `status: "ok"` và `ai_configured: true`.
2. Terminal chạy backend có lỗi quota, kết nối hoặc model hay không.
3. Data transcript đã nằm đúng đường dẫn.
4. Sau khi sửa `.env`, đã khởi động lại backend.
