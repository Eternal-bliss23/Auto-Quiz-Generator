# 🔥 Phoenix — AI-Powered Interactive Quiz Generator

**Phoenix** (formerly *QuizCrafter*) turns PDFs, study notes, or any academic text into **engaging, interactive multiple-choice quizzes** with instant score evaluation and detailed answer explanations.

---

## ✨ Features

- **Multiple Input Formats**
  - **PDF Upload** — parses documents with `pypdf`, extracts text, counts pages and words.
  - **Direct Text Input** — paste lecture notes, study summaries, or textbook paragraphs.
  - **Sample Story** — a single curated sample ("Story Time") for one-click testing.
- **Universal Multi-Provider AI Support**
  - **Built-in Smart Offline NLP Engine** — generates quizzes with **zero setup or API keys**.
  - **Local Ollama** — connects to `http://localhost:11434` (Llama 3.2, Mistral, Gemma 2).
  - **Google Gemini** — fast generation via Gemini Flash.
  - **OpenAI / Compatible** — GPT-4o-mini and OpenAI-compatible endpoints (Groq, OpenRouter).
- **Interactive Quiz Player**
  - Countdown timer, question navigation map, instant or exam feedback.
  - Detailed educational explanations for every question.
- **Results & Analytics Dashboard**
  - Accuracy percentage, score badge, filter by correct/mistakes, retake quiz.
  - **Export** formatted Markdown reports.
  - **Local session history** of past attempts.
- **Dual-Frontend Architecture**
  - **Integrated Web App** — served directly by FastAPI at `http://localhost:8000` (pure Python, works out of the box).
  - **React Dev Client** — Vite + Tailwind + Axios in `frontend/`.

---

## 🎯 Importance

- **Saves time** — creates quizzes from existing material in seconds instead of hours of manual work.
- **Promotes active learning** — turns passive reading into retrieval practice, one of the most effective study techniques.
- **Instant feedback loop** — immediate scoring and explanations reinforce understanding and correct misconceptions.
- **Democratizes AI in education** — works with **zero cost and zero setup** via the offline engine, so anyone can use it.
- **Bridges the gap** — connects static study material (PDFs/notes) to interactive, engaging assessments.
- **Supports self-paced learning** — learners generate unlimited practice quizzes on any topic, anytime.
- **Privacy-conscious** — runs locally; study material never has to leave the user's machine.

---

## 💡 Benefits

### 👨‍🎓 For Students
- Generate unlimited practice quizzes from lecture notes, textbooks, or PDFs.
- Learn faster with instant feedback and detailed answer explanations.
- Track progress with scores, accuracy, and attempt history.
- Prepare for exams anytime — **completely free**.

### 👩‍🏫 For Educators
- Cut quiz-creation time from hours to minutes.
- Produce quick formative assessments and revision material.
- Reuse and regenerate quizzes at different difficulty levels.

### 🏫 For Institutions & Organizations
- **Cost-effective** — no licensing fees (MIT licensed), optional zero-cost offline mode.
- **Scalable** — deploy locally or on a small server for a classroom.
- **No vendor lock-in** — swap AI providers freely (Offline, Ollama, Gemini, OpenAI).
- **Privacy-friendly** — data can stay on-premises.

### 👨‍💻 For Developers
- Modular, readable codebase (FastAPI + optional React).
- Multi-provider abstraction for easy extension.
- Simple setup and `--reload` development workflow.

### ⚙️ Technical & Operational Benefits
- **Offline-first** — no internet or API keys required.
- **Cross-platform** — Windows, macOS, Linux.
- **One-command launch** — minimal training needed.
- **Flexible AI** — choose speed (offline), privacy (Ollama), or quality (Cloud LLMs).

### 🏆 Benefit Summary (for slides)

| Stakeholder | Key Benefit |
|---|---|
| Students | Free unlimited practice + instant feedback |
| Educators | Massive time savings on quiz creation |
| Institutions | Cost-effective, scalable, privacy-preserving |
| Developers | Modular, extensible, multi-provider |

---

## 🎨 Customizations (Phoenix Edition)

| Change | Detail |
|---|---|
| **Rebrand** | Title, navbar, and tab name changed from *QuizCrafter* → **Phoenix**. |
| **Logo** | Thunderbolt emoji replaced with a custom image (`logo.jpg`). |
| **Theme** | Whole UI recolored to a **phoenix fire palette** — orange (`#ea580c`), red, amber. |
| **Sample Topics** | Old academic samples removed; replaced with the **"Story Time"** story. |
| **Quiz Topic field** | Removed. Topic is now auto-derived (sample title / PDF filename / "General Knowledge"). |

---

## 📁 Project Structure

```
Phoenix/
├── run.py                     # Launcher: starts FastAPI + opens browser
├── start.bat                  # Windows one-click launcher
├── backend/
│   ├── main.py                # FastAPI app, endpoints, sample data
│   ├── generator.py           # Multi-provider quiz generation engine
│   ├── requirements.txt       # Python dependencies
│   ├── data/                  # Saved quiz history (JSON)
│   ├── uploads/               # Uploaded PDFs
│   └── static/
│       ├── index.html         # Integrated web UI (Tailwind CSS)
│       └── logo.jpg           # Phoenix logo
└── frontend/                  # React + Vite dev client
    ├── src/App.jsx
    ├── src/QuizPage.jsx
    ├── public/logo.jpg
    └── package.json
```

---

## 🚀 Quick Start

### 1. Install backend dependencies
```bash
pip install -r backend/requirements.txt
```

### 2. Run the app
```bash
python run.py
```
Or double-click `start.bat` on Windows. The browser opens automatically at `http://localhost:8000`.

---

## 🛠️ Manual / Development

### Backend (FastAPI)
```bash
python -m uvicorn main:app --app-dir backend --reload --port 8000
```
> `--app-dir backend` is required because `main.py` imports `generator` from the backend folder. `--reload` auto-restarts on Python edits.

Run the API test suite:
```bash
python backend/test_api.py
```

### Frontend (React + Vite) — requires Node.js & npm
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173`.

---

## 📡 REST API

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check & AI provider availability |
| `GET` | `/api/sample-topics` | Curated sample materials |
| `POST` | `/api/upload` | Upload PDF, extract text + metadata |
| `POST` | `/api/generate` | Generate quiz questions |
| `POST` | `/api/save-result` | Save score and answer history |
| `GET` | `/api/history` | Retrieve previous quiz sessions |
| `POST` | `/api/export` | Export quiz as Markdown |

---

## ⚙️ AI Engine Settings

Open the **Settings (⚙️)** icon in the top navigation to configure:
- **Local Ollama URL** (default `http://localhost:11434`)
- **Google Gemini API Key**
- **OpenAI API Key**

If no keys or local LLMs are available, Phoenix falls back to its **built-in Offline NLP Generator** automatically.

---

## 📊 Feasibility Study

An assessment of whether Phoenix is practical to build, deploy, and sustain.

### 1. Technical Feasibility — ✅ High
- **Stack maturity**: Built on FastAPI + Uvicorn (Python) and optionally React + Vite — all battle-tested, well-documented frameworks.
- **Zero-dependency AI option**: The built-in **Offline NLP Engine** generates quizzes with **no API key, no GPU, and no internet**, removing the biggest technical blocker.
- **Optional LLM integration**: Supports Ollama (local) and Gemini/OpenAI (cloud) through a single `MultiProviderQuizGenerator` abstraction, so providers can be swapped without code changes.
- **PDF parsing**: `pypdf` handles text-based PDFs reliably. *Limitation:* scanned/image PDFs require OCR (not included) — a known constraint.
- **Hardware**: Runs on a standard laptop (Windows/macOS/Linux). No specialized hardware needed.
- **Verdict**: Technically straightforward and proven for a single-user / small-group use case.

### 2. Economic Feasibility — ✅ High
- **Licensing**: MIT — free to use, modify, and distribute.
- **Cost with offline engine**: **₹0 / $0** — fully local generation.
- **Cost with Ollama**: **$0** after one-time local model download.
- **Cost with cloud LLMs**: Pay-as-you-go only when used (Gemini/OpenAI tokens). Quiz generation per request costs a fraction of a cent.
- **Infrastructure**: No server hosting required — runs on `localhost`. Optional hosting is cheap (a small VM or free tier).
- **Development cost**: Small codebase, single developer, short build cycle.
- **Verdict**: Highly economical; scales from free to negligible cost.

### 3. Operational Feasibility — ✅ High
- **Ease of use**: One command (`python run.py`) or double-click `start.bat`; browser opens automatically.
- **No training required**: Clean tabbed UI (Upload PDF / Paste Text / Sample Story) with a single "Generate Quiz" action.
- **Zero-config default**: Works immediately with the offline engine; advanced users can add keys via the ⚙️ Settings.
- **Maintenance**: Auto-reload (`--reload`) for development; modular files make updates easy.
- **Verdict**: Operable by non-technical end users with minimal guidance.

### 4. Legal & Ethical Feasibility — ⚠️ Moderate (manageable)
- **Data privacy**: Uploaded files and history are stored **locally** (`backend/uploads`, `backend/data`) — no third-party exposure unless a cloud LLM is chosen.
- **Copyright**: Users must have rights to the material they upload; the tool should not be used to redistribute copyrighted content.
- **AI accuracy**: LLM-generated questions/explanations may contain errors (hallucinations) — outputs should be reviewed.
- **Academic integrity**: Intended as a *study aid*, not for cheating; institutions may have usage policies.
- **Verdict**: Feasible with clear usage guidelines; no blocking legal issues.

### 5. Schedule / Time Feasibility — ✅ High
- **Small scope**: ~7 Python dependencies, a single-page integrated UI, and an optional React client.
- **Fast setup**: Dependency install + first run in under 5 minutes.
- **Incremental delivery**: Core quiz flow works without any AI keys, so an MVP is available immediately.
- **Verdict**: Deliverable within days, not months.

### 6. Performance & Scalability Feasibility — ⚠️ Moderate
- **Latency**: Offline engine = near-instant; local Ollama = seconds; cloud LLMs = depends on network/rate limits.
- **Concurrency**: Designed for **single-user / classroom-scale** use. High concurrent load would need a production ASGI setup (workers, reverse proxy) and a shared datastore instead of local JSON.
- **Storage**: JSON history is fine for personal use; a database would be needed at scale.
- **Verdict**: Excellent for personal/small-group use; moderate effort to scale to multi-tenant production.

### 7. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Cloud LLM outage / rate limit | Medium | Medium | Automatic fallback to Offline Engine |
| API key leakage | Low | High | Keys stored in `localStorage`/env vars; never committed |
| Scanned PDFs not parsed | Medium | Low | Document limitation; add OCR (e.g., Tesseract) later |
| Inaccurate AI answers | Medium | Medium | Show explanations; allow manual review |
| Port 8000 already in use | Medium | Low | Stop conflicting process / change `--port` |

### 8. Feasibility Summary

| Dimension | Rating |
|---|---|
| Technical | ✅ High |
| Economic | ✅ High |
| Operational | ✅ High |
| Legal / Ethical | ⚠️ Moderate |
| Schedule | ✅ High |
| Performance / Scalability | ⚠️ Moderate |
| **Overall** | **✅ Feasible** |

**Conclusion:** Phoenix is **highly feasible** as a locally-run, AI-powered study tool. Its offline-first design removes cost and infrastructure barriers, while optional LLM providers add flexibility. The main constraints — scanned-PDF support, large-scale concurrency, and AI-answer accuracy — are documented limitations addressable in future iterations.

---

## 🚀 Future Enhancements
- OCR support for scanned/image-based PDFs.
- Multi-format export (PDF, DOCX, CSV).
- User accounts and a proper database for multi-user deployments.
- Spaced-repetition and adaptive difficulty based on past performance.
- Additional question types (true/false, fill-in-the-blank, short answer).

---

## 📄 License

MIT License.
