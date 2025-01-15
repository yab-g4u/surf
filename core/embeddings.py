from __future__ import annotations

from abc import ABC, abstractmethod

from sentence_transformers import SentenceTransformer


class Embedder(ABC):
    @abstractmethod
    def encode(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError


class SentenceTransformerEmbedder(Embedder):
    def __init__(self, model_name: str) -> None:
        self.model = SentenceTransformer(model_name)

    def encode(self, texts: list[str]) -> list[list[float]]:
        vectors = self.model.encode(texts, normalize_embeddings=True)
        return [list(map(float, vector)) for vector in vectors]
