import sqlite3
import pytest
from app.vector_store import SQLiteVectorStore


def test_operations_close_database_connections(tmp_path, monkeypatch):
    original = sqlite3.connect
    connections = []
    def connect(*args, **kwargs):
        connection = original(*args, **kwargs)
        connections.append(connection)
        return connection
    monkeypatch.setattr(sqlite3, "connect", connect)
    store = SQLiteVectorStore(tmp_path / "test.sqlite3")
    assert store.count_chunks() == 0
    for connection in connections:
        with pytest.raises(sqlite3.ProgrammingError, match="closed"):
            connection.execute("SELECT 1")
