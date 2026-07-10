from app.embeddings import HashingEmbedder
from app.rag import NOT_FOUND_MESSAGE, RAGPipeline
from app.retrieval import Retriever
from app.vector_store import SQLiteVectorStore


def test_retrieval_returns_relevant_chunk(tmp_path):
    embedder = HashingEmbedder()
    store = SQLiteVectorStore(tmp_path / "rag.sqlite3")
    chunks = [
        {"source": "a.txt", "document_name": "a.txt", "chunk_index": 0, "text": "Python powers FastAPI services.", "start_char": 0, "end_char": 32},
        {"source": "b.txt", "document_name": "b.txt", "chunk_index": 0, "text": "Tomatoes grow in sunny gardens.", "start_char": 0, "end_char": 32},
    ]
    store.add_chunks(chunks, embedder.embed_texts([chunk["text"] for chunk in chunks]))
    results = Retriever(embedder, store).retrieve("FastAPI Python", top_k=1)
    assert results[0]["document_name"] == "a.txt"


def test_unsupported_question_returns_not_found(tmp_path):
    embedder = HashingEmbedder()
    store = SQLiteVectorStore(tmp_path / "rag.sqlite3")
    chunks = [
        {"source": "a.txt", "document_name": "a.txt", "chunk_index": 0, "text": "The index contains notes about FastAPI.", "start_char": 0, "end_char": 41}
    ]
    store.add_chunks(chunks, embedder.embed_texts([chunk["text"] for chunk in chunks]))
    rag = RAGPipeline(Retriever(embedder, store), min_relevance_score=0.9)
    response = rag.answer("What is the capital of Iceland?")
    assert response["answer"] == NOT_FOUND_MESSAGE
    assert response["is_supported"] is False
