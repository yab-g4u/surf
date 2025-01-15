from __future__ import annotations

from datetime import datetime, timezone

from core.schema import Document
from connectors.base import BaseConnector


class TelegramConnector(BaseConnector):
    name = "telegram"
    access_mode = "api"

    def fetch(self) -> list[Document]:
        now = datetime.now(timezone.utc)
        sample = Document(
            id="telegram:1001",
            platform="telegram",
            title="AI Internship Thread",
            body="Sharing AI and ML internship opportunities this week.",
            author="channel_admin",
            author_url=None,
            url="https://t.me/s/example/1001",
            created_at=now,
            fetched_at=now,
            tags=["internship", "ai"],
            metadata={"channel": "example", "message_id": 1001, "incremental": True},
            raw_payload={"source": "telegram_api"},
            content_hash="",
        )
        return [sample]
