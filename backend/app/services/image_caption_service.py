import base64
import mimetypes
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-6-luna")

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def describe_image(image_path: str) -> str:
    """
    Generate a textual description of an image using a vision model.
    """

    path = Path(image_path)

    if not path.is_file():
        raise FileNotFoundError(
            f"Image file not found: {path}"
        )

    mime_type, _ = mimetypes.guess_type(path.name)

    supported_types = {
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/gif",
    }

    if mime_type not in supported_types:
        raise ValueError(
            f"Unsupported image format: {mime_type}"
        )

    image_base64 = base64.b64encode(
        path.read_bytes()
    ).decode("utf-8")

    image_data_url = (
        f"data:{mime_type};base64,{image_base64}"
    )

    response = client.responses.create(
        model=MODEL_NAME,
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "Describe this image for a document "
                            "search system. Identify the main objects, "
                            "scene, colors, and important visual details. "
                            "If it contains a chart, table, or diagram, "
                            "explain its visible information. "
                            "Do not invent details that are not visible. "
                            "Write a concise, searchable description."
                        ),
                    },
                    {
                        "type": "input_image",
                        "image_url": image_data_url,
                        "detail": "high",
                    },
                ],
            }
        ],
    )

    description = response.output_text.strip()

    if not description:
        raise ValueError(
            "The vision model returned an empty description."
        )

    return description