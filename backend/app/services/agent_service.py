from typing import Any

from backend.app.services.answer_service import generate_answer
from backend.app.services.search_service import search_documents
from backend.app.services.image_search_service import search_images


def route_query(question: str, top_k: int = 3) -> dict[str, Any]:
    """
    Route a user question to the most appropriate existing tool.

    This is a lightweight, deterministic agentic workflow.
    """

    question = question.strip()

    if not question:
        raise ValueError("Question cannot be empty.")

    if not 1 <= top_k <= 5:
        raise ValueError("top_k must be between 1 and 5.")

    image_keywords = (
        "image",
        "images",
        "picture",
        "pictures",
        "photo",
        "photos",
        "visual",
        "visuals",
    )

    normalized_question = question.casefold()

    # Tool 1: Image search
    if any(word in normalized_question for word in image_keywords):
        result = search_images(
            query=question,
            top_k=top_k,
        )

        return {
            "question": question,
            "selected_tool": "image_search",
            "message": "Searched the visual knowledge base.",
            "result": result,
        }

    # Tool 2: Answer questions using retrieved document context
    answer_keywords = (
        "what",
        "why",
        "how",
        "explain",
        "describe",
        "summarize",
        "summary",
        "tell me",
    )

    if normalized_question.startswith(answer_keywords):
        result = generate_answer(
            question=question,
            top_k=top_k,
        )

        return {
            "question": question,
            "selected_tool": "document_qa",
            "message": "Generated an answer using document context.",
            "result": result,
        }

    # Tool 3: Retrieve relevant document passages
    search_response = search_documents(
        query=question,
        top_k=top_k,
    )

    return {
        "question": question,
        "selected_tool": "document_search",
        "message": "Retrieved relevant document passages.",
        "result": search_response,
    }