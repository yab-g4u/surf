from __future__ import annotations

import re
from datetime import datetime

from core.schema import ParsedQuery

_PHRASE_RE = re.compile(r'"([^"]+)"')


def parse_query(query: str) -> ParsedQuery:
    working = query.strip()
    phrases = _PHRASE_RE.findall(working)
    working = _PHRASE_RE.sub("", working)

    filters: dict[str, str] = {}
    excluded_terms: list[str] = []
    free_terms: list[str] = []

    for token in working.split():
        if token.startswith("-") and len(token) > 1:
            excluded_terms.append(token[1:])
            continue
        if ":" in token:
            key, value = token.split(":", 1)
            if key in {"platform", "author", "tag", "after", "before"} and value:
                filters[key] = value
                continue
        free_terms.append(token)

    parsed = ParsedQuery(
        text=" ".join(free_terms).strip(),
        phrases=phrases,
        excluded_terms=excluded_terms,
        platform=filters.get("platform"),
        author=filters.get("author"),
        tag=filters.get("tag"),
    )

    if "after" in filters:
        parsed.after = datetime.fromisoformat(filters["after"])
    if "before" in filters:
        parsed.before = datetime.fromisoformat(filters["before"])

    return parsed
