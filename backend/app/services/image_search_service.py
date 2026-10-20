from typing import Any

from backend.app.database.chroma_db import get_collection


def search_images(
    query: str,
    top_k: int = 5,
    document_id: str | None = None,
) -> dict[str, Any]:
    """
    Search indexed image descriptions using natural language.
    """

    query = query.strip()

    if not query:
        raise ValueError("Search query cannot be empty.")

    if not 1 <= top_k <= 20:
        raise ValueError("top_k must be between 1 and 20.")

    collection = get_collection()

    if collection.count() == 0:
        return {
            "query": query,
            "results_count": 0,
            "results": [],
        }

    where_filter = {"content_type": "image"}

    if document_id:
        where_filter = {
            "$and": [
                {"content_type": "image"},
                {"document_id": document_id},
            ]
        }

    results = collection.query(
        query_texts=[query],
        n_results=min(top_k, collection.count()),
        where=where_filter,
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )

    image_ids = results["ids"][0] if results["ids"] else []
    descriptions = (
        results["documents"][0]
        if results["documents"]
        else []
    )
    metadatas = (
        results["metadatas"][0]
        if results["metadatas"]
        else []
    )
    distances = (
        results["distances"][0]
        if results["distances"]
        else []
    )

    matched_images = []

    for image_id, description, metadata, distance in zip(
        image_ids,
        descriptions,
        metadatas,
        distances,
    ):
        matched_images.append({
            "image_id": image_id,
            "document_id": metadata.get("document_id"),
            "page": metadata.get("page"),
            "image_index": metadata.get("image_index"),
            "image_path": metadata.get("image_path"),
            "description": description,
            "distance": float(distance),
        })

    return {
        "query": query,
        "results_count": len(matched_images),
        "results": matched_images,
    }