# Task 5: AI-Powered Document Search & RAG Query Service

FastAPI service with vector database (ChromaDB) for document embeddings and RAG (Retrieval-Augmented Generation) using OpenRouter.

## Project Structure

```
stage7-task5/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app initialization
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database setup
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── routes/              # API routes
│   │   ├── __init__.py
│   │   ├── health.py        # Health check endpoints
│   │   ├── documents.py     # Document upload/management
│   │   └── query.py         # RAG query endpoints
│   └── services/            # Business logic
│       ├── __init__.py
│       ├── text_extraction_service.py  # PDF/DOCX/TXT extraction
│       ├── chunking_service.py          # Text chunking
│       ├── embedding_service.py        # OpenRouter embeddings
│       ├── vector_db_service.py        # ChromaDB operations
│       ├── rag_service.py              # RAG answer generation
│       └── document_service.py         # Document management
├── requirements.txt
└── README.md
```

## Features

- ✅ Modular architecture (routes, services, models, schemas)
- ✅ Upload PDF, DOCX, or TXT documents
- ✅ Automatic text extraction and chunking
- ✅ Embedding generation using OpenRouter
- ✅ Vector storage in ChromaDB
- ✅ RAG-based question answering
- ✅ Document listing and retrieval

## Setup

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables:**
   ```bash
   export OPENROUTER_API_KEY="your-openrouter-api-key"
   export EMBEDDING_MODEL="openai/text-embedding-3-small"
   export LLM_MODEL="openai/gpt-4o-mini"
   export DATABASE_URL="sqlite:///./task5.db"
   export STORAGE_PATH="./documents"
   export CHROMA_PERSIST_DIR="./chroma_db"
   ```

3. **Run the application:**
   ```bash
   uvicorn app.main:app --reload
   ```

### Docker

1. **Set environment variables** (export or set in your shell):
   ```bash
   export OPENROUTER_API_KEY="your-openrouter-api-key"
   ```

2. **Start the service:**
   ```bash
   docker-compose up -d
   ```

3. **Access the API:**
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs
   - Health: http://localhost:8000/health

## API Endpoints

### 1. Upload Document
- **POST** `/documents`
- Body: multipart/form-data with PDF, DOCX, or TXT file
- Extracts text, chunks it, generates embeddings, stores in vector DB
- Returns: `{"document_id": "...", "chunk_count": 10}`

### 2. Query Documents
- **POST** `/query`
- Body: `{"question": "...", "top_k": 5}`
- Embeds question, searches vector DB, retrieves relevant chunks, generates answer
- Returns: `{"answer": "...", "chunks_used": [...], "document_ids": [...]}`

### 3. List Documents
- **GET** `/documents?skip=0&limit=100`
- Returns list of uploaded documents with chunk counts

### 4. Get Document
- **GET** `/documents/{document_id}`
- Returns document details including text and chunks

### 5. Health Check
- **GET** `/health`
- Returns API health status and configuration

## Usage Examples

### Upload Document
```bash
curl -X POST http://localhost:8000/documents \
  -F "file=@document.pdf"
```

### Query Documents
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the main topic?", "top_k": 5}'
```

### List Documents
```bash
curl http://localhost:8000/documents
```

### Get Document Details
```bash
curl http://localhost:8000/documents/{document_id}
```

## Test
POST - /documents
Upload a document (PDF, DOCX, or TXT)

Extracts text from the document
Chunks the text
Generates embeddings
Stores in vector database
Returns document ID and chunk count
<img width="884" height="212" alt="image" src="https://github.com/user-attachments/assets/444b3f8c-f6cd-41a4-a279-b9f7b734dc9b" />

GET - /documents
List all uploaded documents with chunk counts
<img width="673" height="300" alt="image" src="https://github.com/user-attachments/assets/2bf8274e-ec9b-4673-9c65-117c16f420d5" />

GET - /document/{document_id}
Get document details including extracted text and chunks
<img width="843" height="378" alt="image" src="https://github.com/user-attachments/assets/a94e274b-eb76-4bcd-bdb3-d9b3731a398e" />



## How It Works

1. **Upload**: Document is uploaded, text extracted, split into chunks (~500 tokens)
2. **Embedding**: Each chunk is embedded using OpenRouter embedding model
3. **Storage**: Embeddings stored in ChromaDB with metadata
4. **Query**: User question is embedded, vector search finds similar chunks
5. **RAG**: Retrieved chunks + question sent to LLM for answer generation

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENROUTER_API_KEY` | - | OpenRouter API key (required) |
| `EMBEDDING_MODEL` | `openai/text-embedding-3-small` | Embedding model |
| `LLM_MODEL` | `openai/gpt-4o-mini` | LLM model for RAG |
| `DATABASE_URL` | `sqlite:///./task5.db` | Database connection |
| `STORAGE_PATH` | `./documents` | Document storage path |
| `CHROMA_PERSIST_DIR` | `./chroma_db` | ChromaDB persistence directory |
| `CHUNK_SIZE` | `500` | Tokens per chunk |
| `CHUNK_OVERLAP` | `50` | Overlap tokens between chunks |
| `MAX_FILE_SIZE` | `10485760` | Max file size in bytes (10MB) |

## Vector Database

Uses ChromaDB (local persistent storage) with cosine similarity for semantic search.

