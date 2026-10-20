from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.api import ask as ask_module


client = TestClient(app)


def test_ask_endpoint_returns_answer_and_sources(monkeypatch):
    """The endpoint should return the answer and source metadata."""

    def fake_generate_answer(question: str, top_k: int = 3):
        return {
            "question": question,
            "answer": "Machine learning can help classify documents.",
            "model": "test-model",
            "sources": [
                {
                    "filename": "report.pdf",
                    "page": 2,
                    "relevance_distance": 0.25,
                }
            ],
        }

    monkeypatch.setattr(
        ask_module,
        "generate_answer",
        fake_generate_answer,
    )

    response = client.post(
        "/ask/",
        json={
            "question": "How can machine learning help?",
            "top_k": 3,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["question"] == "How can machine learning help?"
    assert data["answer"] == "Machine learning can help classify documents."
    assert data["model"] == "test-model"
    assert len(data["sources"]) == 1
    assert data["sources"][0]["filename"] == "report.pdf"


def test_ask_endpoint_rejects_empty_question():
    """An empty question should fail request validation."""

    response = client.post(
        "/ask/",
        json={
            "question": "",
            "top_k": 3,
        },
    )

    assert response.status_code == 422


def test_ask_endpoint_rejects_invalid_top_k():
    """top_k must be between 1 and 5."""

    response = client.post(
        "/ask/",
        json={
            "question": "Explain machine learning.",
            "top_k": 10,
        },
    )

    assert response.status_code == 422


def test_ask_endpoint_handles_service_error(monkeypatch):
    """Unexpected service errors should produce HTTP 500."""

    def fake_generate_answer(question: str, top_k: int = 3):
        raise RuntimeError("Simulated service failure")

    monkeypatch.setattr(
        ask_module,
        "generate_answer",
        fake_generate_answer,
    )

    response = client.post(
        "/ask/",
        json={
            "question": "Explain machine learning.",
            "top_k": 3,
        },
    )

    assert response.status_code == 500
    assert response.json()["detail"] == (
        "AI question answering failed. "
        "Check the backend terminal for details."
    )