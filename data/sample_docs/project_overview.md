# RAG Pipeline From Scratch

This sample document describes a portfolio project that demonstrates document ingestion, text chunking, local embeddings, vector search, retrieval, grounded answer generation, and citation display.

The retrieval layer is designed to run without paid APIs. Local sentence-transformers embeddings are used by default, and answer generation can fall back to extractive answers when no LLM provider is configured.

The project intentionally treats unsupported questions cautiously. If retrieved context is weak, the system should say that the answer was not found in the documents.
