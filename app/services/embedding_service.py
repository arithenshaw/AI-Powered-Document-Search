"""
Embedding service for generating vector embeddings using OpenRouter
"""

import httpx
from typing import List
from app.config import settings


class EmbeddingService:
    """Service for generating embeddings"""
    
    @staticmethod
    async def get_embedding(text: str) -> List[float]:
        """
        Get embedding for a single text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        if not settings.OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY is not set. Please set it in your environment variables.")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.OPENROUTER_BASE_URL}/embeddings",
                headers={
                    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.EMBEDDING_MODEL,
                    "input": text,
                },
            )
            
            if response.status_code != 200:
                raise Exception(f"Embedding API error: {response.text}")
            
            result = response.json()
            return result["data"][0]["embedding"]
    
    @staticmethod
    async def get_embeddings_batch(texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for multiple texts in batch
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if not settings.OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY is not set. Please set it in your environment variables.")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{settings.OPENROUTER_BASE_URL}/embeddings",
                headers={
                    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.EMBEDDING_MODEL,
                    "input": texts,
                },
            )
            
            if response.status_code != 200:
                raise Exception(f"Embedding API error: {response.text}")
            
            result = response.json()
            return [item["embedding"] for item in result["data"]]


embedding_service = EmbeddingService()

