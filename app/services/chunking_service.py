"""
Text chunking service for splitting documents into chunks
"""

from typing import List
from app.config import settings


class ChunkingService:
    """Service for chunking text into smaller pieces"""
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
        """
        Split text into chunks with overlap
        
        Args:
            text: Text to chunk
            chunk_size: Size of each chunk in approximate tokens (default from config)
            overlap: Overlap between chunks in approximate tokens (default from config)
            
        Returns:
            List of text chunks
        """
        if chunk_size is None:
            chunk_size = settings.CHUNK_SIZE
        if overlap is None:
            overlap = settings.CHUNK_OVERLAP
        
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            # Approximate tokens: ~4 characters per token
            word_length = len(word) // 4
            
            if current_length + word_length > chunk_size and current_chunk:
                # Save current chunk
                chunks.append(" ".join(current_chunk))
                
                # Start new chunk with overlap
                overlap_words = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
                current_chunk = overlap_words + [word]
                current_length = sum(len(w) // 4 for w in current_chunk)
            else:
                current_chunk.append(word)
                current_length += word_length
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks


chunking_service = ChunkingService()

