import json
import sqlite3

from core.parser import parse_query
from core.vector import search_vectors


def test_semantic_retrieval_prefers_similar_vector() -> None:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript(
        """
        CREATE TABLE documents (
            id TEXT PRIMARY KEY,
            platform TEXT,
            title TEXT,
            body TEXT,
            author TEXT,
            url TEXT,
            created_at TEXT,
            tags TEXT
        );
        CREATE TABLE embeddings (
            doc_id TEXT PRIMARY KEY,
            dimension INTEGER,
            vector TEXT
        );
        """
    )

    conn.execute(
        "INSERT INTO documents VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        ("reddit:t3_a", "reddit", "ML role", "machine learning role", "alice", "https://a", "2026-08-10", "[]"),
    )
    conn.execute(
        "INSERT INTO documents VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        ("reddit:t3_b", "reddit", "Frontend role", "react ui role", "bob", "https://b", "2026-08-10", "[]"),
    )
    conn.execute(
        "INSERT INTO embeddings VALUES (?, ?, ?)",
        ("reddit:t3_a", 3, json.dumps([1.0, 0.0, 0.0])),
    )
    conn.execute(
        "INSERT INTO embeddings VALUES (?, ?, ?)",
        ("reddit:t3_b", 3, json.dumps([0.0, 1.0, 0.0])),
    )

    rows = search_vectors(conn, parse_query("ml"), [0.9, 0.1, 0.0], limit=2)
    assert rows[0]["id"] == "reddit:t3_a"
