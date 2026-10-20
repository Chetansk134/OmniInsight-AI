from unittest.mock import MagicMock, patch

from backend.app.services.answer_service import generate_answer


def test_answer_pipeline_returns_verified_answer():
    """Test retrieval, answer generation, citations, and verification together."""

    retrieved_text = (
        "Machine learning can help classify documents and extract information."
    )

    fake_search_response = {
        "query": "How does machine learning help?",
        "results_count": 1,
        "results": [
            {
                "text": retrieved_text,
                "filename": "report.pdf",
                "page": 2,
                "document_id": "test-document-id",
                "distance": 0.25,
            }
        ],
    }

    fake_openai_response = MagicMock()
    fake_openai_response.output_text = (
        "Machine learning can help classify documents and extract information. "
        "[Source 1: report.pdf, page 2]"
    )

    with (
        patch(
            "backend.app.services.answer_service.search_documents",
            return_value=fake_search_response,
        ),
        patch(
            "backend.app.services.answer_service.OpenAI"
        ) as mock_openai,
        patch(
            "backend.app.services.answer_service.verify_answer_against_context",
            return_value={
                "verified": True,
                "reason": "The answer is supported by the context.",
            },
        ),
    ):
        mock_client = mock_openai.return_value
        mock_client.responses.create.return_value = fake_openai_response

        result = generate_answer(
            question="How does machine learning help?",
            top_k=3,
        )

    assert result["question"] == "How does machine learning help?"
    assert "Machine learning can help classify documents" in result["answer"]
    assert "[Source 1: report.pdf, page 2]" in result["answer"]
    assert result["model"]
    assert len(result["sources"]) == 1
    assert result["sources"][0]["filename"] == "report.pdf"
    assert result["sources"][0]["page"] == 2


def test_answer_pipeline_replaces_answer_when_verification_fails():
    """An unverified generated answer must not be returned as trustworthy."""

    fake_search_response = {
        "query": "Who founded Microsoft?",
        "results_count": 1,
        "results": [
            {
                "text": "The document discusses Microsoft Word.",
                "filename": "report.pdf",
                "page": 5,
                "document_id": "test-document-id",
                "distance": 0.4,
            }
        ],
    }

    fake_openai_response = MagicMock()
    fake_openai_response.output_text = (
        "Microsoft was founded in 1990. "
        "[Source 1: report.pdf, page 5]"
    )

    with (
        patch(
            "backend.app.services.answer_service.search_documents",
            return_value=fake_search_response,
        ),
        patch(
            "backend.app.services.answer_service.OpenAI"
        ) as mock_openai,
        patch(
            "backend.app.services.answer_service.verify_answer_against_context",
            return_value={
                "verified": False,
                "reason": "The context does not support the founding date.",
            },
        ),
    ):
        mock_client = mock_openai.return_value
        mock_client.responses.create.return_value = fake_openai_response

        result = generate_answer(
            question="Who founded Microsoft?",
            top_k=3,
        )

    assert "couldn't verify" in result["answer"].lower()
    assert "founded in 1990" not in result["answer"].lower()
    assert len(result["sources"]) == 1