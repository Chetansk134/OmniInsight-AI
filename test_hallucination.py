from unittest.mock import patch

from backend.app.services.evidence_verification_service import (
    verify_answer_against_context,
)


DOCUMENT_CONTEXT = """
Machine learning techniques can help classify documents and extract
information. Optical character recognition (OCR) can recognize printed
text in scanned documents.
"""


def test_supported_answer_is_verified():
    """An answer supported by the context should pass verification."""

    with patch(
        "backend.app.services.evidence_verification_service.OpenAI"
    ) as mock_openai:

        mock_client = mock_openai.return_value
        mock_client.responses.create.return_value.output_text = (
            '{"verified": true, '
            '"reason": "The context supports the answer."}'
        )

        result = verify_answer_against_context(
            question="How can machine learning help with documents?",
            answer=(
                "Machine learning can help classify documents "
                "and extract information."
            ),
            context=DOCUMENT_CONTEXT,
        )

    assert result["verified"] is True


def test_unsupported_answer_is_rejected():
    """An answer containing an unsupported claim should fail verification."""

    with patch(
        "backend.app.services.evidence_verification_service.OpenAI"
    ) as mock_openai:

        mock_client = mock_openai.return_value
        mock_client.responses.create.return_value.output_text = (
            '{"verified": false, '
            '"reason": "The context does not support the claim."}'
        )

        result = verify_answer_against_context(
            question="How can machine learning help with documents?",
            answer=(
                "Machine learning can classify documents. "
                "Microsoft was founded in 1990."
            ),
            context=DOCUMENT_CONTEXT,
        )

    assert result["verified"] is False


def test_empty_input_fails_verification():
    """Empty input must not be marked as verified."""

    result = verify_answer_against_context(
        question="",
        answer="Some answer",
        context=DOCUMENT_CONTEXT,
    )

    assert result["verified"] is False


def test_verifier_failure_fails_closed():
    """A failed verification request must not be treated as success."""

    with patch(
        "backend.app.services.evidence_verification_service.OpenAI"
    ) as mock_openai:

        mock_client = mock_openai.return_value
        mock_client.responses.create.side_effect = RuntimeError(
            "Simulated API failure"
        )

        result = verify_answer_against_context(
            question="How can machine learning help with documents?",
            answer="Machine learning can classify documents.",
            context=DOCUMENT_CONTEXT,
        )

    assert result["verified"] is False