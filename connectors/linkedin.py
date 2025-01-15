from __future__ import annotations

from datetime import datetime, timezone

from core.schema import Document
from connectors.base import BaseConnector


class LinkedInImportConnector(BaseConnector):
    name = "linkedin"
    access_mode = "import"

    def fetch(self) -> list[Document]:
        now = datetime.now(timezone.utc)
        sample = Document(
            id="linkedin:import_demo_1",
            platform="linkedin",
            title="ML Engineer - Remote",
            body="Imported listing from user-provided LinkedIn export.",
            author="Example Company",
            author_url=None,
            url="https://www.linkedin.com/jobs/view/import_demo_1",
            created_at=now,
            fetched_at=now,
            tags=["job", "ml", "remote"],
            metadata={"source": "user_import"},
            raw_payload={"kind": "linkedin_import"},
            content_hash="",
        )
        return [sample]
