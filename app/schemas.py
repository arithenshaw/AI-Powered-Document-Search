"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class DocumentUploadResponse(BaseModel):
    """Response schema for document upload"""
    document_id: str
    message: str
    chunk_count: int
    
    class Config:
        from_attributes = True


class QueryRequest(BaseModel):
    """Request schema for document query"""
    question: str
    top_k: int = 5  # Number of chunks to retrieve


class ChunkInfo(BaseModel):
    """Information about a retrieved chunk"""
    chunk_id: str
    text: str
    similarity_score: float


class QueryResponse(BaseModel):
    """Response schema for document query"""
    answer: str
    chunks_used: List[ChunkInfo]
    document_ids: List[str]
    model: str


class DocumentInfo(BaseModel):
    """Document information for listing"""
    document_id: str
    original_filename: str
    file_type: str
    chunk_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChunkDetail(BaseModel):
    """Chunk detail information"""
    chunk_id: str
    text: str


class DocumentDetail(BaseModel):
    """Detailed document information"""
    document_id: str
    original_filename: str
    file_type: str
    extracted_text: str
    chunk_count: int
    chunks: List[ChunkDetail]
    created_at: datetime
    
    class Config:
        from_attributes = True


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    message: str
    vector_db: str
    embedding_model: str
    llm_model: str

