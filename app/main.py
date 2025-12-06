"""
Main FastAPI application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.routes import documents, query, health

# Initialize directories
settings.init_directories()

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="RAG Document Search API",
    version="1.0.0",
    description="AI-Powered Document Search & RAG Query Service with Vector Database"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(documents.router)
app.include_router(query.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "RAG Document Search API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "supported_formats": ["PDF", "DOCX", "TXT"],
        "vector_db": "ChromaDB",
        "embedding_model": settings.EMBEDDING_MODEL,
        "llm_model": settings.LLM_MODEL,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

