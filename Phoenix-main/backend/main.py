import os
import shutil
import uuid
import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, File, Form, HTTPException, UploadFile, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import pypdf

from generator import (
    MultiProviderQuizGenerator,
    QuizGenerationRequest,
    QuizResult,
    QuizQuestion,
)

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("quizcrafter")

# Base directory paths
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
DATA_DIR = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "static"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)

HISTORY_FILE = DATA_DIR / "history.json"
if not HISTORY_FILE.exists():
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

app = FastAPI(
    title="QuizCrafter API",
    description="Full-stack AI Quiz Generator with PDF processing and multi-provider AI support",
    version="2.0.0"
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pre-defined sample topics with rich educational text
SAMPLE_TOPICS = [
    {
        "id": "story_time",
        "title": "Story Time",
        "category": "Story",
        "description": "The Hyderabad Express, an old watchmaker, and a seventh hand that only moves when a life is changed forever.",
        "text": """The rain over the Deccan plateau had a way of turning everything the color of wet slate.

At dusk, an ancient train—the Hyderabad Express—groaned along the curved rails heading north toward Kalaburagi. Inside the second-class compartment, a solitary brass trunk rested beneath the wooden berth, rattling in sync with the iron wheels. It belonged to an old watchmaker named Raghu, whose family had maintained the clock towers across Nizam territory for three generations.

In his pocket sat a pocket watch unlike any other. Its face wasn't marked with twelve hours, but seven concentric circles etched in silver. Each circle tracked a different rhythm: the pulse of a running horse, the breath of a sleeping leopard, the cycle of the monsoon winds, the rotation of Jupiter, the turning of the earth, the decay of iron, and, at the dead center, a hand that moved so slowly it appeared entirely frozen.

Raghu's grandfather had told him that the center hand only ticked forward when someone made a choice that permanently altered the weave of their life. For forty years, Raghu had carried it, watching young men leave for the cities, watching soldiers return from border skirmishes, watching monsoons fail and return. The seventh hand had never stirred.

As the train shuddered to a halt at an unlit crossing bordered by black soil and dry acacia trees, the coach lights flickered and died. The hum of the diesel engine dropped to a low, idling growl. Outside, a young runner carrying a lantern stepped onto the gravel track. He wore worn canvas shoes and carried an urgent dispatch pouch—an old telegram runner from the relay stations that still connected remote outposts where wires had snapped in the storm.

The youth leaped up into the doorway to escape the rising downpour, breathing in sharp, measured rhythms. He looked at the stalled train, then down at the pouch clutched in his fist, and finally back along the dark track winding into the hills.

"If I wait for the signals to clear, the crossing bridge at Bhima river will flood before midnight," the runner said, half to himself, his voice cutting through the damp chill. "If I go on foot through the scrub, I might cut three miles, but the ravine is pure mud."

Raghu pulled out the silver watch. In the dim glow of the lantern, the silver dials caught the rain-slicked darkness.

"The mud will take your shoes," Raghu said quietly. "And you will run blind in the acacia."

The youth glanced at the train, safe and dry, waiting on iron that would eventually move. Then he looked at the open wilderness, gripped the strap across his chest, tightened his jaw, and vaulted back down into the stinging rain without looking back. His silhouette vanished into the scrub, his stride opening into an effortless, punishing sprint.

Raghu looked down at his palm. Deep within the brass housing, a faint, metallic *click* resonated through the casing.

The seventh hand had moved."""
    }
]


# Pydantic Schemas
class PDFUploadResponse(BaseModel):
    filename: str
    file_id: str
    page_count: int
    word_count: int
    char_count: int
    preview: str
    extracted_text: str

class QuizSubmission(BaseModel):
    quiz_id: str
    topic: str
    score: int
    total_questions: int
    answers: Dict[str, str]  # question_id -> selected_letter
    percentage: float
    time_spent_seconds: Optional[int] = 0

class ExportRequest(BaseModel):
    title: str
    topic: str
    difficulty: str
    score: Optional[int] = None
    total: Optional[int] = None
    questions: List[Dict[str, Any]]
    user_answers: Optional[Dict[str, str]] = None


# Endpoints

@app.get("/api/health")
async def health_check():
    """Returns system status, active providers, and feature capabilities."""
    ollama_online = False
    try:
        import httpx
        async with httpx.AsyncClient(timeout=1.0) as client:
            res = await client.get("http://localhost:11434/api/version")
            if res.status_code == 200:
                ollama_online = True
    except Exception:
        ollama_online = False

    return {
        "status": "healthy",
        "version": "2.0.0",
        "providers": {
            "offline": {
                "name": "Built-in Smart Offline NLP Engine",
                "available": True,
                "requires_key": False
            },
            "ollama": {
                "name": "Local Ollama LLM",
                "available": ollama_online,
                "requires_key": False,
                "default_url": "http://localhost:11434"
            },
            "gemini": {
                "name": "Google Gemini",
                "available": bool(os.getenv("GEMINI_API_KEY")),
                "requires_key": True
            },
            "openai": {
                "name": "OpenAI / Compatible",
                "available": bool(os.getenv("OPENAI_API_KEY")),
                "requires_key": True
            }
        }
    }


@app.get("/api/sample-topics")
async def get_sample_topics():
    """Returns curated educational sample materials for 1-click test and study."""
    return SAMPLE_TOPICS


@app.post("/api/upload", response_model=PDFUploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """
    Accepts PDF upload, parses document text with pypdf,
    extracts metadata (pages, word count, character count, preview).
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF document (.pdf).")

    file_id = str(uuid.uuid4())[:8]
    safe_name = f"{file_id}_{file.filename}"
    saved_path = UPLOAD_DIR / safe_name

    try:
        # Save uploaded file
        with open(saved_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract text using pypdf
        reader = pypdf.PdfReader(str(saved_path))
        page_count = len(reader.pages)
        
        extracted_pages = []
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            extracted_pages.append(page_text)

        full_text = "\n\n".join(extracted_pages).strip()

        if not full_text:
            raise HTTPException(
                status_code=422,
                detail="Could not extract text from this PDF. It may be scanned or image-based. Try another PDF or paste text directly."
            )

        words = full_text.split()
        word_count = len(words)
        char_count = len(full_text)
        preview = full_text[:600] + ("..." if len(full_text) > 600 else "")

        return PDFUploadResponse(
            filename=file.filename,
            file_id=file_id,
            page_count=page_count,
            word_count=word_count,
            char_count=char_count,
            preview=preview,
            extracted_text=full_text
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing PDF upload: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")


@app.post("/api/generate", response_model=QuizResult)
async def generate_quiz(payload: QuizGenerationRequest):
    """
    Generates a structured multiple-choice quiz using the requested provider
    (Offline NLP, Ollama, Gemini, or OpenAI) with difficulty and question count controls.
    """
    try:
        result = await MultiProviderQuizGenerator.generate_quiz(payload)
        return result
    except Exception as e:
        logger.error(f"Error generating quiz: {e}")
        raise HTTPException(status_code=500, detail=f"Quiz generation error: {str(e)}")


# Legacy compatibility endpoint so older frontends or scripts continue to work
@app.post("/upload/")
async def legacy_upload(file: UploadFile = File(...)):
    res = await upload_pdf(file)
    # Also save as book.pdf for backwards compatibility
    legacy_file = UPLOAD_DIR / "book.pdf"
    with open(legacy_file, "w", encoding="utf-8") as f:
        f.write(res.extracted_text)
    return {"message": "File uploaded successfully", "pages": res.page_count}


@app.post("/generate-questions/")
async def legacy_generate(topic: str = Form(...)):
    legacy_file = UPLOAD_DIR / "book.pdf"
    content = ""
    if legacy_file.exists():
        with open(legacy_file, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

    req = QuizGenerationRequest(
        topic=topic,
        content=content,
        num_questions=5,
        difficulty="Medium",
        provider="auto"
    )
    result = await MultiProviderQuizGenerator.generate_quiz(req)

    # Convert to legacy response format
    formatted = []
    for q in result.questions:
        formatted.append({
            "question": q.question,
            "answers": [
                {
                    "text": opt,
                    "correct": opt.startswith(q.correct_answer)
                }
                for opt in q.options
            ],
            "explanation": q.explanation
        })
    return formatted


@app.post("/api/save-result")
async def save_quiz_result(submission: QuizSubmission):
    """Saves quiz score and answers to persistent local history."""
    try:
        history = []
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)

        item = submission.model_dump()
        item["timestamp"] = int(Path().stat().st_mtime) if False else None
        history.insert(0, item)
        # Keep last 50 entries
        history = history[:50]

        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)

        return {"status": "saved", "total_records": len(history)}
    except Exception as e:
        logger.warning(f"Failed to save quiz history: {e}")
        return {"status": "error", "detail": str(e)}


@app.get("/api/history")
async def get_quiz_history():
    """Retrieves previous quiz sessions and performance analytics."""
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


@app.post("/api/export")
async def export_quiz_markdown(payload: ExportRequest):
    """Exports quiz and user score as a formatted Markdown or text document."""
    lines = [
        f"# 📝 {payload.title}",
        f"**Topic:** {payload.topic} | **Difficulty:** {payload.difficulty}",
    ]
    if payload.score is not None and payload.total is not None:
        pct = round((payload.score / payload.total) * 100, 1)
        lines.append(f"**Score:** {payload.score}/{payload.total} ({pct}%)\n")
    lines.append("---\n")

    for i, q in enumerate(payload.questions, 1):
        q_id = str(q.get("id", i))
        user_choice = payload.user_answers.get(q_id) if payload.user_answers else None
        correct = q.get("correct_answer", "")

        lines.append(f"### Question {i}: {q.get('question')}\n")
        for opt in q.get("options", []):
            is_user = user_choice and opt.startswith(user_choice)
            is_correct = opt.startswith(correct)
            prefix = "[ ] "
            if is_user and is_correct:
                prefix = "[x] (Correct) "
            elif is_user:
                prefix = "[x] (Your choice) "
            elif is_correct:
                prefix = "[ ] (Correct Answer) "
            lines.append(f"- {prefix}{opt}")

        if q.get("explanation"):
            lines.append(f"\n> **Explanation:** {q.get('explanation')}\n")
        lines.append("")

    return {"markdown": "\n".join(lines)}


# Serve single-page frontend application
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @app.get("/")
    async def serve_index():
        index_file = STATIC_DIR / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return {"message": "QuizCrafter API running. Web interface file not found in static directory."}
