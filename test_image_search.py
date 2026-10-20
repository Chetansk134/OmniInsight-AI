from backend.app.services.image_search_service import search_images


def main():
    query = "industrial structures with glowing blue lights"

    print("Search query:", query)
    print("\nSearching indexed images...\n")

    result = search_images(query=query, top_k=5)

    print("Results found:", result["results_count"])

    for index, image in enumerate(result["results"], start=1):
        print("\n" + "=" * 60)
        print(f"Result {index}")
        print("Image ID:", image["image_id"])
        print("PDF page:", image["page"])
        print("Distance:", round(image["distance"], 4))
        print("Image path:", image["image_path"])
        print("Description:", image["description"])


if __name__ == "__main__":
    main()