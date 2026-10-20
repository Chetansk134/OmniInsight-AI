# OmniInsight AI — Agentic Multimodal RAG Platform

OmniInsight AI is a Generative AI-powered document intelligence platform
that combines Retrieval-Augmented Generation (RAG), semantic vector search,
and agentic request routing to help users explore PDF documents.

The platform uses Sentence Transformers to generate local text embeddings,
ChromaDB for semantic retrieval, and the OpenAI API for context-grounded
question answering and vision-based image captioning.

It also includes image extraction and search, source citation validation,
and evidence verification to help reduce unsupported AI-generated answers.
## Features

- **PDF ingestion:** Upload PDFs and extract text for processing.
- **Semantic search:** Retrieve relevant passages using vector similarity.
- **AI question answering:** Ask natural-language questions about uploaded documents.
- **Source citations:** Return source filenames and page numbers with answers.
- **Citation validation:** Validate generated source references against retrieved sources.
- **Evidence verification:** Check whether generated answers are supported by retrieved context.
- **Image extraction:** Extract embedded images from PDF documents.
- **Image captioning:** Generate descriptions of extracted images.
- **Image search:** Search for relevant images using their descriptions.
- **Agentic AI:** Route user requests to appropriate document or image retrieval operations.
- **Document management:** View, preview, and delete uploaded documents.

## Technology Stack

### Frontend
- React.js
- Vite
- JavaScript
- CSS

### Backend
- Python
- FastAPI
- Uvicorn
- Pydantic

### Generative AI and LLMs
- OpenAI API for LLM-based question answering
- OpenAI vision-capable model for image captioning
- Prompt engineering for context-grounded answer generation
- Evidence verification for checking answer support
- Citation validation for checking source references

### Retrieval-Augmented Generation (RAG)
- Retrieval-Augmented Generation (RAG) pipeline
- Document chunking and contextual retrieval
- Sentence Transformers (`all-MiniLM-L6-v2`) for local text embeddings
- Vector similarity search using ChromaDB
- Source-aware answer generation

### Multimodal AI
- PyMuPDF for PDF text extraction and embedded image extraction
- OpenAI vision capabilities for image caption generation
- Image indexing and caption-based image retrieval

### Agentic AI
- Agentic request routing
- Tool selection for document question answering and image search
- Modular AI services for retrieval and response generation

### Databases and Storage
- PostgreSQL for document metadata
- ChromaDB for vector storage and retrieval
- Local persistent storage for uploaded PDFs and extracted images

### Testing
- pytest
- Automated evidence-verification tests
- Citation-validation tests
- Answer-pipeline tests
- FastAPI endpoint tests

## Architecture

```text
React + Vite Frontend
          |
          v
     FastAPI Backend
          |
    +-----+----------------+
    |          |           |
    v          v           v
PostgreSQL  ChromaDB    OpenAI API
    |          |
    v          v
Document    Semantic
Metadata    Retrieval
               |
               v
        Answer Generation
               |
               v
       Citation Validation
               |
               v
       Evidence Verification
               |
               v
          Final Answer