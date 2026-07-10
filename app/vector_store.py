from __future__ import annotations

import json
import math
import sqlite3
from pathlib import Path


class SQLiteVectorStore:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def add_chunks(self, chunks: list[dict], embeddings: list[list[float]]) -> int:
        rows = []
        for chunk, embedding in zip(chunks, embeddings, strict=True):
            rows.append(
                (
                    chunk["source"],
                    chunk["document_name"],
                    chunk["chunk_index"],
                    chunk["text"],
                    chunk["start_char"],
                    chunk["end_char"],
                    json.dumps(embedding),
                )
            )
        with self._connect() as conn:
            conn.executemany(
                """
                INSERT INTO chunks
                (source, document_name, chunk_index, text, start_char, end_char, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )
        return len(rows)

    def search(self, query_embedding: list[float], top_k: int = 4) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, source, document_name, chunk_index, text, start_char, end_char, embedding FROM chunks"
            ).fetchall()
        scored = []
        for row in rows:
            embedding = json.loads(row["embedding"])
            scored.append(
                {
                    "id": row["id"],
                    "source": row["source"],
                    "document_name": row["document_name"],
                    "chunk_index": row["chunk_index"],
                    "text": row["text"],
                    "start_char": row["start_char"],
                    "end_char": row["end_char"],
                    "score": cosine_similarity(query_embedding, embedding),
                }
            )
        return sorted(scored, key=lambda item: item["score"], reverse=True)[:top_k]

    def documents(self) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT source, document_name, COUNT(*) AS chunks
                FROM chunks
                GROUP BY source, document_name
                ORDER BY document_name
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def count_chunks(self) -> int:
        with self._connect() as conn:
            return int(conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0])

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    document_name TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    start_char INTEGER NOT NULL,
                    end_char INTEGER NOT NULL,
                    embedding TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    dot = sum(a * b for a, b in zip(left, right, strict=True))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)
