from __future__ import annotations

import asyncio
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .config import load_settings
from .memory import MemoryStore, MemoryUpdate
from .models import GenerationRequest
from .orchestrator import GenerationService
from .storage import read_json

app = typer.Typer(help="Multi-agent popular science generation")
memory_app = typer.Typer(help="User cognitive memory commands")
run_app = typer.Typer(help="Run inspection commands")
app.add_typer(memory_app, name="memory")
app.add_typer(run_app, name="run")
console = Console()


@app.command()
def generate(
    topic: str = typer.Option(..., "--topic", "-t", help="Science topic"),
    audience: str = typer.Option("general beginner", "--audience", "-a"),
    user_id: str = typer.Option("default", "--user-id", "-u"),
    style: str = typer.Option("clear, engaging popular science", "--style"),
    source_file: Path | None = typer.Option(None, "--source-file"),
    max_iterations: int | None = typer.Option(None, "--max-iterations"),
    backend: str | None = typer.Option(None, "--backend", help="mock or openai-compatible"),
    data_dir: Path | None = typer.Option(None, "--data-dir"),
) -> None:
    """Generate a text popular science article."""
    source_text = source_file.read_text(encoding="utf-8") if source_file else None
    request = GenerationRequest(
        topic=topic,
        audience=audience,
        user_id=user_id,
        style=style,
        source_text=source_text,
        max_iterations=max_iterations,
        llm_backend=backend,
    )
    settings = load_settings(data_dir=data_dir, llm_backend=backend, max_iterations=max_iterations)
    result = asyncio.run(GenerationService(settings).generate(request))
    console.print(f"[bold green]Generated[/bold green] {result.run_id}")
    console.print(f"Article: {result.artifacts[0].path}")
    console.print(f"Run dir: {result.run_dir}")
    console.print(f"Memory updates: {len(result.memory_updates)}")
    console.print()
    console.print(result.final_article.content)


@memory_app.command("show")
def memory_show(
    user_id: str = typer.Option("default", "--user-id", "-u"),
    data_dir: Path | None = typer.Option(None, "--data-dir"),
) -> None:
    store = MemoryStore(load_settings(data_dir=data_dir).data_dir)
    console.print(store.show(user_id))


@memory_app.command("search")
def memory_search(
    query: str = typer.Argument(...),
    user_id: str = typer.Option("default", "--user-id", "-u"),
    data_dir: Path | None = typer.Option(None, "--data-dir"),
) -> None:
    store = MemoryStore(load_settings(data_dir=data_dir).data_dir)
    results = store.search(user_id, query)
    table = Table(title=f"Memory search: {query}")
    table.add_column("Score")
    table.add_column("Title")
    table.add_column("Summary")
    table.add_column("Path")
    for item in results:
        table.add_row(f"{item.score:.2f}", item.title, item.summary[:80], item.path)
    console.print(table)


@memory_app.command("update")
def memory_update(
    title: str = typer.Option(..., "--title"),
    summary: str = typer.Option(..., "--summary"),
    section: str = typer.Option("knowledge", "--section"),
    tags: str = typer.Option("", "--tags", help="Comma-separated tags"),
    confidence: float = typer.Option(0.7, "--confidence"),
    user_id: str = typer.Option("default", "--user-id", "-u"),
    data_dir: Path | None = typer.Option(None, "--data-dir"),
) -> None:
    store = MemoryStore(load_settings(data_dir=data_dir).data_dir)
    written = store.apply_updates(
        user_id,
        [
            MemoryUpdate(
                section=section,
                title=title,
                summary=summary,
                tags=[tag.strip() for tag in tags.split(",") if tag.strip()],
                confidence=confidence,
                source_run="manual",
            )
        ],
    )
    console.print(f"Updated: {', '.join(written) if written else 'no changes'}")


@run_app.command("show")
def run_show(
    run_id: str = typer.Argument(...),
    data_dir: Path | None = typer.Option(None, "--data-dir"),
) -> None:
    settings = load_settings(data_dir=data_dir)
    path = settings.data_dir / "runs" / run_id / "state.json"
    if not path.exists():
        raise typer.BadParameter(f"Run not found: {run_id}")
    data = read_json(path)
    console.print_json(data=data)
