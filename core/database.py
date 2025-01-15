from __future__ import annotations

import json
import sqlite3
from pathlib import Path


class Database:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._enable_extensions()

    def _enable_extensions(self) -> None:
        try:
            self.conn.enable_load_extension(True)
            self.conn.execute("SELECT load_extension('sqlite_vec')")
        except sqlite3.DatabaseError:
            # sqlite-vec may not be available in all environments; fallback path still works.
            pass
        finally:
            try:
                self.conn.enable_load_extension(False)
            except sqlite3.DatabaseError:
                pass

    def initialize(self, embedding_dimension: int) -> None:
        self.conn.executescript(
            """
            PRAGMA journal_mode=WAL;

            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                platform TEXT NOT NULL,
                title TEXT,
                body TEXT NOT NULL,
                author TEXT,
                author_url TEXT,
                url TEXT NOT NULL,
                created_at TEXT,
                fetched_at TEXT NOT NULL,
                tags TEXT NOT NULL,
                metadata TEXT NOT NULL,
                raw_payload TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
                id UNINDEXED,
                title,
                body,
                author,
                tokenize='porter unicode61'
            );

            CREATE TABLE IF NOT EXISTS embeddings (
                doc_id TEXT PRIMARY KEY,
                dimension INTEGER NOT NULL,
                vector TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY(doc_id) REFERENCES documents(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_documents_platform ON documents(platform);
            CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at);
            CREATE INDEX IF NOT EXISTS idx_documents_author ON documents(author);
            """
        )
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS embedding_metadata (
                singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
                dimension INTEGER NOT NULL
            )
            """
        )
        self.conn.execute(
            "INSERT OR REPLACE INTO embedding_metadata(singleton, dimension) VALUES (1, ?)",
            (embedding_dimension,),
        )
        self.conn.commit()

    def transaction(self) -> sqlite3.Connection:
        return self.conn

    @staticmethod
    def dumps_json(value: object) -> str:
        return json.dumps(value, ensure_ascii=True, separators=(",", ":"))
