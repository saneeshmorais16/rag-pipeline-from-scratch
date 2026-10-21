# RAG Pipeline From Scratch

[Verification record](docs/VERIFICATION.md) · [Measured evaluation](docs/EVALUATION.md) · [Local demo](docs/DEMO.md)

![Local demo using synthetic data](docs/demo.jpg)

A portfolio-ready starter Retrieval-Augmented Generation pipeline that demonstrates document ingestion, chunking, local embeddings, vector search, retrieval, grounded answer generation, citations, and a simple API/UI.

This project is intentionally honest: it is a clean in-progress implementation, not a production RAG platform. It is designed to show the core engineering path clearly and safely.

## What It Does

- Ingests `.txt`, `.md`, and optionally `.pdf` documents.
- Cleans and chunks document text.
- Generates local sentence-transformers embeddings by default.
- Stores chunks and embeddings in a local SQLite vector index.
- Retrieves top-k semantically similar chunks for a question.
- Produces an extractive answer from the highest-ranked document, or an optional LLM answer from retrieved chunks.
- Falls back to extractive answers when no LLM API key is configured.
- Rejects low-similarity queries; similarity alone does not prove that a question is answerable.
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

Use Python 3.12. Run these commands from the repository root in a fresh virtual environment.

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

See [the local demo](docs/DEMO.md) for a captured ingestion and query session using the included sample document.

## Responsible AI and Limitations

- The system should answer only from retrieved document context.
- Low-scoring context triggers rejection, but in-domain unanswerable questions can still receive irrelevant answers. See the measured rejection rate in `docs/EVALUATION.md`.
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
