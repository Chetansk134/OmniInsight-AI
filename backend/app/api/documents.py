import hashlib
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from backend.app.database.chroma_db import get_collection
from backend.app.database.postgres_db import (
    delete_document_record,
    get_all_documents,
    get_document_by_hash,
    get_document_by_id,
)
from backend.app.ingestion.pdf_ingestion import ingest_pdf

router = APIRouter(prefix="/documents", tags=["Documents"])

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


@router.get("/")
def list_documents():
    """List uploaded documents stored in PostgreSQL."""

    try:
        return {"documents": get_all_documents()}

    except Exception as error:
        print(f"Failed to retrieve documents: {error}")

        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve documents. Check the backend logs.",
        ) from error


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a PDF while preventing duplicate file uploads."""

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    file_bytes = await file.read(MAX_FILE_SIZE + 1)

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="PDF exceeds the 20 MB upload limit.",
        )

    if not file_bytes:
        raise HTTPException(
            status_code=400,
            detail="The uploaded PDF is empty.",
        )

    try:
        file_hash = hashlib.sha256(file_bytes).hexdigest()

        existing_document = get_document_by_hash(file_hash)

        if existing_document:
            return {
                "message": "This document has already been uploaded.",
                "status": "duplicate",
                "document_id": existing_document["document_id"],
                "filename": existing_document["filename"],
                "total_pages": existing_document["total_pages"],
                "chunks_created": 0,
            }

        result = ingest_pdf(file_bytes, file.filename)

        return {
            "message": "PDF processing completed.",
            **result,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        print(f"Document processing failed: {error}")

        raise HTTPException(
            status_code=500,
            detail="Document processing failed. Check the backend logs.",
        ) from error


@router.delete("/{document_id}")
def delete_document(document_id: str):
    """Delete a document and its associated data."""

    # 1. Find the document in PostgreSQL.
    try:
        document = get_document_by_id(document_id)

    except Exception as error:
        print(f"Failed to retrieve document: {error}")

        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve the document.",
        ) from error

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    # 2. Validate the stored PDF path.
    project_root = Path(__file__).resolve().parents[3]
    upload_dir = (project_root / "data" / "uploads").resolve()

    try:
        file_path = Path(document["file_path"]).resolve()

        if not file_path.is_relative_to(upload_dir):
            raise HTTPException(
                status_code=500,
                detail="The stored PDF path is invalid. No data was deleted.",
            )

    except (OSError, TypeError, ValueError) as error:
        raise HTTPException(
            status_code=500,
            detail="Unable to validate the stored PDF path.",
        ) from error

    # 3. Remove the document's chunks from ChromaDB.
    try:
        collection = get_collection()

        collection.delete(
            where={"document_id": document_id}
        )

    except Exception as error:
        print(f"ChromaDB deletion failed: {error}")

        raise HTTPException(
            status_code=500,
            detail="Unable to delete the document's search data.",
        ) from error

    # 4. Delete the stored PDF, if it exists.
    try:
        if file_path.exists():
            if not file_path.is_file():
                raise HTTPException(
                    status_code=500,
                    detail="The stored PDF path is not a file.",
                )

            file_path.unlink()

    except OSError as error:
        print(f"PDF deletion failed: {error}")

        raise HTTPException(
            status_code=500,
            detail=(
                "The search data was deleted, but the PDF could not "
                "be deleted. Check the backend logs."
            ),
        ) from error

    # 5. Delete the PostgreSQL record.
    try:
        deleted = delete_document_record(document_id)

        if not deleted:
            raise HTTPException(
                status_code=409,
                detail=(
                    "The PDF and search data were deleted, but the "
                    "database record could not be removed."
                ),
            )

    except HTTPException:
        raise

    except Exception as error:
        print(f"PostgreSQL deletion failed: {error}")

        raise HTTPException(
            status_code=500,
            detail=(
                "The PDF and search data were deleted, but the "
                "database record could not be removed."
            ),
        ) from error

    return {
        "message": "Document deleted successfully.",
        "document_id": document_id,
        "filename": document["filename"],
    }

@router.get("/{document_id}/preview")
def preview_document(document_id: str):
    """Safely preview an uploaded PDF using its document ID."""

    # 1. Find the document in PostgreSQL.
    try:
        document = get_document_by_id(document_id)

    except Exception as error:
        print(f"Failed to retrieve document for preview: {error}")

        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve the document.",
        ) from error

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    # 2. Restrict access to files in the uploads directory.
    project_root = Path(__file__).resolve().parents[3]
    upload_dir = (project_root / "data" / "uploads").resolve()

    try:
        file_path = Path(document["file_path"]).resolve()

        if not file_path.is_relative_to(upload_dir):
            raise HTTPException(
                status_code=500,
                detail="The stored PDF path is invalid.",
            )

    except (OSError, TypeError, ValueError) as error:
        raise HTTPException(
            status_code=500,
            detail="Unable to validate the stored PDF path.",
        ) from error

    # 3. Check that the PDF exists.
    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="The stored PDF file was not found.",
        )

    # 4. Return the PDF for browser preview.
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        content_disposition_type="inline",
        filename=document["filename"],
    )

