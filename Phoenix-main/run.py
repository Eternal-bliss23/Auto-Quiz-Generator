#!/usr/bin/env python
"""
QuizCrafter Launcher
Runs the FastAPI server and launches your browser to http://localhost:8000.
"""
import sys
import os
import time
import webbrowser
import threading
from pathlib import Path

# Add backend directory to sys.path
BASE_DIR = Path(__file__).resolve().parent
BACKEND_DIR = BASE_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))

def open_browser():
    time.sleep(1.2)
    print("\n[+] Opening QuizCrafter in your browser: http://localhost:8000 ...")
    webbrowser.open("http://localhost:8000")

def main():
    print("=" * 60)
    print("  QuizCrafter - AI Interactive Quiz Generator")
    print("=" * 60)
    print("Backend & Frontend server starting at http://localhost:8000")
    print("Press CTRL+C to stop the server anytime.\n")

    # Start browser in a background thread
    threading.Thread(target=open_browser, daemon=True).start()

    # Launch uvicorn
    import uvicorn
    uvicorn.run("main:app", app_dir=str(BACKEND_DIR), host="127.0.0.1", port=8000, reload=False)

if __name__ == "__main__":
    main()
