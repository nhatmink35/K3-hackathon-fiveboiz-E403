# VLearn AI Tutor — MVP Prototype

## Mô tả

Prototype AI Tutor cải tiến cho nền tảng VLearn, hỗ trợ học viên ôn tập kiến thức theo quy trình:

```
Mở chatbot → Chọn mức độ → 5 câu hỏi gợi ý → Hỏi/đáp AI kèm trích dẫn → Quiz → Kết quả + Tài liệu cần ôn
```

## Cấu trúc

```
codebase/
├── backend/
│   ├── main.py            # FastAPI server
│   ├── ai_agent.py        # AI Agent (Google Gemini)
│   ├── data_loader.py     # Parse transcript bài giảng
│   ├── requirements.txt   # Dependencies
│   ├── .env               # API key (KHÔNG commit)
│   └── .env.example       # Template
└── frontend/
    ├── index.html          # Trang chính
    ├── css/styles.css      # Styling
    └── js/app.js           # Logic tương tác
```

## Cách chạy

### 1. Cài đặt dependencies

```bash
cd codebase/backend
pip install -r requirements.txt
```

### 2. Cấu hình API key

```bash
# Tạo file .env trong codebase/backend/
cp .env.example .env
# Sửa GEMINI_API_KEY trong file .env
```

### 3. Chạy server

```bash
cd codebase/backend
python -m uvicorn main:app --reload --port 8000
```

### 4. Mở trình duyệt

Truy cập: http://localhost:8000

## Tech Stack

- **Backend:** Python FastAPI
- **AI:** Google Gemini 3.5 Flash (free tier)
- **Frontend:** HTML / CSS / JavaScript (thuần)
- **Data:** 6 transcript bài giảng bản sạch (~700 đoạn có mã trích dẫn)

## Lưu ý

- File `.env` chứa API key — KHÔNG commit lên repo
- Data trong `data/vlearn-pack/` chỉ dùng trong phạm vi hackathon
- Prototype mức **Working** — chạy end-to-end với data thật
- AI call thật ở quyết định trung tâm (sinh câu hỏi, trả lời, sinh quiz)
