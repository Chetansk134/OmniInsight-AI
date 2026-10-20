from backend.app.database.chroma_db import get_collection
from backend.app.ingestion.pdf_ingestion import get_embedding_model


def search_documents(query: str, top_k: int = 5):
    """Search ChromaDB and remove duplicate text passages."""

    if not query or not query.strip():
        raise ValueError("Search query cannot be empty.")

    if not 1 <= top_k <= 10:
        raise ValueError("top_k must be between 1 and 10.")

    collection = get_collection()
    total_chunks = collection.count()

    if total_chunks == 0:
        return {
            "query": query,
            "results_count": 0,
            "results": [],
        }

    # Retrieve extra candidates because some may be duplicates.
    candidate_count = min(total_chunks, top_k * 5)

    model = get_embedding_model()

    query_embedding = model.encode(
        [query.strip()],
        normalize_embeddings=True,
    ).tolist()

    search_results = collection.query(
        query_embeddings=query_embedding,
        n_results=candidate_count,
        include=["documents", "metadatas", "distances"],
    )

    documents = search_results.get("documents", [[]])[0]
    metadatas = search_results.get("metadatas", [[]])[0]
    distances = search_results.get("distances", [[]])[0]

    unique_results = []
    seen_texts = set()

    for text, metadata, distance in zip(
        documents,
        metadatas,
        distances,
    ):
        if not text:
            continue

        # Normalize whitespace and capitalization for duplicate detection.
        normalized_text = " ".join(text.split()).casefold()

        if normalized_text in seen_texts:
            continue

        seen_texts.add(normalized_text)

        metadata = metadata or {}

        unique_results.append({
            "text": text,
            "filename": metadata.get("filename", "Unknown document"),
            "page": metadata.get("page"),
            "document_id": metadata.get("document_id"),
            "distance": float(distance),
        })

        # Return only the requested number of unique passages.
        if len(unique_results) >= top_k:
            break

    return {
        "query": query,
        "results_count": len(unique_results),
        "results": unique_results,
    }