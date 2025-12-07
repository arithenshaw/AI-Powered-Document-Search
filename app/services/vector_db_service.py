"""
Vector database service for storing and querying document embeddings
"""

from typing import List, Dict, Any, Optional
from app.config import settings

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False


class VectorDBService:
    """Service for managing vector database operations"""
    
    def __init__(self):
        self.client = None
        self.collection = None
        if CHROMADB_AVAILABLE:
            self._initialize()
    
    def _initialize(self):
        """Initialize ChromaDB client and collection"""
        if not CHROMADB_AVAILABLE:
            return
        
        # Disable telemetry to suppress warnings
        client_settings = Settings(
            anonymized_telemetry=False,
            allow_reset=True
        )
        
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=client_settings
        )
        self.collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_documents(
        self,
        document_id: str,
        chunk_ids: List[str],
        embeddings: List[List[float]],
        chunks: List[str],
        metadatas: List[Dict[str, Any]]
    ):
        """
        Add document chunks to vector database
        
        Args:
            document_id: Document identifier
            chunk_ids: List of chunk IDs
            embeddings: List of embedding vectors
            chunks: List of chunk texts
            metadatas: List of metadata dictionaries
        """
        if not self.collection:
            raise Exception("Vector database not initialized")
        
        self.collection.add(
            ids=chunk_ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas,
        )
    
    def query(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        filter_dict: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Query vector database for similar chunks
        
        Args:
            query_embedding: Query embedding vector
            n_results: Number of results to return
            filter_dict: Optional filter dictionary
            
        Returns:
            Dictionary with ids, documents, metadatas, and distances
        """
        if not self.collection:
            raise Exception("Vector database not initialized")
        
        where = filter_dict if filter_dict else None
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
        )
        
        return results
    
    def get_chunks(self, chunk_ids: List[str]) -> Dict[str, Any]:
        """
        Get chunks by IDs
        
        Args:
            chunk_ids: List of chunk IDs
            
        Returns:
            Dictionary with ids and documents
        """
        if not self.collection:
            raise Exception("Vector database not initialized")
        
        return self.collection.get(ids=chunk_ids)
    
    def delete_document(self, document_id: str):
        """
        Delete all chunks for a document
        
        Args:
            document_id: Document identifier
        """
        if not self.collection:
            raise Exception("Vector database not initialized")
        
        # Get all chunks for this document
        results = self.collection.get(
            where={"document_id": document_id}
        )
        
        if results["ids"]:
            self.collection.delete(ids=results["ids"])


# Global instance
try:
    vector_db_service = VectorDBService()
except Exception:
    vector_db_service = None

