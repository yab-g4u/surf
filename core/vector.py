from __future__ import annotations

import json
import math
import sqlite3
from typing import Any

from core.schema import ParsedQuery


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


def search_vectors(
    conn: sqlite3.Connection,
    parsed: ParsedQuery,
    query_vector: list[float],
    limit: int,
) -> list[dict[str, Any]]:
    sql = """
    SELECT d.id,
           d.platform,
           d.title,
           d.body,
           d.author,
           d.url,
           d.created_at,
           e.vector
    FROM embeddings e
    JOIN documents d ON d.id = e.doc_id
    WHERE 1=1
    """
    params: list[Any] = []

    if parsed.platform:
        sql += " AND d.platform = ?"
        params.append(parsed.platform)
    if parsed.author:
        sql += " AND d.author = ?"
        params.append(parsed.author)
    if parsed.tag:
        sql += " AND d.tags LIKE ?"
        params.append(f"%{parsed.tag}%")
    if parsed.after:
        sql += " AND d.created_at >= ?"
        params.append(parsed.after.isoformat())
    if parsed.before:
        sql += " AND d.created_at <= ?"
        params.append(parsed.before.isoformat())

    rows = conn.execute(sql, params).fetchall()

    scored: list[dict[str, Any]] = []
    for row in rows:
        row_dict = dict(row)
        vector = json.loads(row_dict.pop("vector"))
        row_dict["vector_score"] = _cosine_similarity(query_vector, vector)
        scored.append(row_dict)

    scored.sort(key=lambda item: item["vector_score"], reverse=True)
    return scored[:limit]
