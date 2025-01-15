from __future__ import annotations

from connectors.base import BaseConnector
from connectors.devpost import DevpostConnector
from connectors.linkedin import LinkedInImportConnector
from connectors.reddit import RedditConnector
from connectors.telegram import TelegramConnector
from connectors.x import XConnector


def create_connectors() -> dict[str, BaseConnector]:
    connectors: list[BaseConnector] = [
        RedditConnector(),
        TelegramConnector(),
        DevpostConnector(),
        XConnector(),
        LinkedInImportConnector(),
    ]
    return {connector.name: connector for connector in connectors}
