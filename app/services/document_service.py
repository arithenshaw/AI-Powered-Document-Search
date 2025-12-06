"""
Document service for managing document uploads and processing
"""

import uuid
import os
from datetime import datetime
from typing import List, Dict
from sqlalchemy.orm import Session
from app.models import Document
from app.config import settings
from app.services.text_extraction_service import text_extraction_service
from app.services.chunking_service import chunking_service
from app.services.embedding_service import embedding_service
from app.services.vector_db_service import vector_db_service


class DocumentService:
    """Service for managing documents"""
    
    @staticmethod
    async def create_document(
        db: Session,
        filename: str,
        file_content: bytes,
        file_type: str
    ) -> Document:
        """
        Create a new document, extract text, chunk it, generate embeddings, and store in vector DB
        
        Args:
            db: Database session
            filename: Original filename
            file_content: File content as bytes
            file_type: File MIME type
            
        Returns:
            Created Document instance
        """
        # Generate document ID
        document_id = str(uuid.uuid4())
        
        # Determine file extension
        if "pdf" in file_type.lower():
            file_ext = "pdf"
        elif "wordprocessingml" in file_type.lower() or "docx" in file_type.lower():
            file_ext = "docx"
        else:
            file_ext = "txt"
        
        # Save file
        file_path = os.path.join(settings.STORAGE_PATH, f"{document_id}.{file_ext}")
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # Extract text
        extracted_text = text_extraction_service.extract_text(file_content, file_type)
        
        if not extracted_text.strip():
            raise ValueError("No text extracted from document")
        
        # Chunk text
        chunks = chunking_service.chunk_text(extracted_text)
        
        if not chunks:
            raise ValueError("No chunks created from document")
        
        # Generate embeddings for chunks
        embeddings = await embedding_service.get_embeddings_batch(chunks)
        
        # Prepare data for vector DB
        chunk_ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [
            {
                "document_id": document_id,
                "chunk_index": i,
                "filename": filename,
            }
            for i in range(len(chunks))
        ]
        
        # Store in vector database
        if vector_db_service:
            vector_db_service.add_documents(
                document_id=document_id,
                chunk_ids=chunk_ids,
                embeddings=embeddings,
                chunks=chunks,
                metadatas=metadatas
            )
        
        # Create database record
        doc = Document(
            document_id=document_id,
            original_filename=filename,
            file_path=file_path,
            file_type=file_ext,
            extracted_text=extracted_text,
            chunk_count=len(chunks),
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        
        return doc
    
    @staticmethod
    def get_document(db: Session, document_id: str) -> Document:
        """Get document by ID"""
        return db.query(Document).filter(Document.document_id == document_id).first()
    
    @staticmethod
    def list_documents(db: Session, skip: int = 0, limit: int = 100):
        """List documents with pagination"""
        return db.query(Document).offset(skip).limit(limit).all()
    
    @staticmethod
    async def get_document_chunks(document_id: str) -> List[Dict[str, str]]:
        """Get chunks for a document from vector DB"""
        if not vector_db_service:
            return []
        
        chunk_ids = []
        # Get all chunks for this document (we need to query by metadata)
        # For now, we'll reconstruct chunk IDs based on chunk_count
        doc = None  # Would need to get from DB first
        # This is a simplified version - in production, you'd query by metadata
        return []


document_service = DocumentService()

