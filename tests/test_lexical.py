import sqlite3

from core.lexical import search_fts
from core.parser import parse_query


def test_keyword_search_returns_expected() -> None:
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

        CREATE VIRTUAL TABLE documents_fts USING fts5(
            id UNINDEXED,
            title,
            body,
            author
        );
        """
    )
    conn.execute(
        "INSERT INTO documents VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            "reddit:t3_1",
            "reddit",
            "Remote AI Engineer",
            "Hiring remote ML engineers",
            "alice",
            "https://example.com",
            "2026-08-10T00:00:00",
            "[\"ai\"]",
        ),
    )
    conn.execute(
        "INSERT INTO documents_fts (id, title, body, author) VALUES (?, ?, ?, ?)",
        ("reddit:t3_1", "Remote AI Engineer", "Hiring remote ML engineers", "alice"),
    )

    rows = search_fts(conn, parse_query("AI engineer"), limit=10)
    assert rows
    assert rows[0]["id"] == "reddit:t3_1"
