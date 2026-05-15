from __future__ import annotations

import asyncio
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .config import load_settings
from .daemon import DEFAULT_HOST, DEFAULT_PORT, install_api_daemon
from .dependencies import format_dependency_report, install_project_dependencies
from .memory import MemoryStore, MemoryUpdate
from .models import GenerationRequest
from .orchestrator import GenerationService
from .storage import read_json
from .user_config import provider_config, save_user_config

app = typer.Typer(help="Multi-agent popular science generation")
memory_app = typer.Typer(help="User cognitive memory commands")
run_app = typer.Typer(help="Run inspection commands")
app.add_typer(memory_app, name="memory")
app.add_typer(run_app, name="run")
console = Console()


def main() -> None:
    app()


@app.command()
def tui() -> None:
    """Start the full-screen terminal UI."""
    try:
        from .tui.app import run_tui
    except ModuleNotFoundError as exc:
        if exc.name == "textual":
            console.print("[red]Textual 未安装，无法启动全屏 TUI。[/red]")
            console.print("请先运行：pop-agent install-deps")
            raise typer.Exit(1) from exc
        raise
    run_tui()


@app.command("doctor")
def doctor(
    include_dev: bool = typer.Option(False, "--dev", help="Include test/development dependencies"),
) -> None:
    """Check local runtime dependencies."""
    console.print(format_dependency_report(include_dev=include_dev))


@app.command("install-deps")
def install_deps(
    include_dev: bool = typer.Option(True, "--dev/--no-dev", help="Install development dependencies too"),
) -> None:
    """Install or repair project dependencies with pip."""
    console.print("Installing dependencies...")
    result = install_project_dependencies(include_dev=include_dev)
    if result.stdout:
        console.print(result.stdout)
    if result.stderr:
        console.print(result.stderr)
    if result.returncode != 0:
        raise typer.Exit(result.returncode)
    console.print("[bold green]Dependencies installed.[/bold green]")


@app.command("onboard")
def onboard(
    install_daemon_option: bool = typer.Option(
        False,
        "--install-daemon",
        help="Install a local API daemon after writing the initial config.",
    ),
    provider: str = typer.Option(
        "mock",
        "--provider",
        help="Provider preset: mock, deepseek, or openai.",
    ),
    api_key: str | None = typer.Option(None, "--api-key", help="API key for real providers."),
    base_url: str | None = typer.Option(None, "--base-url", help="Override provider base URL."),
    model: str | None = typer.Option(None, "--model", help="Override provider model."),
    data_dir: Path = typer.Option(Path("data"), "--data-dir", help="Data directory."),
    host: str = typer.Option(DEFAULT_HOST, "--host", help="Daemon bind host."),
    port: int = typer.Option(DEFAULT_PORT, "--port", help="Daemon bind port."),
    start_daemon: bool = typer.Option(
        True,
        "--start-daemon/--no-start-daemon",
        help="Start daemon immediately when systemd user service is available.",
    ),
) -> None:
    """Run source-install onboarding and optionally install the local API daemon."""
    normalized_provider = provider.lower()
    if normalized_provider not in {"mock", "deepseek", "openai"}:
        raise typer.BadParameter("provider must be one of: mock, deepseek, openai")
    if normalized_provider != "mock" and not api_key:
        raise typer.BadParameter("--api-key is required for real providers")

    config = provider_config(
        normalized_provider,
        api_key=api_key,
        base_url=base_url,
        model=model,
        data_dir=str(data_dir),
    )
    path = save_user_config(config)
    console.print(f"[bold green]Config saved[/bold green]: {path}")
    console.print(format_dependency_report(include_dev=False))

    if install_daemon_option:
        result = install_api_daemon(
            host=host,
            port=port,
            data_dir=data_dir,
            start=start_daemon,
        )
        console.print(result.message)
    else:
        console.print("Next: run [bold]pop-agent tui[/bold] or [bold]pop-agent generate --topic ...[/bold]")


@app.command("daemon")
def daemon(
    host: str = typer.Option(DEFAULT_HOST, "--host", help="Bind host."),
    port: int = typer.Option(DEFAULT_PORT, "--port", help="Bind port."),
) -> None:
    """Run the local FastAPI daemon in the foreground."""
    import uvicorn

    uvicorn.run("pop_agent.api:app", host=host, port=port)


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

    def show_progress(stage: str, message: str) -> None:
        console.print(f"[dim]{stage}[/dim] {message}")

    result = asyncio.run(GenerationService(settings).generate(request, progress=show_progress))
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


if __name__ == "__main__":
    main()
