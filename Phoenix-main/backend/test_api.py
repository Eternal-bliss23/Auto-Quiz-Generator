import sys
import os
import io
from pathlib import Path

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from main import app
from generator import SmartOfflineGenerator
import pypdf

def create_sample_pdf_bytes():
    writer = pypdf.PdfWriter()
    page = writer.add_blank_page(width=612, height=792)
    # Write some text into an actual PDF stream
    # Simple valid PDF with text annotation or extractable stream
    packet = io.BytesIO()
    # Let's create a minimal PDF with PDFWriter
    writer.write(packet)
    packet.seek(0)
    return packet.getvalue()

def run_tests():
    print("[*] Starting QuizCrafter Verification Tests...\n")
    client = TestClient(app)

    # Test 1: Health Check Endpoint
    print("Test 1: Testing /api/health ...")
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    print(f"[PASS] Health Check: Status={data['status']}, Ollama Detected={data['providers']['ollama']['available']}\n")

    # Test 2: Sample Topics Endpoint
    print("Test 2: Testing /api/sample-topics ...")
    res = client.get("/api/sample-topics")
    assert res.status_code == 200
    topics = res.json()
    assert len(topics) >= 3
    print(f"[PASS] Sample Topics: Found {len(topics)} curated topics.\n")

    # Test 3: Offline Generator Quality Test
    print("Test 3: Testing SmartOfflineGenerator ...")
    sample_text = topics[0]["text"]
    questions = SmartOfflineGenerator.generate_from_text(
        text=sample_text,
        topic="Artificial Intelligence",
        num_questions=5,
        difficulty="Medium"
    )
    assert len(questions) == 5
    for q in questions:
        assert len(q.options) == 4
        assert q.correct_answer in ["A", "B", "C", "D"]
        assert len(q.explanation) > 10
    print("[PASS] SmartOfflineGenerator: Generated 5 valid MCQs with explanations.\n")

    # Test 4: API Generate Quiz Endpoint
    print("Test 4: Testing POST /api/generate ...")
    payload = {
        "topic": "Microservices",
        "content": topics[1]["text"],
        "num_questions": 5,
        "difficulty": "Easy",
        "provider": "offline"
    }
    res = client.post("/api/generate", json=payload)
    assert res.status_code == 200
    quiz = res.json()
    assert len(quiz["questions"]) == 5
    print(f"[PASS] POST /api/generate: Provider used = {quiz['provider_used']}\n")

    # Test 5: Save Result & History
    print("Test 5: Testing POST /api/save-result and GET /api/history ...")
    sub_res = client.post("/api/save-result", json={
        "quiz_id": quiz["quiz_id"],
        "topic": "Microservices",
        "score": 5,
        "total_questions": 5,
        "percentage": 100.0,
        "answers": {"1": "A", "2": "A", "3": "A", "4": "A", "5": "A"},
        "time_spent_seconds": 45
    })
    assert sub_res.status_code == 200
    hist_res = client.get("/api/history")
    assert hist_res.status_code == 200
    history = hist_res.json()
    assert len(history) > 0
    assert history[0]["topic"] == "Microservices"
    print(f"[PASS] History: Successfully saved and retrieved quiz session.\n")

    # Test 6: Export Markdown Endpoint
    print("Test 6: Testing POST /api/export ...")
    export_payload = {
        "title": quiz["title"],
        "topic": quiz["topic"],
        "difficulty": quiz["difficulty"],
        "score": 5,
        "total": 5,
        "questions": quiz["questions"],
        "user_answers": {"1": "A"}
    }
    res = client.post("/api/export", json=export_payload)
    assert res.status_code == 200
    assert "# 📝" in res.json()["markdown"]
    print("[PASS] POST /api/export: Generated formatted report.\n")

    # Test 7: Static Web App Delivery
    print("Test 7: Testing GET / (Static Web UI) ...")
    res = client.get("/")
    assert res.status_code == 200
    assert "QuizCrafter" in res.text
    print("[PASS] GET /: Web App served successfully.\n")

    print("[SUCCESS] ALL TESTS COMPLETED WITH 100% SUCCESS!")

if __name__ == "__main__":
    run_tests()
