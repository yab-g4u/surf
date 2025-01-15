from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, HttpUrl


class Document(BaseModel):
    id: str
    platform: str
    title: str | None = None
    body: str
    author: str | None = None
    author_url: HttpUrl | None = None
    url: HttpUrl
    created_at: datetime | None = None
    fetched_at: datetime
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    raw_payload: dict[str, Any] = Field(default_factory=dict)
    content_hash: str


class ParsedQuery(BaseModel):
    text: str
    phrases: list[str] = Field(default_factory=list)
    excluded_terms: list[str] = Field(default_factory=list)
    platform: str | None = None
    author: str | None = None
    tag: str | None = None
    after: datetime | None = None
    before: datetime | None = None


class SearchResult(BaseModel):
    id: str
    platform: str
    title: str | None = None
    snippet: str
    author: str | None = None
    url: HttpUrl
    created_at: datetime | None = None
    score: float
