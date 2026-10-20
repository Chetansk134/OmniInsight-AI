from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.app.services.search_service import search_documents

router = APIRouter(prefix="/search", tags=["Search"])


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=3, ge=1, le=10)


@router.post("/")
def search(request: SearchRequest):
    """Search indexed documents and return unique passages."""

    try:
        # search_documents already returns the complete response.
        return search_documents(
            query=request.query,
            top_k=request.top_k,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        print(f"Document search failed: {error}")

        raise HTTPException(
            status_code=500,
            detail="Document search failed. Check backend logs.",
        ) from error