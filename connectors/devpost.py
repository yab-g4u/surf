from __future__ import annotations

from datetime import datetime, timezone

from core.schema import Document
from connectors.base import BaseConnector


class DevpostConnector(BaseConnector):
    name = "devpost"
    access_mode = "api"

    def fetch(self) -> list[Document]:
        now = datetime.now(timezone.utc)
        hackathon_doc = Document(
            id="devpost:hackathon_demo_2026",
            platform="devpost",
            title="Robotics + AI Global Hackathon",
            body=(
                "Join teams building robotics and AI systems. "
                "Prizes include hardware grants and mentorship."
            ),
            author="Devpost Organizer",
            author_url=None,
            url="https://devpost.com/hackathons/robotics-ai-global",
            created_at=now,
            fetched_at=now,
            tags=["hackathon", "robotics", "ai"],
            metadata={
                "entity_type": "hackathon",
                "deadline": "2026-09-01",
                "location": "remote",
                "technologies": ["python", "computer-vision", "robotics"],
                "prizes": "$25,000",
            },
            raw_payload={"kind": "hackathon"},
            content_hash="",
        )
        return [hackathon_doc]
