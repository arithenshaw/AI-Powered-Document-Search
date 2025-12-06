"""
Query routes for RAG-based document search
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import QueryRequest, QueryResponse, ChunkInfo
from app.services.embedding_service import embedding_service
from app.services.rag_service import rag_service
from app.services.vector_db_service import vector_db_service
from app.config import settings

router = APIRouter(prefix="/query", tags=["Query"])


@router.post("", response_model=QueryResponse)
async def query_documents(
    query_data: QueryRequest,
    db: Session = Depends(get_db),
):
    """
    Query documents using RAG
    
    - Embeds the question
    - Searches vector database for similar chunks
    - Retrieves top-K relevant chunks
    - Generates answer using LLM with retrieved context
    
    Returns answer, chunks used, and document IDs
    """
    if not vector_db_service:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Vector database not available"
        )
    
    try:
        # Validate top_k
        top_k = min(max(query_data.top_k, 1), settings.MAX_TOP_K)
        
        # Embed question
        question_embedding = await embedding_service.get_embedding(query_data.question)
        
        # Search vector database
        results = vector_db_service.query(
            query_embedding=question_embedding,
            n_results=top_k
        )
        
        if not results.get("ids") or not results["ids"][0]:
            return QueryResponse(
                answer="No relevant documents found in the database.",
                chunks_used=[],
                document_ids=[],
                model=settings.LLM_MODEL,
            )
        
        # Extract chunks and metadata
        chunk_ids = results["ids"][0]
        chunks_text = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results.get("distances", [[0.0] * len(chunk_ids)])[0]
        
        # Calculate similarity scores (1 - distance for cosine similarity)
        similarity_scores = [1 - dist for dist in distances]
        
        chunks_used = [
            ChunkInfo(
                chunk_id=chunk_id,
                text=chunk_text,
                similarity_score=round(score, 4),
            )
            for chunk_id, chunk_text, score in zip(chunk_ids, chunks_text, similarity_scores)
        ]
        
        # Get unique document IDs
        document_ids = list(set([meta["document_id"] for meta in metadatas]))
        
        # Generate answer using RAG
        answer_data = await rag_service.generate_answer(query_data.question, chunks_text)
        
        return QueryResponse(
            answer=answer_data["answer"],
            chunks_used=chunks_used,
            document_ids=document_ids,
            model=answer_data["model"],
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query failed: {str(e)}"
        )

