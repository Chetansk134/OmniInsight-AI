from pathlib import Path

from backend.app.database.postgres_db import get_all_documents
from backend.app.ingestion.image_extraction import extract_pdf_images


def main():
    # Get uploaded documents from PostgreSQL.
    documents = get_all_documents()

    if not documents:
        print("No uploaded documents found.")
        return

    # Find image-doc.pdf.
    document = next(
        (
            item
            for item in documents
            if item["filename"].lower() == "image-doc.pdf"
        ),
        None,
    )

    if document is None:
        print("image-doc.pdf was not found.")
        return

    pdf_path = Path(document["file_path"])

    print("Selected PDF:", document["filename"])
    print("PDF path:", pdf_path)
    print("Document ID:", document["document_id"])

    # Extract images from the PDF.
    result = extract_pdf_images(
        pdf_path=str(pdf_path),
        document_id=document["document_id"],
    )

    print("\nImage extraction completed!")
    print("Images extracted:", result["images_extracted"])

    for image in result["images"]:
        print("\nImage details:")
        print("Page:", image["page"])
        print("Image index:", image["image_index"])
        print("Image path:", image["image_path"])
        print("Image format:", image["image_extension"])
        print("Size:", image["size_bytes"], "bytes")


if __name__ == "__main__":
    main()