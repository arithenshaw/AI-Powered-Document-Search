"""
Health check routes
"""

from fastapi import APIRouter
from app.schemas import HealthResponse
from app.config import settings

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="RAG Document Search API is running",
        vector_db="ChromaDB",
        embedding_model=settings.EMBEDDING_MODEL,
        llm_model=settings.LLM_MODEL,
    )

