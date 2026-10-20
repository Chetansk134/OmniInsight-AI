import re


CITATION_PATTERN = r"\[Source \d+:[^\]]+\]"


def validate_citations(answer: str, valid_source_labels: set[str]) -> str:
    """
    Remove invalid source citations and duplicate valid citations.
    Preserve the first occurrence of each valid citation.
    """

    generated_citations = re.findall(CITATION_PATTERN, answer)

    for citation in generated_citations:
        if citation not in valid_source_labels:
            answer = answer.replace(citation, "")

    seen_citations = set()

    def remove_duplicate_citations(match):
        citation = match.group(0)

        if citation in seen_citations:
            return ""

        seen_citations.add(citation)
        return citation

    answer = re.sub(
        CITATION_PATTERN,
        remove_duplicate_citations,
        answer,
    )

    answer = re.sub(r"[ \t]{2,}", " ", answer)
    answer = re.sub(r"\n{3,}", "\n\n", answer)

    return answer.strip()