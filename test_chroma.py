from backend.app.database.chroma_db import test_chroma

try:
    result = test_chroma()

    print("ChromaDB connection successful!")
    print("Collection:", result["collection_name"])
    print("Documents:", result["document_count"])
    print("Storage:", result["storage_path"])

except Exception as error:
    print("ChromaDB test failed.")
    print("Error:", error)