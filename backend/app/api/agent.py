from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.app.services.agent_service import route_query

router = APIRouter(
    prefix="/agent",
    tags=["Agentic AI"],
)


class AgentRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Question or search request for the agent.",
    )

    top_k: int = Field(
        default=3,
        ge=1,
        le=5,
        description="Maximum number of results to retrieve.",
    )


@router.post("/")
def run_agent(request: AgentRequest):
    try:
        return route_query(
            question=request.question,
            top_k=request.top_k,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        print(f"Agent execution failed: {error}")

        raise HTTPException(
            status_code=500,
            detail="Agent execution failed. Check backend logs.",
        ) from error