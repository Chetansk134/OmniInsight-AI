from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.app.services.answer_service import generate_answer

router = APIRouter(prefix="/ask", tags=["AI Question Answering"])


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=3, ge=1, le=5)


@router.post("/")
def ask_question(request: AskRequest):
    try:
        result = generate_answer(
            question=request.question,
            top_k=request.top_k,
        )
        return result

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        print(f"AI question answering failed: {error}")

        raise HTTPException(
            status_code=500,
            detail=(
                "AI question answering failed. "
                "Check the backend terminal for details."
            ),
        ) from error