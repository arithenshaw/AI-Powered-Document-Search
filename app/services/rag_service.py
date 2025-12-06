"""
RAG (Retrieval-Augmented Generation) service for answering questions
"""

import httpx
from typing import List, Dict
from app.config import settings
from app.services.embedding_service import embedding_service


class RAGService:
    """Service for RAG-based question answering"""
    
    @staticmethod
    async def generate_answer(question: str, context_chunks: List[str]) -> Dict[str, str]:
        """
        Generate answer using RAG with OpenRouter LLM
        
        Args:
            question: User's question
            context_chunks: Retrieved context chunks
            
        Returns:
            Dictionary with answer and model name
        """
        if not settings.OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY is not set. Please set it in your environment variables.")
        
        context = "\n\n".join([f"[Chunk {i+1}]: {chunk}" for i, chunk in enumerate(context_chunks)])
        
        prompt = f"""You are a helpful assistant that answers questions based on the provided context documents.

Context Documents:
{context}

Question: {question}

Instructions:
- Answer the question based ONLY on the provided context
- If the context doesn't contain enough information, say so
- Cite which chunks you used in your answer
- Be concise and accurate

Answer:"""

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{settings.OPENROUTER_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.LLM_MODEL,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a helpful assistant that answers questions based on provided context documents."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.3,
                },
            )
            
            if response.status_code == 401:
                error_data = response.json() if response.text else {}
                error_msg = error_data.get("error", {}).get("message", "Authentication failed")
                raise ValueError(f"OpenRouter API authentication failed: {error_msg}. Please check your OPENROUTER_API_KEY.")
            elif response.status_code != 200:
                raise Exception(f"LLM API error (status {response.status_code}): {response.text}")
            
            result = response.json()
            answer = result["choices"][0]["message"]["content"]
            
            return {
                "answer": answer,
                "model": settings.LLM_MODEL,
            }


rag_service = RAGService()

