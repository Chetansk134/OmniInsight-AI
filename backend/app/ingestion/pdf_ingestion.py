import hashlib
import uuid
from pathlib import Path

import pymupdf
from sentence_transformers import SentenceTransformer

from backend.app.database.chroma_db import get_collection
from backend.app.database.postgres_db import save_document
from backend.app.ingestion.image_extraction import extract_pdf_images
from backend.app.services.image_caption_service import describe_image


# Project directories
PROJECT_ROOT = Path(__file__).resolve().parents[3]

UPLOAD_DIR = PROJECT_ROOT / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Load the embedding model only when needed
_embedding_model = None


def get_embedding_model():
    """Load and reuse the Sentence Transformer model."""
    global _embedding_model

    if _embedding_model is None:
        _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

    return _embedding_model


def split_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 150,
):
    """Split text into overlapping character-based chunks."""

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be between 0 and chunk_size.")

    text = " ".join(text.split())

    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end == len(text):
            break

        start = end - overlap

    return chunks


def ingest_pdf(file_bytes: bytes, filename: str):
    """
    Extract PDF text, generate embeddings, store chunks in ChromaDB,
    and save document metadata in PostgreSQL.
    """

    if not filename or not filename.lower().endswith(".pdf"):
        raise ValueError("Only PDF files are supported.")

    if not file_bytes:
        raise ValueError("The uploaded file is empty.")

    # 1. Extract text from the PDF.
    try:
        with pymupdf.open(
            stream=file_bytes,
            filetype="pdf",
        ) as pdf:
            page_texts = [
                page.get_text("text").strip()
                for page in pdf
            ]

            total_pages = len(pdf)

    except Exception as exc:
        raise ValueError(
            "The uploaded file is not a readable PDF."
        ) from exc

    if total_pages == 0:
        raise ValueError("The PDF contains no pages.")

    document_id = str(uuid.uuid4())
    file_hash = hashlib.sha256(file_bytes).hexdigest()
    safe_filename = Path(filename).name

    # 2. Split extracted text into chunks.
    chunks = []

    for page_number, page_text in enumerate(page_texts, start=1):
        for chunk in split_text(page_text):
            chunks.append({
                "text": chunk,
                "page": page_number,
            })

    print(f"PDF pages extracted: {total_pages}")
    print(f"Text chunks created: {len(chunks)}")

    # 3. Save the original PDF.
    stored_filename = f"{document_id}_{safe_filename}"
    file_path = UPLOAD_DIR / stored_filename
    file_path.write_bytes(file_bytes)

    # 4. Extract embedded images from the saved PDF.
    try:
        image_extraction_result = extract_pdf_images(
            pdf_path=str(file_path),
            document_id=document_id,
        )

        images = image_extraction_result["images"]

        print(
            f"Images extracted: "
            f"{image_extraction_result['images_extracted']}"
        )

    except Exception as error:
        print(f"Image extraction failed: {error}")
        images = []

    # 5. Generate searchable captions for extracted images.
    image_records = []

    for image in images:
        try:
            description = describe_image(image["image_path"])

            image_records.append({
                **image,
                "description": description,
            })

            print(
                f"Caption generated for PDF page "
                f"{image['page']}"
            )

        except Exception as error:
            print(
                f"Image captioning failed for "
                f"{image['image_path']}: {error}"
            )
    # 6. Handle PDFs without extractable text.
    if not chunks:
        status = "no_extractable_text"

        save_document(
            document_id=document_id,
            filename=safe_filename,
            file_path=str(file_path),
            file_hash=file_hash,
            total_pages=total_pages,
            status=status,
        )

        return {
            "document_id": document_id,
            "filename": safe_filename,
            "file_path": str(file_path),
            "file_hash": file_hash,
            "total_pages": total_pages,
            "chunks_created": 0,
            "status": status,
            "message": (
                "No extractable text was found. "
                "OCR may be required for scanned PDFs."
            ),
        }

    # 7. Generate embeddings.
    model = get_embedding_model()

    texts = [item["text"] for item in chunks]

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False,
    ).tolist()

    # 8. Prepare ChromaDB records.
    collection = get_collection()

    chunk_ids = [
        f"{document_id}_{index}"
        for index in range(len(chunks))
    ]

    metadata = [
        {
            "document_id": document_id,
            "filename": safe_filename,
            "page": item["page"],
            "chunk_index": index,
        }
        for index, item in enumerate(chunks)
    ]

    # 9. Store chunks and embeddings.
    collection.add(
        ids=chunk_ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadata,
    )

    # 10. Index image captions in ChromaDB.
    if image_records:
        image_texts = [
            image["description"]
            for image in image_records
        ]

        image_model = get_embedding_model()

        image_embeddings = image_model.encode(
            image_texts,
            normalize_embeddings=True,
            show_progress_bar=False,
        ).tolist()

        image_ids = [
            f"{document_id}_image_{index}"
            for index in range(len(image_records))
        ]

        image_metadata = [
            {
                "document_id": document_id,
                "filename": safe_filename,
                "page": image["page"],
                "image_index": image["image_index"],
                "image_path": image["image_path"],
                "content_type": "image",
            }
            for image in image_records
        ]

        collection.add(
            ids=image_ids,
            documents=image_texts,
            embeddings=image_embeddings,
            metadatas=image_metadata,
        )

        print(
            f"Image captions indexed: {len(image_records)}"
        )

    # 11. Save document metadata in PostgreSQL.
    save_document(
        document_id=document_id,
        filename=safe_filename,
        file_path=str(file_path),
        file_hash=file_hash,
        total_pages=total_pages,
        status="processed",
    )

    # 12. Return the processing result.
    return {
        "document_id": document_id,
        "filename": safe_filename,
        "file_path": str(file_path),
        "file_hash": file_hash,
        "total_pages": total_pages,
        "chunks_created": len(chunks),
        "status": "processed",
    }