from backend.app.database.chroma_db import get_collection


def main():
    collection = get_collection()

    print("Total records in ChromaDB:", collection.count())

    results = collection.get(
        where={"content_type": "image"},
        include=["documents", "metadatas"],
    )

    image_count = len(results["ids"])

    print("Indexed image descriptions:", image_count)

    for index, image_id in enumerate(results["ids"], start=1):
        metadata = results["metadatas"][index - 1]
        description = results["documents"][index - 1]

        print("\n" + "=" * 60)
        print(f"Image {index}")
        print("Image ID:", image_id)
        print("Document ID:", metadata.get("document_id"))
        print("PDF page:", metadata.get("page"))
        print("Image path:", metadata.get("image_path"))
        print("AI description:", description)


if __name__ == "__main__":
    main()