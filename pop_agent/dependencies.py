from __future__ import annotations

import importlib.util
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Dependency:
    label: str
    import_name: str
    package_spec: str
    required: bool = True


@dataclass(frozen=True)
class DependencyStatus:
    dependency: Dependency
    installed: bool


RUNTIME_DEPENDENCIES: tuple[Dependency, ...] = (
    Dependency("FastAPI", "fastapi", "fastapi>=0.115"),
    Dependency("HTTPX", "httpx", "httpx>=0.27"),
    Dependency("Pydantic", "pydantic", "pydantic>=2.7"),
    Dependency("python-dotenv", "dotenv", "python-dotenv>=1.0"),
    Dependency("Rich", "rich", "rich>=13.7"),
    Dependency("Textual", "textual", "textual>=0.89"),
    Dependency("Typer", "typer", "typer>=0.12"),
    Dependency("Uvicorn", "uvicorn", "uvicorn>=0.30"),
)

DEV_DEPENDENCIES: tuple[Dependency, ...] = (
    Dependency("pytest", "pytest", "pytest>=8.2", required=False),
    Dependency("pytest-asyncio", "pytest_asyncio", "pytest-asyncio>=0.23", required=False),
)


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def check_dependencies(*, include_dev: bool = False) -> list[DependencyStatus]:
    dependencies = list(RUNTIME_DEPENDENCIES)
    if include_dev:
        dependencies.extend(DEV_DEPENDENCIES)
    return [
        DependencyStatus(
            dependency=dependency,
            installed=importlib.util.find_spec(dependency.import_name) is not None,
        )
        for dependency in dependencies
    ]


def missing_dependencies(*, include_dev: bool = False) -> list[Dependency]:
    return [
        status.dependency
        for status in check_dependencies(include_dev=include_dev)
        if not status.installed
    ]


def format_dependency_report(*, include_dev: bool = False) -> str:
    statuses = check_dependencies(include_dev=include_dev)
    lines = ["依赖检查:"]
    for status in statuses:
        mark = "OK" if status.installed else "缺失"
        kind = "必需" if status.dependency.required else "开发"
        lines.append(f"- {mark} [{kind}] {status.dependency.package_spec}")
    missing = [status for status in statuses if not status.installed]
    if not missing:
        lines.append("所有依赖已安装。")
    else:
        specs = " ".join(status.dependency.package_spec for status in missing)
        lines.append(f"可安装缺失依赖: {sys.executable} -m pip install {specs}")
    return "\n".join(lines)


def install_project_dependencies(*, include_dev: bool = True) -> subprocess.CompletedProcess[str]:
    root = project_root()
    if not (root / "pyproject.toml").exists():
        raise FileNotFoundError(f"找不到 pyproject.toml: {root}")
    target = f"{root}[dev]" if include_dev else str(root)
    return subprocess.run(
        [sys.executable, "-m", "pip", "install", "-e", target],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
