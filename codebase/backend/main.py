import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

from data_loader import DataLoader
from ai_agent import AITutor

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
load_dotenv(os.path.join(project_root, '.env'), encoding='utf-8-sig')

# Initialize globals
data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'vlearn-pack', 'transcript')
data_loader = DataLoader(data_dir=data_dir)
ai_agent = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global ai_agent
    # Startup: Load all transcripts and initialize AITutor
    data_loader.load_all()
    api_key = os.getenv("GEMINI_API_KEY", os.getenv("GENMINI_API_KEY", ""))
    ai_agent = AITutor(api_key=api_key)
    print(f"[Startup] Loaded {len(data_loader.chunks)} chunks, {len(data_loader.slides)} slides")
    provider_status = "configured" if ai_agent.api_key else "not configured"
    print(f"[Startup] AI Tutor initialized; Gemini is {provider_status}")
    yield
    # Shutdown
    print("[Shutdown] Server stopping...")


app = FastAPI(title="VLearn AI Tutor MVP", lifespan=lifespan)

# Setup CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Pydantic models ---

class SuggestQuestionsRequest(BaseModel):
    level: str
    slide_ids: Optional[List[str]] = None


class ChatRequest(BaseModel):
    message: str
    level: Optional[str] = "coban"
    slide_ids: Optional[List[str]] = None


class GenerateQuizRequest(BaseModel):
    level: str
    slide_ids: Optional[List[str]] = None


LEVEL_INFO_MAP = {
    "coban": {"label": "Cơ bản", "badge_class": "badge-coban", "emoji": "🌱"},
    "thongthao": {"label": "Thông thạo", "badge_class": "badge-thongthao", "emoji": "🌿"},
    "nangcao": {"label": "Nâng cao", "badge_class": "badge-nangcao", "emoji": "🌳"}
}


# --- API Endpoints ---

@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "ai_configured": bool(ai_agent and ai_agent.api_key),
        "primary_model": ai_agent.primary_model_name if ai_agent else None,
        "fallback_model": ai_agent.fallback_model_name if ai_agent else None,
        "chunks": len(data_loader.chunks),
        "slides": len(data_loader.slides),
    }


@app.get("/api/slides")
async def get_slides():
    slides = data_loader.get_slides()
    return {"slides": slides}


@app.post("/api/suggest-questions")
async def suggest_questions(req: SuggestQuestionsRequest):
    context = data_loader.get_context_for_slides(req.slide_ids)
    questions = await ai_agent.suggest_questions(context=context, level=req.level)
    level_info = LEVEL_INFO_MAP.get(req.level, LEVEL_INFO_MAP["coban"])
    return {
        "questions": questions,
        "level_info": level_info
    }


@app.post("/api/chat")
async def chat(req: ChatRequest):
    context = data_loader.get_context_for_slides(req.slide_ids)
    response = await ai_agent.chat(message=req.message, context=context, level=req.level)

    # Fill in badge information if it was missing from the AI response
    if "badge" not in response or not response["badge"]:
        level_info = LEVEL_INFO_MAP.get(req.level, LEVEL_INFO_MAP["coban"])
        response["badge"] = {"class": level_info["badge_class"], "label": level_info["label"]}

    return response


@app.post("/api/generate-quiz")
async def generate_quiz(req: GenerateQuizRequest):
    context = data_loader.get_context_for_slides(req.slide_ids)
    quiz_data = await ai_agent.generate_quiz(context=context, level=req.level)
    return quiz_data


# --- Serve frontend static files ---

frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend')
frontend_dir = os.path.abspath(frontend_dir)

# Mount CSS and JS subdirectories
css_dir = os.path.join(frontend_dir, 'css')
js_dir = os.path.join(frontend_dir, 'js')

if os.path.exists(css_dir):
    app.mount("/css", StaticFiles(directory=css_dir), name="css")

if os.path.exists(js_dir):
    app.mount("/js", StaticFiles(directory=js_dir), name="js")


@app.get("/")
async def serve_index():
    index_path = os.path.join(frontend_dir, 'index.html')
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    return HTMLResponse("<h1>Frontend not found. Place index.html in codebase/frontend/</h1>")
