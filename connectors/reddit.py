from __future__ import annotations

from datetime import datetime, timezone

from core.schema import Document
from connectors.base import BaseConnector


class RedditConnector(BaseConnector):
    name = "reddit"
    access_mode = "api"

    def fetch(self) -> list[Document]:
        now = datetime.now(timezone.utc)
        sample = Document(
            id="reddit:t3_demo1",
            platform="reddit",
            title="Looking for ML engineers",
            body="We are hiring remote machine learning engineers in East Africa.",
            author="reddit_user",
            author_url="https://www.reddit.com/user/reddit_user",
            url="https://www.reddit.com/r/MachineLearning/comments/demo1/looking_for_ml_engineers/",
            created_at=now,
            fetched_at=now,
            tags=["MachineLearning", "Hiring"],
            metadata={"subreddit": "MachineLearning", "post_id": "t3_demo1"},
            raw_payload={"kind": "t3"},
            content_hash="",
        )
        return [sample]
