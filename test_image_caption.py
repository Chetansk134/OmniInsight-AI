from backend.app.database.postgres_db import get_all_documents
from backend.app.ingestion.image_extraction import extract_pdf_images
from backend.app.services.image_caption_service import describe_image


def main():
    documents = get_all_documents()

    document = next(
        (
            item for item in documents
            if item["filename"].lower() == "image-doc.pdf"
        ),
        None,
    )

    if document is None:
        print("image-doc.pdf was not found in PostgreSQL.")
        return

    result = extract_pdf_images(
        pdf_path=document["file_path"],
        document_id=document["document_id"],
    )

    if not result["images"]:
        print("No embedded images were extracted.")
        return

    image = result["images"][0]

    print("Image path:", image["image_path"])
    print("\nGenerating AI description...")

    description = describe_image(image["image_path"])

    print("\nAI-generated image description:")
    print(description)


if __name__ == "__main__":
    main()