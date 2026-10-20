from backend.app.services.citation_validation_service import validate_citations


VALID_SOURCE_1 = "[Source 1: report.pdf, page 2]"
VALID_SOURCE_2 = "[Source 2: report.pdf, page 5]"


def test_valid_citation_is_preserved():
    answer = f"The report discusses machine learning. {VALID_SOURCE_1}"

    result = validate_citations(
        answer,
        {VALID_SOURCE_1},
    )

    assert VALID_SOURCE_1 in result
    assert "machine learning" in result


def test_invalid_citation_is_removed():
    answer = (
        "The report discusses machine learning. "
        "[Source 9: missing.pdf, page 99]"
    )

    result = validate_citations(
        answer,
        {VALID_SOURCE_1},
    )

    assert "[Source 9:" not in result
    assert "machine learning" in result


def test_duplicate_citations_are_removed():
    answer = (
        f"First statement. {VALID_SOURCE_1} "
        f"Second statement. {VALID_SOURCE_1}"
    )

    result = validate_citations(
        answer,
        {VALID_SOURCE_1},
    )

    assert result.count(VALID_SOURCE_1) == 1


def test_multiple_valid_citations_are_preserved():
    answer = f"First statement. {VALID_SOURCE_1} Second statement. {VALID_SOURCE_2}"

    result = validate_citations(
        answer,
        {VALID_SOURCE_1, VALID_SOURCE_2},
    )

    assert VALID_SOURCE_1 in result
    assert VALID_SOURCE_2 in result