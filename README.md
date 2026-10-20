# OmniInsight AI — Agentic Multimodal RAG Platform

OmniInsight AI is an AI-powered document intelligence platform that enables users to upload PDF documents, search their content using semantic similarity, ask questions about the documents, and retrieve relevant images.

The platform combines Retrieval-Augmented Generation (RAG), vector search, citation validation, and evidence verification to help generate answers grounded in retrieved document content.

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
- React
- Vite
- JavaScript
- CSS

### Backend
- Python
- FastAPI
- Uvicorn

### Data and Retrieval
- PostgreSQL for document metadata
- ChromaDB for vector storage and semantic retrieval
- Sentence Transformers for local text embeddings
- PyMuPDF for PDF processing

### AI
- OpenAI API for answer generation and image captioning
- Evidence verification and citation-validation services

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