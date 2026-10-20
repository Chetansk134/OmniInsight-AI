from backend.app.services.evidence_verification_service import (
    verify_answer_against_context,
)


context = """
Machine learning techniques can help classify documents and extract
information. Optical character recognition (OCR) can recognize printed
text in scanned documents.
"""

# Test 1: The answer is supported by the context.
supported_answer = (
    "Machine learning can help classify documents and extract information."
)

result1 = verify_answer_against_context(
    question="How can machine learning help with documents?",
    answer=supported_answer,
    context=context,
)

print("\nTEST 1: Supported answer")
print(result1)


# Test 2: The answer contains a claim not supported by the context.
unsupported_answer = (
    "Machine learning can classify documents. "
    "Microsoft was founded in 1990."
)

result2 = verify_answer_against_context(
    question="How can machine learning help with documents?",
    answer=unsupported_answer,
    context=context,
)

print("\nTEST 2: Answer containing an unsupported claim")
print(result2)