# Project Status

## Current Build Status

Starter implementation complete locally. The project includes a FastAPI API, simple browser UI, local embedding retrieval path, SQLite-backed vector storage, tests, and GitHub Actions configuration.

## Completed Features

- Document folder ingestion for `.txt`, `.md`, and `.pdf` files.
- Upload endpoint and UI for individual documents.
- Text cleaning and overlapping chunking.
- Local sentence-transformers embeddings by default, with deterministic offline fallback.
- SQLite vector storage with cosine similarity retrieval.
- RAG response path with citation/source chunks.
- Extractive grounded answer fallback when no LLM key is configured.
- Basic unsupported-question guard when retrieved context is weak.
- FastAPI endpoints: `POST /ingest`, `POST /query`, `GET /health`, and `GET /documents`.
- Simple HTML/CSS/JavaScript frontend.
- Pytest coverage for chunking, retrieval, unsupported question behavior, and API health.
- GitHub Actions workflow for tests.

## Remaining Improvements

- Add duplicate-document handling or re-index controls.
- Add richer PDF extraction tests with non-private fixture PDFs.
- Add optional ChromaDB or FAISS backend behind the same retrieval interface.
- Add streaming LLM responses and stronger citation formatting.
- Add screenshots after the app is run and visually verified.

## What Needs Testing Before Making Public

- Run the app on a fresh machine and confirm model download behavior.
- Test with a small public PDF fixture.
- Verify API responses with multiple uploaded files.
- Confirm GitHub Actions passes in the repository environment.
- Review README screenshots after real UI screenshots are added.

## What Must Not Be Committed

- `.env` or `.env.*` files.
- API keys, tokens, credentials, or passwords.
- Private documents or personal data.
- SQLite/vector database files.
- Upload folders, generated outputs, logs, or PDFs.
- `chroma_db/`, `uploads/`, `secrets/`, and `credentials/`.
