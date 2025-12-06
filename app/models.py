"""
Database models
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.database import Base


class Document(Base):
    """Document model for storing document metadata"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String, unique=True, index=True, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # pdf, docx, txt
    extracted_text = Column(Text, nullable=True)
    chunk_count = Column(Integer, default=0, nullable=False)
    document_metadata = Column(JSON, nullable=True)  # Renamed from 'metadata' (reserved word)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Document(document_id={self.document_id}, chunks={self.chunk_count})>"

