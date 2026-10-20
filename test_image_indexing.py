from backend.app.database.postgres_db import get_all_documents
from backend.app.services.image_indexing_service import index_document_images


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
        print("ERROR: image-doc.pdf was not found.")
        return

    print("Document:", document["filename"])
    print("Document ID:", document["document_id"])
    print("\nStarting image indexing...")

    result = index_document_images(
        pdf_path=document["file_path"],
        document_id=document["document_id"],
    )

    print("\nImage indexing result:")

    for key, value in result.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()