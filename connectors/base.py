from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from core.schema import Document


@dataclass(frozen=True)
class ConnectorContext:
    name: str


class BaseConnector(ABC):
    name: str
    access_mode: str

    @abstractmethod
    def fetch(self) -> list[Document]:
        raise NotImplementedError
