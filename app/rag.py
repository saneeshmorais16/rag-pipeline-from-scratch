from __future__ import annotations

import os
import re


NOT_FOUND_MESSAGE = "I could not find an answer supported by the ingested documents."


class RAGPipeline:
    def __init__(self, retriever, min_relevance_score: float = 0.18):
        self.retriever = retriever
        self.min_relevance_score = min_relevance_score

    def answer(self, question: str, top_k: int = 4) -> dict:
        sources = self.retriever.retrieve(question, top_k=top_k)
        strong_sources = [source for source in sources if source["score"] >= self.min_relevance_score]
        if not strong_sources:
            return {"answer": NOT_FOUND_MESSAGE, "sources": sources, "is_supported": False}

        llm_answer = self._try_llm_answer(question, strong_sources)
        if llm_answer:
            return {"answer": llm_answer, "sources": strong_sources, "is_supported": True}

        # The extractive fallback quotes only its highest-ranked document.
        # Cite exactly that document, rather than attaching unused retrieval hits.
        extractive_sources = strong_sources[:1]
        return {
            "answer": self._extractive_answer(question, extractive_sources),
            "sources": extractive_sources,
            "is_supported": True,
        }

    def _try_llm_answer(self, question: str, sources: list[dict]) -> str:
        provider = os.getenv("LLM_PROVIDER", "").lower().strip()
        if provider == "openai" and os.getenv("OPENAI_API_KEY"):
            return self._openai_answer(question, sources)
        if provider == "anthropic" and os.getenv("ANTHROPIC_API_KEY"):
            return self._anthropic_answer(question, sources)
        return ""

    def _openai_answer(self, question: str, sources: list[dict]) -> str:
        try:
            from openai import OpenAI
        except ImportError:
            return ""
        client = OpenAI()
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": _system_prompt()},
                {"role": "user", "content": _user_prompt(question, sources)},
            ],
            temperature=0,
        )
        return response.choices[0].message.content or ""

    def _anthropic_answer(self, question: str, sources: list[dict]) -> str:
        try:
            import anthropic
        except ImportError:
            return ""
        client = anthropic.Anthropic()
        response = client.messages.create(
            model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-latest"),
            max_tokens=500,
            system=_system_prompt(),
            messages=[{"role": "user", "content": _user_prompt(question, sources)}],
        )
        return "\n".join(block.text for block in response.content if getattr(block, "type", "") == "text")

    def _extractive_answer(self, question: str, sources: list[dict]) -> str:
        question_terms = set(re.findall(r"[a-z0-9]+", question.lower()))
        sentences = []
        for source in sources:
            for sentence in re.split(r"(?<=[.!?])\s+", source["text"]):
                terms = set(re.findall(r"[a-z0-9]+", sentence.lower()))
                if question_terms & terms:
                    sentences.append(sentence.strip())
                if len(sentences) >= 3:
                    break
            if len(sentences) >= 3:
                break
        if not sentences:
            sentences = [sources[0]["text"][:500].strip()]
        return " ".join(sentences)


def _system_prompt() -> str:
    return (
        "Answer only from the provided document context. "
        "If the answer is not supported, say it is not found in the documents. "
        "Keep the answer concise and mention source chunk numbers when useful."
    )


def _user_prompt(question: str, sources: list[dict]) -> str:
    context = "\n\n".join(
        f"[{source['document_name']} chunk {source['chunk_index']} score {source['score']:.3f}]\n{source['text']}"
        for source in sources
    )
    return f"Question: {question}\n\nContext:\n{context}"
