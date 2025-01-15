from __future__ import annotations

import logging

from apscheduler.schedulers.background import BackgroundScheduler

from connectors.factory import create_connectors
from core.settings import AppConfig
from ingestion.pipeline import IngestionPipeline

logger = logging.getLogger(__name__)


def register_jobs(scheduler: BackgroundScheduler, pipeline: IngestionPipeline, config: AppConfig) -> None:
    connectors = create_connectors()

    connector_config_map = {
        "reddit": config.connectors.reddit,
        "telegram": config.connectors.telegram,
        "devpost": config.connectors.devpost,
        "x": config.connectors.x,
        "linkedin": config.connectors.linkedin,
    }

    for name, connector in connectors.items():
        cfg = connector_config_map[name]
        if not cfg.enabled:
            continue
        if cfg.interval_minutes is None:
            continue

        def run_connector(connector_name: str = name) -> None:
            docs = connectors[connector_name].fetch()
            stats = pipeline.upsert_documents(docs)
            logger.info("indexed connector=%s stats=%s", connector_name, stats)

        scheduler.add_job(
            run_connector,
            "interval",
            minutes=cfg.interval_minutes,
            id=f"index_{name}",
            replace_existing=True,
        )
