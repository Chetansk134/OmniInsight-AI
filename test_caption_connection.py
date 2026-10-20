from dotenv import load_dotenv

load_dotenv()

from backend.app.services.image_caption_service import describe_image


image_path = input("Enter the full path of one extracted image: ").strip().strip('"')

try:
    print("\nGenerating image caption...\n")

    description = describe_image(image_path)

    print("SUCCESS!")
    print("Image description:")
    print(description)

except Exception as error:
    print("CAPTIONING FAILED")
    print(f"Error type: {type(error).__name__}")
    print(f"Error details: {error}")