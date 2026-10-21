from __future__ import annotations

import hashlib
import math
import warnings
import re
from typing import Protocol


class Embedder(Protocol):
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        ...

    def embed_query(self, text: str) -> list[float]:
        ...


class SentenceTransformerEmbedder:
    def __init__(self, model_name: str):
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(model_name)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        vectors = self.model.encode(texts, normalize_embeddings=True)
        return [vector.tolist() for vector in vectors]

    def embed_query(self, text: str) -> list[float]:
        return self.embed_texts([text])[0]


class HashingEmbedder:
    """Small deterministic fallback for tests/offline demos when model files are unavailable."""

    def __init__(self, dimensions: int = 384):
        self.dimensions = dimensions

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_query(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        tokens = re.findall(r"[a-z0-9]+", text.lower())
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]


def get_embedder(model_name: str) -> Embedder:
    if model_name == "hashing":
        return HashingEmbedder()
    try:
        return SentenceTransformerEmbedder(model_name)
    except Exception as exc:
        warnings.warn(f"Semantic embedding model unavailable ({type(exc).__name__}); using lexical hashing embeddings.", RuntimeWarning)
        return HashingEmbedder()
