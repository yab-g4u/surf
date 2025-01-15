from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class DatabaseConfig(BaseModel):
    path: str = "./data/search.db"


class EmbeddingsConfig(BaseModel):
    model: str = "sentence-transformers/all-MiniLM-L6-v2"
    dimension: int = 384


class SearchConfig(BaseModel):
    bm25_limit: int = 50
    vector_limit: int = 50
    rrf_k: int = 60


class ConnectorScheduleConfig(BaseModel):
    enabled: bool = False
    interval_minutes: int | None = None
    access_mode: str = "api"


class ConnectorConfig(BaseModel):
    reddit: ConnectorScheduleConfig = Field(
        default_factory=lambda: ConnectorScheduleConfig(enabled=True, interval_minutes=30, access_mode="api")
    )
    telegram: ConnectorScheduleConfig = Field(
        default_factory=lambda: ConnectorScheduleConfig(enabled=True, interval_minutes=10, access_mode="api")
    )
    devpost: ConnectorScheduleConfig = Field(
        default_factory=lambda: ConnectorScheduleConfig(enabled=True, interval_minutes=1440, access_mode="api")
    )
    x: ConnectorScheduleConfig = Field(
        default_factory=lambda: ConnectorScheduleConfig(enabled=False, interval_minutes=60, access_mode="import")
    )
    linkedin: ConnectorScheduleConfig = Field(
        default_factory=lambda: ConnectorScheduleConfig(enabled=False, interval_minutes=None, access_mode="import")
    )


class AppConfig(BaseModel):
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    embeddings: EmbeddingsConfig = Field(default_factory=EmbeddingsConfig)
    search: SearchConfig = Field(default_factory=SearchConfig)
    connectors: ConnectorConfig = Field(default_factory=ConnectorConfig)


def load_config(config_path: str | Path = "config/config.yaml") -> AppConfig:
    path = Path(config_path)
    if not path.exists():
        return AppConfig()

    data: dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return AppConfig.model_validate(data)
