#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent


@dataclass(frozen=True)
class BootstrapDependency:
    label: str
    import_name: str
    package_spec: str


RUNTIME_DEPENDENCIES: tuple[BootstrapDependency, ...] = (
    BootstrapDependency("FastAPI", "fastapi", "fastapi>=0.115"),
    BootstrapDependency("HTTPX", "httpx", "httpx>=0.27"),
    BootstrapDependency("Pydantic", "pydantic", "pydantic>=2.7"),
    BootstrapDependency("python-dotenv", "dotenv", "python-dotenv>=1.0"),
    BootstrapDependency("Rich", "rich", "rich>=13.7"),
    BootstrapDependency("Textual", "textual", "textual>=0.89"),
    BootstrapDependency("Typer", "typer", "typer>=0.12"),
    BootstrapDependency("Uvicorn", "uvicorn", "uvicorn>=0.30"),
)


def main(argv: list[str] | None = None) -> int:
    args = list(argv or sys.argv[1:])
    command = args[0] if args else "help"
    rest = args[1:]
    if command in {"-h", "--help", "help"}:
        print_help()
        return 0
    if command == "doctor":
        return doctor()
    if command == "install-deps":
        include_dev = "--no-dev" not in rest
        return install_deps(include_dev=include_dev)
    if command == "install":
        include_dev = "--no-dev" not in rest
        return install_deps(include_dev=include_dev)
    if command == "build":
        return build()
    if command in {"ui-build", "ui:build"}:
        return ui_build()
    if command == "link":
        include_dev = "--no-dev" not in rest
        return link(include_dev=include_dev)
    if command == "tui":
        code = install_deps(include_dev=True, only_if_missing=True)
        if code != 0:
            return code
        return run_pop_agent(["tui", *rest])
    if command == "onboard":
        code = install_deps(include_dev=True, only_if_missing=True)
        if code != 0:
            return code
        return run_pop_agent(["onboard", *rest])
    print(f"Unknown command: {command}")
    print_help()
    return 2


def print_help() -> None:
    print(
        "\n".join(
            [
                "Usage: python3 bootstrap.py <command>",
                "",
                "Commands:",
                "  doctor        Check Python, command availability, and runtime dependencies.",
                "  install       Alias for install-deps.",
                "  install-deps  Install project dependencies with pip install -e '.[dev]'.",
                "  build         Compile Python sources to catch syntax/import-time issues.",
                "  ui-build      Validate Textual TUI imports and build Web frontend assets.",
                "  link          Install this checkout as an editable global command.",
                "  onboard       Install missing dependencies if needed, then run pop-agent onboard.",
                "  tui           Install missing dependencies if needed, then start pop-agent tui.",
                "",
                "Source install example:",
                "  python3 bootstrap.py install && python3 bootstrap.py build && python3 bootstrap.py ui-build",
                "  python3 bootstrap.py link",
                "  pop-agent onboard --install-daemon",
            ]
        )
    )


def doctor() -> int:
    print(f"Python: {sys.version.split()[0]} ({sys.executable})")
    if sys.version_info < (3, 10):
        print("ERROR: Python >= 3.10 is required.")
        return 1
    if not (ROOT / "pyproject.toml").exists():
        print(f"ERROR: pyproject.toml not found in {ROOT}")
        return 1

    command_path = shutil.which("pop-agent")
    if command_path:
        print(f"Command: pop-agent -> {command_path}")
    else:
        print("Command: pop-agent is not installed or not on PATH yet.")
        print("Next step: python3 bootstrap.py install-deps")

    missing = missing_dependencies()
    for dependency in RUNTIME_DEPENDENCIES:
        mark = "OK" if dependency.import_name not in missing else "missing"
        print(f"- {mark}: {dependency.package_spec}")
    return 1 if missing else 0


def install_deps(*, include_dev: bool, only_if_missing: bool = False) -> int:
    if only_if_missing and not missing_dependencies():
        return 0
    target = ".[dev]" if include_dev else "."
    command = [sys.executable, "-m", "pip", "install", "-e", target]
    print("Running:", " ".join(command))
    return subprocess.run(command, cwd=ROOT).returncode


def build() -> int:
    command = [sys.executable, "-m", "compileall", "bootstrap.py", "pop_agent"]
    print("Running:", " ".join(command))
    return subprocess.run(command, cwd=ROOT).returncode


def ui_build() -> int:
    code = (
        "from pop_agent.tui.app import PopAgentTUI; "
        "app = PopAgentTUI(); "
        "print(app.TITLE)"
    )
    command = [sys.executable, "-c", code]
    print("Running:", " ".join(command))
    result = subprocess.run(command, cwd=ROOT)
    if result.returncode != 0:
        return result.returncode
    return build_web_assets()


def build_web_assets() -> int:
    web_root = ROOT / "web"
    src_dir = web_root / "src"
    dist_dir = web_root / "dist"
    required = ("index.html", "styles.css", "app.js")

    missing = [name for name in required if not (src_dir / name).exists()]
    if missing:
        print("ERROR: missing Web frontend assets:", ", ".join(missing))
        return 1

    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(parents=True, exist_ok=True)
    for name in required:
        shutil.copy2(src_dir / name, dist_dir / name)

    print(f"Built Web frontend: {dist_dir / 'index.html'}")
    return 0


def link(*, include_dev: bool) -> int:
    target = ".[dev]" if include_dev else "."
    command = [sys.executable, "-m", "pip", "install", "-e", target]
    print("Running:", " ".join(command))
    result = subprocess.run(command, cwd=ROOT)
    if result.returncode != 0:
        return result.returncode
    command_path = shutil.which("pop-agent")
    if command_path:
        print(f"Linked command: {command_path}")
        return 0
    local_bin = Path.home() / ".local" / "bin"
    print("WARNING: pop-agent was installed, but it is not on PATH.")
    print(f"Add this to PATH: export PATH={local_bin}:$PATH")
    return 0


def run_pop_agent(args: list[str]) -> int:
    command_path = shutil.which("pop-agent")
    if command_path:
        return subprocess.run([command_path, *args], cwd=ROOT).returncode
    return subprocess.run([sys.executable, "-m", "pop_agent", *args], cwd=ROOT).returncode


def missing_dependencies() -> set[str]:
    return {
        dependency.import_name
        for dependency in RUNTIME_DEPENDENCIES
        if importlib.util.find_spec(dependency.import_name) is None
    }


if __name__ == "__main__":
    raise SystemExit(main())
