"""
Document routes for uploading and managing documents
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import (
    DocumentUploadResponse,
    DocumentInfo,
    DocumentDetail
)
from app.services.document_service import document_service
from app.services.vector_db_service import vector_db_service
from app.config import settings

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("", response_model=DocumentUploadResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload a document (PDF, DOCX, or TXT)
    
    - Extracts text from the document
    - Chunks the text
    - Generates embeddings
    - Stores in vector database
    
    Returns document ID and chunk count
    """
    # Validate file type
    if not file.content_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File type not specified"
        )
    
    file_type = file.content_type.lower()
    supported_types = ["pdf", "wordprocessingml", "docx", "text/plain", "txt"]
    if not any(t in file_type for t in supported_types):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF, DOCX, and TXT files are supported"
        )
    
    # Read file content
    file_content = await file.read()
    
    # Validate file size
    if len(file_content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds {settings.MAX_FILE_SIZE / 1024 / 1024}MB limit"
        )
    
    try:
        doc = await document_service.create_document(
            db=db,
            filename=file.filename or "document",
            file_content=file_content,
            file_type=file_type
        )
        
        return DocumentUploadResponse(
            document_id=doc.document_id,
            message="Document uploaded and indexed successfully",
            chunk_count=doc.chunk_count,
        )
    
    except ValueError as e:
        # Handle API key errors and validation errors
        error_msg = str(e)
        if "OPENROUTER_API_KEY" in error_msg or "authentication" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=error_msg
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    except Exception as e:
        error_msg = str(e)
        if "authentication" in error_msg.lower() or "401" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=error_msg
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {error_msg}"
        )


@router.get("", response_model=List[DocumentInfo])
async def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    List all uploaded documents with chunk counts
    """
    docs = document_service.list_documents(db, skip=skip, limit=limit)
    return [
        DocumentInfo(
            document_id=doc.document_id,
            original_filename=doc.original_filename,
            file_type=doc.file_type,
            chunk_count=doc.chunk_count,
            created_at=doc.created_at,
        )
        for doc in docs
    ]


@router.get("/{document_id}", response_model=DocumentDetail)
async def get_document(
    document_id: str,
    db: Session = Depends(get_db),
):
    """
    Get document details including extracted text and chunks
    """
    doc = document_service.get_document(db, document_id)
    
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Retrieve chunks from vector DB
    chunks_data = []
    if vector_db_service:
        try:
            chunk_ids = [f"{document_id}_chunk_{i}" for i in range(doc.chunk_count)]
            results = vector_db_service.get_chunks(chunk_ids)
            
            chunks_data = [
                {"chunk_id": chunk_id, "text": doc_text}
                for chunk_id, doc_text in zip(results.get("ids", []), results.get("documents", []))
            ]
        except Exception:
            chunks_data = []
    
    return DocumentDetail(
        document_id=doc.document_id,
        original_filename=doc.original_filename,
        file_type=doc.file_type,
        extracted_text=doc.extracted_text or "",
        chunk_count=doc.chunk_count,
        chunks=chunks_data,
        created_at=doc.created_at,
    )

