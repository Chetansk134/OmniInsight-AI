from pathlib import Path
from typing import Any

from backend.app.ingestion.image_extraction import extract_pdf_images
from backend.app.services.image_caption_service import describe_image
from backend.app.database.chroma_db import get_collection


def index_document_images(
    pdf_path: str,
    document_id: str,
) -> dict[str, Any]:
    """
    Extract images from a PDF, generate AI descriptions,
    and store the descriptions in ChromaDB.
    """

    extraction_result = extract_pdf_images(
        pdf_path=pdf_path,
        document_id=document_id,
    )

    images = extraction_result["images"]

    if not images:
        return {
            "document_id": document_id,
            "images_extracted": 0,
            "images_indexed": 0,
            "message": "No embedded images found in the PDF.",
        }

    collection = get_collection()

    indexed_count = 0
    failed_images = []

    for image in images:
        image_path = Path(image["image_path"])

        try:
            print(
                f"Generating description for page "
                f"{image['page']}, image {image['image_index']}..."
            )

            description = describe_image(str(image_path))

            image_id = (
                f"{document_id}_page_{image['page']}"
                f"_image_{image['image_index']}"
            )

            metadata = {
                "document_id": document_id,
                "filename": image_path.name,
                "page": int(image["page"]),
                "image_index": int(image["image_index"]),
                "content_type": "image",
                "image_path": str(image_path.resolve()),
            }

            collection.upsert(
                ids=[image_id],
                documents=[description],
                metadatas=[metadata],
            )

            indexed_count += 1

        except Exception as error:
            failed_images.append({
                "image_path": str(image_path),
                "error": str(error),
            })

            print(
                f"Could not index image {image_path.name}: {error}"
            )

    return {
        "document_id": document_id,
        "images_extracted": len(images),
        "images_indexed": indexed_count,
        "failed_images": failed_images,
        "message": (
            "Image indexing completed."
            if not failed_images
            else "Image indexing completed with some failures."
        ),
    }