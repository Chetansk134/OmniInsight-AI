from pathlib import Path

import pymupdf


# Project directories
PROJECT_ROOT = Path(__file__).resolve().parents[3]

IMAGE_OUTPUT_DIR = PROJECT_ROOT / "data" / "extracted_images"
IMAGE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def extract_pdf_images(
    pdf_path: str,
    document_id: str,
):
    """
    Extract embedded images from a PDF and save them locally.

    Returns metadata for every successfully saved image.
    """

    pdf_file = Path(pdf_path).resolve()

    if not pdf_file.is_file():
        raise FileNotFoundError(
            f"PDF file not found: {pdf_file}"
        )

    if pdf_file.suffix.lower() != ".pdf":
        raise ValueError("Only PDF files are supported.")

    extracted_images = []

    with pymupdf.open(pdf_file) as pdf:

        for page_index, page in enumerate(pdf):

            # Get image references on the current page.
            images = page.get_images(full=True)

            for image_index, image_info in enumerate(images):

                xref = image_info[0]

                try:
                    image_data = pdf.extract_image(xref)

                    image_bytes = image_data["image"]
                    image_extension = image_data["ext"]

                    image_filename = (
                        f"{document_id}_"
                        f"page_{page_index + 1}_"
                        f"image_{image_index + 1}."
                        f"{image_extension}"
                    )

                    image_path = (
                        IMAGE_OUTPUT_DIR / image_filename
                    )

                    image_path.write_bytes(image_bytes)

                    extracted_images.append({
                        "document_id": document_id,
                        "page": page_index + 1,
                        "image_index": image_index + 1,
                        "image_path": str(image_path),
                        "image_extension": image_extension,
                        "size_bytes": len(image_bytes),
                    })

                except Exception as error:
                    print(
                        f"Could not extract image {xref} "
                        f"from page {page_index + 1}: {error}"
                    )

    return {
        "document_id": document_id,
        "images_extracted": len(extracted_images),
        "images": extracted_images,
    }