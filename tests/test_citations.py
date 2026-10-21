from app.rag import RAGPipeline


def test_extractive_citations_only_include_the_quoted_document(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "")
    sources = [
        {"document_name": "refunds", "text": "Refunds take 30 days.", "score": 0.9},
        {"document_name": "shipping", "text": "Shipping takes five days.", "score": 0.4},
    ]
    class Retriever:
        def retrieve(self, question, top_k):
            return sources
    result = RAGPipeline(Retriever()).answer("How many days do refunds take?")
    assert result["sources"] == sources[:1]
    assert "Shipping" not in result["answer"]
