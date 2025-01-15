from __future__ import annotations

import json
import sqlite3

from core.database import Database
from core.embeddings import Embedder
from core.schema import Document
from ingestion.deduplicate import compute_content_hash


class IngestionPipeline:
    def __init__(self, db: Database, embedder: Embedder) -> None:
        self.db = db
        self.embedder = embedder

    def upsert_documents(self, documents: list[Document]) -> dict[str, int]:
        inserted = 0
        updated = 0
        embedded = 0

        conn = self.db.transaction()
        with conn:
            for doc in documents:
                doc.content_hash = compute_content_hash(doc)
                existing = conn.execute(
                    "SELECT content_hash FROM documents WHERE id = ?",
                    (doc.id,),
                ).fetchone()

                needs_embedding = True
                if existing and existing["content_hash"] == doc.content_hash:
                    needs_embedding = False
                elif existing:
                    updated += 1
                else:
                    inserted += 1

                conn.execute(
                    """
                    INSERT INTO documents (
                        id, platform, title, body, author, author_url, url,
                        created_at, fetched_at, tags, metadata, raw_payload, content_hash, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                    ON CONFLICT(id) DO UPDATE SET
                        platform=excluded.platform,
                        title=excluded.title,
                        body=excluded.body,
                        author=excluded.author,
                        author_url=excluded.author_url,
                        url=excluded.url,
                        created_at=excluded.created_at,
                        fetched_at=excluded.fetched_at,
                        tags=excluded.tags,
                        metadata=excluded.metadata,
                        raw_payload=excluded.raw_payload,
                        content_hash=excluded.content_hash,
                        updated_at=datetime('now')
                    """,
                    (
                        doc.id,
                        doc.platform,
                        doc.title,
                        doc.body,
                        doc.author,
                        str(doc.author_url) if doc.author_url else None,
                        str(doc.url),
                        doc.created_at.isoformat() if doc.created_at else None,
                        doc.fetched_at.isoformat(),
                        Database.dumps_json(doc.tags),
                        Database.dumps_json(doc.metadata),
                        Database.dumps_json(doc.raw_payload),
                        doc.content_hash,
                    ),
                )

                conn.execute("DELETE FROM documents_fts WHERE id = ?", (doc.id,))
                conn.execute(
                    "INSERT INTO documents_fts (id, title, body, author) VALUES (?, ?, ?, ?)",
                    (doc.id, doc.title or "", doc.body, doc.author or ""),
                )

                if needs_embedding:
                    vector = self.embedder.encode([f"{doc.title or ''}\n{doc.body}"])[0]
                    conn.execute(
                        """
                        INSERT INTO embeddings (doc_id, dimension, vector, updated_at)
                        VALUES (?, ?, ?, datetime('now'))
                        ON CONFLICT(doc_id) DO UPDATE SET
                            dimension=excluded.dimension,
                            vector=excluded.vector,
                            updated_at=datetime('now')
                        """,
                        (doc.id, len(vector), json.dumps(vector, separators=(",", ":"))),
                    )
                    embedded += 1

        return {"inserted": inserted, "updated": updated, "embedded": embedded}
