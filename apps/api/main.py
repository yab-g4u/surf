from __future__ import annotations

from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from connectors.factory import create_connectors
from core.database import Database
from core.embeddings import SentenceTransformerEmbedder
from core.search import SearchService
from core.settings import load_config
from ingestion.pipeline import IngestionPipeline
from scheduler.jobs import register_jobs

config = load_config()
db = Database(config.database.path)
db.initialize(config.embeddings.dimension)
embedder = SentenceTransformerEmbedder(config.embeddings.model)
search_service = SearchService(db.conn, embedder, config.search)
pipeline = IngestionPipeline(db, embedder)
connectors = create_connectors()
scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(_: FastAPI):
    register_jobs(scheduler, pipeline, config)
    scheduler.start()
    yield
    scheduler.shutdown(wait=False)


app = FastAPI(title="Surf Local Search", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/index/{connector_name}")
def index_connector(connector_name: str) -> dict:
    if connector_name == "all":
        aggregate = {"inserted": 0, "updated": 0, "embedded": 0}
        for connector in connectors.values():
            stats = pipeline.upsert_documents(connector.fetch())
            for key in aggregate:
                aggregate[key] += stats[key]
        return {"connector": "all", "stats": aggregate}

    connector = connectors.get(connector_name)
    if connector is None:
        return {"error": f"unknown connector: {connector_name}"}

    stats = pipeline.upsert_documents(connector.fetch())
    return {"connector": connector_name, "stats": stats}


@app.get("/api/search")
def search(q: str = Query(..., min_length=1)) -> dict:
    results = search_service.search(q)
    return {
        "query": q,
        "total": len(results),
        "results": [result.model_dump(mode="json") for result in results],
    }


@app.get("/api/stats")
def stats() -> dict:
    row = db.conn.execute("SELECT COUNT(*) AS count FROM documents").fetchone()
    total_docs = row["count"] if row else 0

    rows = db.conn.execute(
        "SELECT platform, COUNT(*) AS count FROM documents GROUP BY platform ORDER BY count DESC"
    ).fetchall()

    by_platform = {r["platform"]: r["count"] for r in rows}
    emb_row = db.conn.execute("SELECT COUNT(*) AS count FROM embeddings").fetchone()
    embeddings = emb_row["count"] if emb_row else 0

    return {
        "documents": total_docs,
        "by_platform": by_platform,
        "embeddings": embeddings,
        "database_path": config.database.path,
    }
