from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.app.services.image_search_service import search_images


router = APIRouter(
    prefix="/image-search",
    tags=["Image Search"],
)


class ImageSearchRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Natural-language description of the image to find.",
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of image results.",
    )

    document_id: str | None = Field(
        default=None,
        description="Optionally restrict the search to one document.",
    )


@router.post("/")
def search_images_endpoint(request: ImageSearchRequest):
    try:
        return search_images(
            query=request.query,
            top_k=request.top_k,
            document_id=request.document_id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Image search failed. Check the backend logs.",
        ) from error