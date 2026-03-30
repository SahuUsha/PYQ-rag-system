# PYQ RAG System

A retrieval-augmented generation (RAG) system for university exam questions.

## Overview

This project ingests exam paper PDFs, extracts structured questions using Gemini AI, stores the results in PostgreSQL, indexes semantic embeddings in Qdrant, and provides a search API plus an optional Streamlit frontend.

## Architecture

- `FastAPI` backend in `app/main.py`
- `POST /upload` to upload a PDF and ingest questions
- `GET /search` to query stored questions and return ranked results
- `Streamlit` UI in `streamlit_ui.py` for interactive search

## Core Components

### PDF ingestion

- `app/routes/upload.py`
  - accepts file upload
  - saves temporary file
  - extracts exam questions via `app/services/pdf_services.py`
  - saves results to PostgreSQL
  - inserts vectors into Qdrant

### Question extraction

- `app/services/pdf_services.py`
  - currently uses `app/services/gemini_service.py` to parse PDFs
- `app/services/gemini_service.py`
  - calls Gemini API to extract structured question JSON
  - output includes fields like `question_text`, `subquestions`, `marks`, `subject`, `year`, `semester`, and `exam_type`

### Database

- `app/database.py`
  - SQLAlchemy engine and session setup
  - loads `DATABASE_URL` from `.env`
- `app/models.py`
  - defines `Question` model
  - `question_text` is stored as `JSONB`

### Embeddings and vector search

- `app/services/embedding.py`
  - generates embeddings using Gemini embedding model
- `app/services/qdrant_service.py`
  - creates a Qdrant collection
  - inserts question vectors
  - searches for similar vectors

### Search flow

- `app/routes/search.py`
  - receives search queries
  - expands queries using `app/services/query_expansion_service.py`
  - searches Qdrant over the expanded queries
  - fetches question metadata from PostgreSQL
  - reranks results with hybrid scoring
  - generates reference content with `app/services/groq_service.py`

### AI generation

- `app/services/query_expansion_service.py`
  - expands and refines user queries for better recall
- `app/services/groq_service.py`
  - generates similar short questions, a long question, and a topic summary

## Key features

- AI-powered PDF question extraction
- Structured storage of exam questions
- Semantic search using embeddings
- Query expansion for better retrieval
- Hybrid ranking combining vector similarity and lexical relevance
- AI-generated exam-style reference output
- Simple Streamlit frontend for search experimentation

## Environment variables

The project requires these values in a `.env` file:

- `DATABASE_URL`
- `QDRANT_URL`
- `QDRANT_API_KEY`
- `GEMINI_API_KEY`
- `GROQ_API_KEY`

## How to run

1. Install dependencies from `requirements.txt`
2. Create a `.env` file with the required API keys and database settings
3. Start the FastAPI backend:
   ```bash
   uvicorn app.main:app --reload --port 8001
   ```
4. Run the Streamlit UI:
   ```bash
   streamlit run streamlit_ui.py
   ```

## Notes

- The backend creates database tables and the Qdrant collection on startup.
- Uploaded PDF questions are stored in PostgreSQL and indexed in Qdrant for semantic search.
- Search returns both retrieved questions and AI-generated reference content.
