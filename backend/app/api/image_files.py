from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(
    prefix="/images",
    tags=["Extracted Images"],
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]

IMAGE_DIRECTORY = (
    PROJECT_ROOT / "data" / "extracted_images"
).resolve()


@router.get("/{image_filename}")
def get_extracted_image(image_filename: str):
    # Accept only filenames, not directory paths
    if (
        not image_filename
        or Path(image_filename).name != image_filename
        or "/" in image_filename
        or "\\" in image_filename
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid image filename.",
        )

    image_path = (IMAGE_DIRECTORY / image_filename).resolve()

    if not image_path.is_relative_to(IMAGE_DIRECTORY):
        raise HTTPException(
            status_code=400,
            detail="Invalid image path.",
        )

    if not image_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Image not found.",
        )

    allowed_extensions = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".gif": "image/gif",
        ".bmp": "image/bmp",
    }

    media_type = allowed_extensions.get(
        image_path.suffix.lower()
    )

    if media_type is None:
        raise HTTPException(
            status_code=415,
            detail="Unsupported image format.",
        )

    return FileResponse(
        path=image_path,
        media_type=media_type,
        content_disposition_type="inline",
    )