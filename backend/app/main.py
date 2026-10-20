from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.documents import router as documents_router
from backend.app.api.search import router as search_router
from backend.app.api.ask import router as ask_router
from backend.app.api.image_search import router as image_search_router
from backend.app.api.image_files import router as image_files_router
from backend.app.api.agent import router as agent_router


# Initialize FastAPI application
app = FastAPI(
    title="OmniInsight AI",
    description="Agentic Multimodal RAG Platform",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(documents_router)
app.include_router(search_router)
app.include_router(ask_router)
app.include_router(image_search_router)
app.include_router(image_files_router)
app.include_router(agent_router)
# Home endpoint
@app.get("/", tags=["Default"])
def home():
    return {
        "project": "OmniInsight AI",
        "message": "Welcome to OmniInsight AI!",
        "status": "running",
    }


# Health-check endpoint
@app.get("/health", tags=["Default"])
def health_check():
    return {
        "status": "healthy",
        "project": "OmniInsight AI",
    }