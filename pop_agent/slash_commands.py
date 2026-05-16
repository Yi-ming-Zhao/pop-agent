from __future__ import annotations

import argparse
import asyncio
import json
import os
import shlex
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config import load_settings
from .memory import MemoryStore, MemoryUpdate
from .models import GenerationRequest
from .orchestrator import GenerationService
from .storage import read_json
from .user_config import format_user_config


@dataclass(frozen=True)
class ParsedSlashCommand:
    command_name: str
    args: str


@dataclass(frozen=True)
class SlashCommand:
    name: str
    description: str
    argument_hint: str = ""
    aliases: tuple[str, ...] = ()


@dataclass
class CommandResult:
    action: str
    message: str = ""
    payload: dict[str, Any] | None = None


class SlashCommandError(ValueError):
    pass


class SlashArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise SlashCommandError(message)


COMMANDS: tuple[SlashCommand, ...] = (
    SlashCommand("help", "显示可用 slash commands", aliases=("?",)),
    SlashCommand(
        "generate",
        "运行科普多 Agent 生成流程",
        "--topic TOPIC [--audience AUDIENCE] [--user-id USER] [--backend mock]",
        aliases=("g",),
    ),
    SlashCommand(
        "memory",
        "查看、搜索或更新用户认知记忆",
        "show|search|update ...",
        aliases=("m",),
    ),
    SlashCommand("run", "查看运行记录", "show RUN_ID"),
    SlashCommand("settings", "显示当前用户级配置", aliases=("config",)),
    SlashCommand("install", "打开安装/配置向导"),
    SlashCommand("exit", "退出 TUI", aliases=("quit", "q")),
)


def parse_slash_command(raw: str) -> ParsedSlashCommand | None:
    text = raw.strip()
    if not text.startswith("/"):
        return None
    body = text[1:].strip()
    if not body:
        return ParsedSlashCommand("help", "")
    command, _, args = body.partition(" ")
    return ParsedSlashCommand(command_name=command.strip().lower(), args=args.strip())


async def dispatch_slash_command(
    raw: str,
    *,
    progress: Any | None = None,
) -> CommandResult:
    parsed = parse_slash_command(raw)
    if parsed is None:
        raise SlashCommandError("命令必须以 / 开头。")
    command = resolve_command(parsed.command_name)
    if command == "help":
        return CommandResult("message", format_help())
    if command == "exit":
        return CommandResult("exit", "退出。")
    if command == "settings":
        return CommandResult("message", format_user_config())
    if command == "install":
        return CommandResult("install", "打开安装向导。")
    if command == "generate":
        return await handle_generate(parsed.args, progress=progress)
    if command == "memory":
        return handle_memory(parsed.args)
    if command == "run":
        return handle_run(parsed.args)
    raise SlashCommandError(f"未知命令：/{parsed.command_name}")


def resolve_command(name: str) -> str:
    for command in COMMANDS:
        if name == command.name or name in command.aliases:
            return command.name
    raise SlashCommandError(f"未知命令：/{name}")


def format_help() -> str:
    lines = ["可用 slash commands:"]
    for command in COMMANDS:
        aliases = f" aliases: {', '.join('/' + item for item in command.aliases)}" if command.aliases else ""
        hint = f" {command.argument_hint}" if command.argument_hint else ""
        lines.append(f"/{command.name}{hint} - {command.description}{aliases}")
    return "\n".join(lines)


async def handle_generate(args_text: str, *, progress: Any | None = None) -> CommandResult:
    parser = SlashArgumentParser(prog="/generate", add_help=False)
    parser.add_argument("--topic", "-t", required=True)
    parser.add_argument("--audience", "-a", default="general beginner")
    parser.add_argument("--user-id", "-u", default="default")
    parser.add_argument("--style", default="clear, engaging popular science")
    parser.add_argument("--source-file", type=Path)
    parser.add_argument("--max-iterations", type=int)
    parser.add_argument("--backend")
    parser.add_argument("--data-dir", type=Path)
    args = parser.parse_args(split_args(args_text))

    source_text = args.source_file.read_text(encoding="utf-8") if args.source_file else None
    request = GenerationRequest(
        topic=args.topic,
        audience=args.audience,
        user_id=args.user_id,
        style=args.style,
        source_text=source_text,
        max_iterations=args.max_iterations,
        llm_backend=args.backend,
    )
    settings = load_settings(
        data_dir=args.data_dir,
        llm_backend=args.backend,
        max_iterations=args.max_iterations,
    )
    result = await GenerationService(settings).generate(request, progress=progress)
    message = (
        f"Generated {result.run_id}\n"
        f"Article: {result.artifacts[0].path}\n"
        f"Run dir: {result.run_dir}\n"
        f"Memory updates: {len(result.memory_updates)}\n\n"
        f"{result.final_article.content}"
    )
    return CommandResult("message", message, {"run_id": result.run_id})


def handle_memory(args_text: str) -> CommandResult:
    tokens = split_args(args_text)
    if not tokens:
        raise SlashCommandError("用法：/memory show|search|update ...")
    subcommand = tokens[0]
    parser = SlashArgumentParser(prog=f"/memory {subcommand}", add_help=False)
    if subcommand == "show":
        parser.add_argument("--user-id", "-u", default="default")
        parser.add_argument("--data-dir", type=Path)
        args = parser.parse_args(tokens[1:])
        store = MemoryStore(load_settings(data_dir=args.data_dir).data_dir)
        return CommandResult("message", store.show(args.user_id))
    if subcommand == "search":
        parser.add_argument("query")
        parser.add_argument("--user-id", "-u", default="default")
        parser.add_argument("--data-dir", type=Path)
        args = parser.parse_args(tokens[1:])
        store = MemoryStore(load_settings(data_dir=args.data_dir).data_dir)
        rows = store.search(args.user_id, args.query)
        if not rows:
            return CommandResult("message", "没有找到匹配记忆。")
        message = "\n".join(
            f"- {item.score:.2f} {item.title}: {item.summary} ({item.path})"
            for item in rows
        )
        return CommandResult("message", message)
    if subcommand == "update":
        parser.add_argument("--title", required=True)
        parser.add_argument("--summary", required=True)
        parser.add_argument("--section", default="knowledge")
        parser.add_argument("--tags", default="")
        parser.add_argument("--confidence", type=float, default=0.7)
        parser.add_argument("--user-id", "-u", default="default")
        parser.add_argument("--data-dir", type=Path)
        args = parser.parse_args(tokens[1:])
        store = MemoryStore(load_settings(data_dir=args.data_dir).data_dir)
        written = store.apply_updates(
            args.user_id,
            [
                MemoryUpdate(
                    section=args.section,
                    title=args.title,
                    summary=args.summary,
                    tags=[tag.strip() for tag in args.tags.split(",") if tag.strip()],
                    confidence=args.confidence,
                    source_run="slash-command",
                )
            ],
        )
        return CommandResult("message", f"Updated: {', '.join(written) if written else 'no changes'}")
    raise SlashCommandError("用法：/memory show|search|update ...")


def handle_run(args_text: str) -> CommandResult:
    tokens = split_args(args_text)
    if not tokens:
        raise SlashCommandError("用法：/run show RUN_ID")
    subcommand = tokens[0]
    parser = SlashArgumentParser(prog=f"/run {subcommand}", add_help=False)
    if subcommand != "show":
        raise SlashCommandError("用法：/run show RUN_ID")
    parser.add_argument("run_id")
    parser.add_argument("--data-dir", type=Path)
    args = parser.parse_args(tokens[1:])
    settings = load_settings(data_dir=args.data_dir)
    path = settings.data_dir / "runs" / args.run_id / "state.json"
    if not path.exists():
        raise SlashCommandError(f"Run not found: {args.run_id}")
    return CommandResult(
        "message",
        json.dumps(read_json(path), ensure_ascii=False, indent=2),
    )


def split_args(args_text: str) -> list[str]:
    try:
        tokens = shlex.split(args_text, posix=os.name != "nt")
    except ValueError as exc:
        raise SlashCommandError(str(exc)) from exc
    if os.name == "nt":
        return [strip_matching_quotes(token) for token in tokens]
    return tokens


def strip_matching_quotes(token: str) -> str:
    if len(token) >= 2 and token[0] == token[-1] and token[0] in {"'", '"'}:
        return token[1:-1]
    return token


def dispatch_slash_command_sync(raw: str) -> CommandResult:
    return asyncio.run(dispatch_slash_command(raw))
