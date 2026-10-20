from backend.app.ingestion.pdf_ingestion import ingest_pdf
from backend.app.database.chroma_db import get_collection


sample_text = """
OmniInsight AI is an agentic multimodal retrieval-augmented generation
platform. It uses PostgreSQL to store document metadata and ChromaDB
to store text chunks and embeddings. FastAPI provides the backend API.
Sentence Transformers generates embeddings for semantic search.
"""

try:
    import pymupdf

    # Create a small sample PDF in memory.
    pdf_document = pymupdf.open()
    page = pdf_document.new_page()
    page.insert_text((72, 72), sample_text)

    pdf_bytes = pdf_document.tobytes()
    pdf_document.close()

    result = ingest_pdf(pdf_bytes, "sample_document.pdf")

    print("PDF ingestion completed!")
    print("Document ID:", result["document_id"])
    print("Pages:", result["total_pages"])
    print("Chunks:", result["chunks_created"])
    print("Status:", result["status"])
    print("ChromaDB total chunks:", get_collection().count())

except Exception as error:
    print("PDF ingestion failed.")
    print("Error:", error)