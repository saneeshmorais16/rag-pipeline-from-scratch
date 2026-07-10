# RAG Pipeline From Scratch

A portfolio-ready starter Retrieval-Augmented Generation pipeline that demonstrates document ingestion, chunking, local embeddings, vector search, retrieval, grounded answer generation, citations, and a simple API/UI.

This project is intentionally honest: it is a clean in-progress implementation, not a production RAG platform. It is designed to show the core engineering path clearly and safely.

## What It Does

- Ingests `.txt`, `.md`, and optionally `.pdf` documents.
- Cleans and chunks document text.
- Generates local sentence-transformers embeddings by default.
- Stores chunks and embeddings in a local SQLite vector index.
- Retrieves top-k semantically similar chunks for a question.
- Generates a grounded answer with retrieved source chunks.
- Falls back to extractive answers when no LLM API key is configured.
- Refuses unsupported answers when retrieved context is weak.
- Provides FastAPI endpoints and a simple browser UI.

## Why It Matters

RAG systems are useful when answers need to be grounded in a known document collection instead of relying only on a language model's general knowledge. This project demonstrates the core pieces in a small, readable codebase that can be extended and reviewed.

## Tech Stack

- Python
- FastAPI
- SQLite
- sentence-transformers
- Optional OpenAI-compatible or Anthropic LLM calls
- HTML, CSS, and JavaScript frontend
- pytest
- GitHub Actions

## Features

- `POST /ingest`: ingest a local file or folder.
- `POST /ingest/upload`: upload and ingest one document from the UI.
- `POST /query`: retrieve context and answer a question.
- `GET /health`: check service and indexed chunk count.
- `GET /documents`: list indexed documents.
- Citation display with document name, chunk index, text, and similarity score.
- No paid API required for retrieval.

## Architecture

```text
Documents (.txt, .md, .pdf)
        |
        v
Text extraction and cleaning
        |
        v
Overlapping chunking
        |
        v
Local embeddings
        |
        v
SQLite vector store
        |
        v
Semantic retrieval
        |
        v
Grounded answer generation
        |
        v
Answer + source citations
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python run.py
```

Open `http://127.0.0.1:8000` in a browser.

On macOS/Linux, activate the virtual environment with:

```bash
source .venv/bin/activate
```

## Example Queries

After ingesting `data/sample_docs`, try:

- What does this project demonstrate?
- Can this run without paid APIs?
- What happens when the documents do not support an answer?

## Screenshots

Screenshots will be added after the UI is run and captured with non-private sample data.

## Responsible AI and Limitations

- The system should answer only from retrieved document context.
- If context is weak, it returns that the answer was not found in the documents.
- Local retrieval quality depends on chunking, embedding quality, and document content.
- Optional LLM generation can still make mistakes, so source citations should be reviewed.
- This starter project is not hardened for multi-user production use.

## Future Improvements

- Add ChromaDB or FAISS as a selectable backend.
- Add deduplication, deletion, and re-indexing controls.
- Add stronger evaluation tests for answer faithfulness.
- Add streaming responses and richer citation formatting.
- Add Docker packaging.
- Add screenshots and a short demo GIF using public sample documents.

## No-Secrets Note

Do not commit `.env`, API keys, tokens, credentials, private documents, generated databases, logs, uploads, generated PDFs, or personal data. Use `.env.example` only for placeholder variable names.
