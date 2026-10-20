import os
from pathlib import Path

import chromadb
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[3]

chroma_path = os.getenv(
    "CHROMA_PATH",
    str(PROJECT_ROOT / "chroma_db"),
)

client = chromadb.PersistentClient(path=chroma_path)

collection = client.get_or_create_collection(
    name="omniinsight_documents",
    metadata={
        "description": "Document chunks and embeddings for OmniInsight AI"
    },
)


def get_collection():
    """Return the ChromaDB document collection."""
    return collection


def test_chroma():
    """Return basic information about the collection."""
    return {
        "collection_name": collection.name,
        "document_count": collection.count(),
        "storage_path": chroma_path,
    }