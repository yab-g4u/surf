from datetime import datetime, timezone

from core.schema import Document
from ingestion.deduplicate import compute_content_hash


def make_document(body: str) -> Document:
    now = datetime.now(timezone.utc)
    return Document(
        id="reddit:t3_test",
        platform="reddit",
        title="Test",
        body=body,
        author="alice",
        author_url="https://example.com/alice",
        url="https://example.com/post",
        created_at=now,
        fetched_at=now,
        tags=["python"],
        metadata={"subreddit": "MachineLearning"},
        raw_payload={},
        content_hash="",
    )


def test_hash_changes_when_content_changes() -> None:
    h1 = compute_content_hash(make_document("hello"))
    h2 = compute_content_hash(make_document("hello world"))
    assert h1 != h2
