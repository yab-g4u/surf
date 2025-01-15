from __future__ import annotations

from datetime import datetime, timezone

from core.schema import Document
from connectors.base import BaseConnector


class XConnector(BaseConnector):
    name = "x"
    access_mode = "import"

    def fetch(self) -> list[Document]:
        now = datetime.now(timezone.utc)
        sample = Document(
            id="x:demo_1",
            platform="x",
            title=None,
            body="Hiring backend AI engineers for remote-first startup.",
            author="x_author",
            author_url="https://x.com/x_author",
            url="https://x.com/x_author/status/demo_1",
            created_at=now,
            fetched_at=now,
            tags=["hiring", "backend", "ai"],
            metadata={"hashtags": ["#AI", "#Backend"], "engagement": {"likes": 10}},
            raw_payload={"source": "import"},
            content_hash="",
        )
        return [sample]
