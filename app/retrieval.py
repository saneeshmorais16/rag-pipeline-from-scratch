from app.embeddings import Embedder
from app.vector_store import SQLiteVectorStore


class Retriever:
    def __init__(self, embedder: Embedder, vector_store: SQLiteVectorStore):
        self.embedder = embedder
        self.vector_store = vector_store

    def retrieve(self, question: str, top_k: int = 4) -> list[dict]:
        query_embedding = self.embedder.embed_query(question)
        return self.vector_store.search(query_embedding, top_k=top_k)
