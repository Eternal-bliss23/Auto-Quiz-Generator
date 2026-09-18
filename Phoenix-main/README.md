# 🚀 QuizCrafter: AI-Powered Interactive Quiz Generator 🤖📚

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC.svg)](https://tailwindcss.com/)

**QuizCrafter** transforms PDFs, study notes, and educational materials into **engaging, interactive multiple-choice quizzes** with real-time scoring, countdown timers, and comprehensive answer explanations!

---

## 🌟 Key Highlights

- 🧠 **Universal Multi-Provider AI Support**:
  - **Zero-Setup Offline NLP Engine**: Works instantly out of the box with pure Python — no API keys or local LLM required!
  - **Local Ollama**: Connect directly to your local models (`llama3.2`, `mistral`, `gemma2`, `phi3`).
  - **Google Gemini**: High-speed, high-accuracy quiz synthesis with Gemini 1.5 & 2.0 Flash.
  - **OpenAI & Compatible Endpoints**: Compatible with GPT-4o, Groq, OpenRouter, and DeepSeek.
- 📄 **Smart Document Parsing**:
  - Automatically extracts text from uploaded PDF documents using `pypdf`.
  - Displays word counts, page numbers, and detected topics.
- ⏱️ **Interactive Quiz Player**:
  - Built-in countdown timer and quick question-map navigator.
  - Immediate review with detailed educational rationales for each option.
- 📊 **Analytics & Session History**:
  - Performance scoring (Mastery, Proficient, Needs Practice).
  - Review answered questions and filter mistakes.
  - Download formatted **Markdown Quiz Reports**.
  - Retain local quiz history across sessions.
- 💻 **Dual Frontend Architecture**:
  - **Integrated Web Interface**: Served directly by FastAPI at `http://localhost:8000` with dark mode support.
  - **Modern React Client**: Standalone Vite + Tailwind CSS application in `frontend/`.

---

## 🚀 Quick Start (One-Click)

### Option A: Run with Python (Recommended)
Clone the repository and run:
```bash
# 1. Clone your repository
git clone https://github.com/Eternal-bliss23/QuizCrafter.git
cd QuizCrafter

# 2. Install dependencies
pip install -r backend/requirements.txt

# 3. Launch application
python run.py
```
> On Windows, you can also just double-click **`start.bat`**!

Your default browser will automatically open to `http://localhost:8000`.

---

### Option B: React Frontend Development (Optional)
If you want to run or modify the standalone React application:

```bash
cd frontend
npm install
npm run dev
```
The React development server runs on `http://localhost:5173`.

---

## ⚙️ AI Engine Configuration

Configure your AI settings easily in the web UI by clicking the **Settings (⚙️)** button in the top navigation bar:

| Provider | Requirement | Default / Fallback |
| :--- | :--- | :--- |
| **Offline NLP** | None | Built-in offline algorithm (always works) |
| **Ollama** | Ollama running locally | `http://localhost:11434` |
| **Google Gemini** | `GEMINI_API_KEY` | Set in UI or `.env` |
| **OpenAI / Groq** | `OPENAI_API_KEY` | Set in UI or `.env` |

---

## 📡 REST API Overview

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | System health check & AI provider availability status |
| `GET` | `/api/sample-topics` | Pre-packaged curated study modules |
| `POST` | `/api/upload` | Upload PDF and extract text with metadata |
| `POST` | `/api/generate` | Generate customized quiz questions |
| `POST` | `/api/save-result` | Save completed quiz attempt to history |
| `GET` | `/api/history` | Retrieve past test sessions and scores |
| `POST` | `/api/export` | Download quiz as a Markdown summary document |

---

## 📂 Project Structure

```text
QuizCrafter/
├── backend/
│   ├── main.py              # FastAPI application & API routes
│   ├── generator.py         # Multi-provider AI quiz engine (Offline, Ollama, Gemini, OpenAI)
│   ├── quiz_llm.py          # LLM prompt orchestration
│   ├── template.py          # Prompt engineering templates
│   ├── test_api.py          # API verification test suite
│   ├── static/              # Bundled frontend (HTML/JS/Tailwind)
│   └── requirements.txt     # Python dependencies
├── frontend/                # Optional React + Vite + Tailwind client
│   ├── src/                 # React components & UI logic
│   └── package.json         # Node.js dependencies & scripts
├── run.py                   # One-click application launcher
├── start.bat                # Windows quick-launch script
├── LICENSE                  # Open source license
└── README.md                # Project documentation
```

---

## 👤 Author & Maintainer

- **Developer**: [Souparna Ghosh](https://github.com/Eternal-bliss23)
- **GitHub**: [@Eternal-bliss23](https://github.com/Eternal-bliss23)
- **Project Repository**: [https://github.com/Eternal-bliss23/QuizCrafter](https://github.com/Eternal-bliss23/QuizCrafter)

Feel free to star ⭐ the repository if you found this useful!

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
