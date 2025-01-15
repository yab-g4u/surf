from __future__ import annotations

import sqlite3
from typing import Any

from core.schema import ParsedQuery


def _build_fts_query(parsed: ParsedQuery) -> str:
    parts: list[str] = []

    if parsed.text:
        parts.extend(parsed.text.split())
    for phrase in parsed.phrases:
        parts.append(f'"{phrase}"')
    for term in parsed.excluded_terms:
        parts.append(f"NOT {term}")

    return " ".join(parts) if parts else "*"


def search_fts(conn: sqlite3.Connection, parsed: ParsedQuery, limit: int) -> list[dict[str, Any]]:
    fts_query = _build_fts_query(parsed)

    if fts_query == "*":
        sql = """
        SELECT d.id,
               d.platform,
               d.title,
               d.body,
               d.author,
               d.url,
               d.created_at,
               0.0 AS bm25_score
        FROM documents d
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

        sql += " ORDER BY d.created_at DESC LIMIT ?"
        params.append(limit)
        rows = conn.execute(sql, params).fetchall()
        return [dict(row) for row in rows]

    sql = """
    SELECT d.id,
           d.platform,
           d.title,
           d.body,
           d.author,
           d.url,
           d.created_at,
           bm25(documents_fts) AS bm25_score
    FROM documents_fts
    JOIN documents d ON d.id = documents_fts.id
    WHERE documents_fts MATCH ?
    """
    params: list[Any] = [fts_query]

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

    sql += " ORDER BY bm25_score LIMIT ?"
    params.append(limit)

    rows = conn.execute(sql, params).fetchall()
    return [dict(row) for row in rows]
