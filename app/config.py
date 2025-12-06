"""
Configuration settings for the application
"""

import os
from typing import Optional

class Settings:
    """Application settings"""
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./task5.db")
    
    # OpenRouter Configuration
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "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")
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "openai/text-embedding-3-small")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "openai/gpt-4o-mini")
    
    # Vector Database Configuration
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    CHROMA_COLLECTION_NAME: str = os.getenv("CHROMA_COLLECTION_NAME", "documents")
    
    # Storage Configuration
    STORAGE_PATH: str = os.getenv("STORAGE_PATH", "./documents")
    
    # Chunking Configuration
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "500"))  # tokens per chunk
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "50"))
    
    # File Upload Limits
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", str(10 * 1024 * 1024)))  # 10MB default
    
    # Query Configuration
    DEFAULT_TOP_K: int = int(os.getenv("DEFAULT_TOP_K", "5"))  # Default number of chunks to retrieve
    MAX_TOP_K: int = int(os.getenv("MAX_TOP_K", "10"))  # Maximum chunks to retrieve

    @classmethod
    def init_directories(cls):
        """Initialize required directories"""
        os.makedirs(cls.STORAGE_PATH, exist_ok=True)
        os.makedirs(cls.CHROMA_PERSIST_DIR, exist_ok=True)


settings = Settings()

