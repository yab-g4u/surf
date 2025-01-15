from __future__ import annotations

import os
from typing import Annotated

import httpx
import typer

from core.database import Database
from core.settings import load_config

app = typer.Typer(help="Surf CLI for local hybrid search")


def _api_base() -> str:
    return os.getenv("SURF_API_BASE", "http://127.0.0.1:8000")


@app.command("search")
def search_cmd(
    query: str,
    platform: Annotated[str | None, typer.Option("--platform")] = None,
) -> None:
    q = query if not platform else f"platform:{platform} {query}"
    response = httpx.get(f"{_api_base()}/api/search", params={"q": q}, timeout=30)
    response.raise_for_status()
    payload = response.json()

    typer.echo(f"Query: {payload['query']}")
    typer.echo(f"Total: {payload['total']}")
    for item in payload["results"][:10]:
        typer.echo(f"- [{item['platform']}] {item.get('title') or '(no title)'}")
        typer.echo(f"  {item['url']}")


@app.command("index")
def index_cmd(connector: str = "all") -> None:
    response = httpx.post(f"{_api_base()}/api/index/{connector}", timeout=60)
    response.raise_for_status()
    payload = response.json()
    typer.echo(payload)


@app.command("init")
def init_cmd() -> None:
    config = load_config()
    db = Database(config.database.path)
    db.initialize(config.embeddings.dimension)
    typer.echo(f"Initialized local database at {config.database.path}")


@app.command("stats")
def stats_cmd() -> None:
    response = httpx.get(f"{_api_base()}/api/stats", timeout=30)
    response.raise_for_status()
    payload = response.json()
    typer.echo("Search Index")
    typer.echo("")
    typer.echo(f"Documents: {payload['documents']}")
    typer.echo("")
    for platform, count in payload["by_platform"].items():
        typer.echo(f"{platform.capitalize():<12} {count}")
    typer.echo("")
    typer.echo(f"Embeddings: {payload['embeddings']}")
    typer.echo(f"Database: {payload['database_path']}")


@app.command("serve")
def serve_cmd() -> None:
    typer.echo("Run API with: uvicorn apps.api.main:app --reload --port 8000")
    typer.echo("Run web with: cd apps/web && npm run dev")


if __name__ == "__main__":
    app()
