from __future__ import annotations

from typing import Any

from core.embeddings import Embedder
from core.fusion import rrf
from core.lexical import search_fts
from core.parser import parse_query
from core.schema import SearchResult
from core.settings import SearchConfig
from core.vector import search_vectors


class SearchService:
    def __init__(self, conn, embedder: Embedder, config: SearchConfig) -> None:
        self.conn = conn
        self.embedder = embedder
        self.config = config

    def search(self, query: str) -> list[SearchResult]:
        parsed = parse_query(query)

        lexical_rows = search_fts(self.conn, parsed, self.config.bm25_limit)
        query_vector = self.embedder.encode([query])[0]
        vector_rows = search_vectors(self.conn, parsed, query_vector, self.config.vector_limit)

        lexical_ids = [row["id"] for row in lexical_rows]
        vector_ids = [row["id"] for row in vector_rows]
        fused = rrf([lexical_ids, vector_ids], k=self.config.rrf_k)

        by_id: dict[str, dict[str, Any]] = {}
        for row in lexical_rows + vector_rows:
            by_id[row["id"]] = row

        ranked = sorted(fused.items(), key=lambda item: item[1], reverse=True)
        results: list[SearchResult] = []
        for doc_id, score in ranked:
            row = by_id[doc_id]
            snippet = (row.get("body") or "")[:240]
            results.append(
                SearchResult(
                    id=row["id"],
                    platform=row["platform"],
                    title=row.get("title"),
                    snippet=snippet,
                    author=row.get("author"),
                    url=row["url"],
                    created_at=row.get("created_at"),
                    score=score,
                )
            )
        return results
