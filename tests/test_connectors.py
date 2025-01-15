from connectors.devpost import DevpostConnector
from connectors.reddit import RedditConnector
from connectors.telegram import TelegramConnector


def test_reddit_normalization() -> None:
    docs = RedditConnector().fetch()
    assert docs
    doc = docs[0]
    assert doc.id.startswith("reddit:")
    assert doc.platform == "reddit"
    assert "subreddit" in doc.metadata


def test_telegram_normalization() -> None:
    docs = TelegramConnector().fetch()
    assert docs
    doc = docs[0]
    assert doc.id.startswith("telegram:")
    assert doc.platform == "telegram"


def test_devpost_normalization() -> None:
    docs = DevpostConnector().fetch()
    assert docs
    doc = docs[0]
    assert doc.id.startswith("devpost:")
    assert doc.metadata.get("entity_type") == "hackathon"
