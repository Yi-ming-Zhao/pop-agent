from __future__ import annotations

import asyncio
import json

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    RichLog,
    Select,
    Static,
    TabPane,
    TabbedContent,
)

from ..config import load_settings
from ..dependencies import format_dependency_report, install_project_dependencies
from ..install import save_user_config_without_test, test_user_config_connection
from ..memory import MemoryStore, MemoryUpdate
from ..models import GenerationRequest
from ..orchestrator import GenerationService
from ..slash_commands import SlashCommandError, dispatch_slash_command, format_help
from ..storage import read_json
from ..user_config import (
    PROVIDER_PRESETS,
    UserConfig,
    format_user_config,
    has_runtime_configuration,
    load_user_config,
    provider_config,
    save_user_config,
)


class InstallScreen(ModalScreen[bool]):
    CSS = """
    InstallScreen {
        align: center middle;
    }

    #install-dialog {
        width: 78;
        max-width: 95%;
        height: auto;
        padding: 1 2;
        border: thick $accent;
        background: $surface;
    }

    #install-dialog Input, #install-dialog Select {
        margin-bottom: 1;
    }

    #install-buttons {
        height: auto;
        margin-top: 1;
    }

    #install-buttons Button {
        margin-right: 1;
    }

    #install-status {
        min-height: 3;
        margin-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        config = load_user_config()
        provider = config.provider if config.provider in PROVIDER_PRESETS else "deepseek"
        preset = PROVIDER_PRESETS[provider]
        yield Vertical(
            Static("pop-agent 安装向导", classes="dialog-title"),
            Static(format_dependency_report(include_dev=False), id="dependency-status"),
            Horizontal(
                Button("检查依赖", id="install-check-deps"),
                Button("安装/修复依赖", id="install-install-deps"),
                id="dependency-buttons",
            ),
            Label("选择模型供应商"),
            Select(
                [(preset.label, key) for key, preset in PROVIDER_PRESETS.items()],
                value=provider,
                id="install-provider",
            ),
            Label("API key（Mock 模式可留空）"),
            Input(value=config.api_key or "", password=True, id="install-api-key"),
            Label("Base URL"),
            Input(value=config.base_url or preset.base_url, id="install-base-url"),
            Label("模型名"),
            Input(value=config.model or preset.model, id="install-model"),
            Label("数据目录"),
            Input(value=config.data_dir or "data", id="install-data-dir"),
            Horizontal(
                Button("测试并保存", id="install-test-save", variant="primary"),
                Button("保存当前配置", id="install-save-current"),
                Button("保存 Mock 演示配置", id="install-save-mock"),
                Button("关闭", id="install-close"),
                id="install-buttons",
            ),
            Static("", id="install-status"),
            id="install-dialog",
        )

    @on(Select.Changed, "#install-provider")
    def provider_changed(self, event: Select.Changed) -> None:
        provider = str(event.value)
        preset = PROVIDER_PRESETS.get(provider, PROVIDER_PRESETS["mock"])
        self.query_one("#install-base-url", Input).value = preset.base_url
        self.query_one("#install-model", Input).value = preset.model
        if not preset.requires_api_key:
            self.query_one("#install-api-key", Input).value = ""

    @on(Button.Pressed, "#install-check-deps")
    def check_deps(self) -> None:
        self.query_one("#dependency-status", Static).update(
            format_dependency_report(include_dev=False)
        )

    @on(Button.Pressed, "#install-install-deps")
    async def install_deps(self) -> None:
        status = self.query_one("#install-status", Static)
        deps = self.query_one("#dependency-status", Static)
        status.update("正在安装/修复依赖...")
        result = await asyncio.to_thread(install_project_dependencies, include_dev=True)
        output = (result.stdout or result.stderr or "").strip()
        if result.returncode == 0:
            deps.update(format_dependency_report(include_dev=False))
            status.update("依赖安装完成。")
        else:
            status.update(f"依赖安装失败，退出码 {result.returncode}\n{output[-1200:]}")

    @on(Button.Pressed, "#install-save-mock")
    def save_mock(self) -> None:
        data_dir = self.query_one("#install-data-dir", Input).value.strip() or "data"
        path = save_user_config(provider_config("mock", data_dir=data_dir))
        self.query_one("#install-status", Static).update(f"已保存 Mock 配置：{path}")
        self.dismiss(True)

    @on(Button.Pressed, "#install-test-save")
    async def test_and_save(self) -> None:
        status = self.query_one("#install-status", Static)
        status.update("正在测试连接...")
        config = self.form_config()
        ok, message = await test_user_config_connection(config)
        status.update(message)
        if ok:
            self.dismiss(True)

    @on(Button.Pressed, "#install-save-current")
    def save_current(self) -> None:
        status = self.query_one("#install-status", Static)
        ok, message = save_user_config_without_test(self.form_config())
        status.update(message)
        if ok:
            self.dismiss(True)

    @on(Button.Pressed, "#install-close")
    def close(self) -> None:
        self.dismiss(False)

    def form_config(self) -> UserConfig:
        provider = str(self.query_one("#install-provider", Select).value or "mock")
        return provider_config(
            provider,
            api_key=self.query_one("#install-api-key", Input).value.strip() or None,
            base_url=self.query_one("#install-base-url", Input).value.strip() or None,
            model=self.query_one("#install-model", Input).value.strip() or None,
            data_dir=self.query_one("#install-data-dir", Input).value.strip() or None,
        )


class PopAgentTUI(App[None]):
    TITLE = "pop-agent"
    SUB_TITLE = "multi-agent popular science studio"
    BINDINGS = [
        ("ctrl+c", "quit", "退出"),
        ("f1", "help", "帮助"),
        ("f2", "install", "安装"),
    ]

    CSS = """
    Screen {
        background: $background;
    }

    #main {
        height: 1fr;
    }

    #side {
        width: 28;
        padding: 1;
        border-right: solid $primary;
        background: $panel;
    }

    #side-title {
        text-style: bold;
        margin-bottom: 1;
    }

    #side Button {
        width: 100%;
        margin-bottom: 1;
    }

    #workspace {
        width: 1fr;
        padding: 1 2;
    }

    #status-panel {
        width: 36;
        padding: 1;
        border-left: solid $primary;
        background: $panel;
    }

    #command-row {
        height: 3;
        padding: 0 1;
        border-top: solid $primary;
        background: $surface;
    }

    #command-input {
        width: 1fr;
    }

    .form-row {
        height: auto;
        margin-bottom: 1;
    }

    .wide-input {
        width: 1fr;
    }

    RichLog {
        border: round $primary;
        padding: 0 1;
        height: 1fr;
    }

    TabbedContent {
        height: 1fr;
    }

    .hint {
        color: $text-muted;
        margin-bottom: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="main"):
            with Vertical(id="side"):
                yield Static("科普多 Agent", id="side-title")
                yield Button("生成文章", id="nav-generate", variant="primary")
                yield Button("用户记忆", id="nav-memory")
                yield Button("运行记录", id="nav-runs")
                yield Button("设置/安装", id="nav-settings")
                yield Button("帮助", id="nav-help")
                yield Static("F2 可重新打开安装向导\n底部输入 /help 查看命令", classes="hint")
            with Vertical(id="workspace"):
                with TabbedContent(initial="generate", id="tabs"):
                    with TabPane("生成", id="generate"):
                        yield Static("填写主题后点击生成；系统会让教师 Agent 和学生 Agent 迭代改稿。", classes="hint")
                        yield Input(placeholder="主题，例如：黑洞为什么不是洞", id="topic-input")
                        yield Input(value="初中生", placeholder="目标读者", id="audience-input")
                        yield Input(value="default", placeholder="用户 ID", id="user-id-input")
                        yield Input(value="clear, engaging popular science", placeholder="写作风格", id="style-input")
                        yield Input(value="", placeholder="最大迭代轮数，留空使用配置", id="iterations-input")
                        yield Button("开始生成", id="generate-button", variant="success")
                        yield RichLog(id="generate-log", wrap=True, highlight=True, markup=True)
                    with TabPane("记忆", id="memory"):
                        yield Static("查看或维护用户认知画像、知识掌握、误解和表达偏好。", classes="hint")
                        yield Input(value="default", placeholder="用户 ID", id="memory-user-id")
                        yield Input(placeholder="搜索词，例如：黑洞 事件视界", id="memory-query")
                        with Horizontal(classes="form-row"):
                            yield Button("查看记忆", id="memory-show")
                            yield Button("搜索记忆", id="memory-search")
                        yield Input(placeholder="新记忆标题", id="memory-title")
                        yield Input(placeholder="新记忆摘要", id="memory-summary")
                        yield Input(value="knowledge", placeholder="section: profile/knowledge/preferences/misconceptions", id="memory-section")
                        yield Input(placeholder="tags，用逗号分隔", id="memory-tags")
                        yield Button("添加记忆", id="memory-add")
                        yield RichLog(id="memory-log", wrap=True, highlight=True, markup=True)
                    with TabPane("运行", id="runs"):
                        yield Static("输入 run_id 查看历史生成状态。", classes="hint")
                        yield Input(placeholder="run_...", id="run-id-input")
                        yield Button("查看运行记录", id="run-show")
                        yield RichLog(id="run-log", wrap=True, highlight=True, markup=True)
                    with TabPane("设置", id="settings"):
                        yield Static("用户配置保存在本机配置目录，API key 展示时会脱敏。", classes="hint")
                        yield Button("打开安装向导", id="open-install", variant="primary")
                        yield RichLog(id="settings-log", wrap=True, highlight=True, markup=True)
                    with TabPane("帮助", id="help"):
                        yield RichLog(id="help-log", wrap=True, highlight=True, markup=True)
            with Vertical(id="status-panel"):
                yield Static("状态", id="status-title")
                yield Static("", id="runtime-status")
        with Horizontal(id="command-row"):
            yield Input(placeholder="/help 或 /generate --topic \"黑洞\" --backend mock", id="command-input")
        yield Footer()

    async def on_mount(self) -> None:
        self.refresh_status()
        self.query_one("#help-log", RichLog).write(format_help())
        self.query_one("#settings-log", RichLog).write(format_user_config())
        if not has_runtime_configuration():
            self.open_install()

    def refresh_status(self) -> None:
        settings = load_settings()
        status = (
            f"backend: {settings.llm_backend}\n"
            f"model: {settings.model}\n"
            f"data: {settings.data_dir}\n"
            f"iterations: {settings.max_iterations}\n"
            f"threshold: {settings.clarity_threshold}"
        )
        self.query_one("#runtime-status", Static).update(status)

    def open_install(self) -> None:
        self.push_screen(InstallScreen(), callback=self.install_closed)

    def install_closed(self, saved: bool | None) -> None:
        if saved:
            self.refresh_status()
            log = self.query_one("#settings-log", RichLog)
            log.clear()
            log.write(format_user_config())

    def action_install(self) -> None:
        self.open_install()

    def action_help(self) -> None:
        self.query_one("#tabs", TabbedContent).active = "help"

    @on(Button.Pressed, "#nav-generate")
    def nav_generate(self) -> None:
        self.query_one("#tabs", TabbedContent).active = "generate"

    @on(Button.Pressed, "#nav-memory")
    def nav_memory(self) -> None:
        self.query_one("#tabs", TabbedContent).active = "memory"

    @on(Button.Pressed, "#nav-runs")
    def nav_runs(self) -> None:
        self.query_one("#tabs", TabbedContent).active = "runs"

    @on(Button.Pressed, "#nav-settings")
    def nav_settings(self) -> None:
        self.query_one("#tabs", TabbedContent).active = "settings"

    @on(Button.Pressed, "#nav-help")
    def nav_help(self) -> None:
        self.query_one("#tabs", TabbedContent).active = "help"

    @on(Button.Pressed, "#open-install")
    def open_install_button(self) -> None:
        self.open_install()

    @on(Button.Pressed, "#generate-button")
    async def generate_from_form(self) -> None:
        topic = self.query_one("#topic-input", Input).value.strip()
        if not topic:
            self.notify("请先填写主题", severity="warning")
            return
        iterations_text = self.query_one("#iterations-input", Input).value.strip()
        max_iterations = int(iterations_text) if iterations_text else None
        request = GenerationRequest(
            topic=topic,
            audience=self.query_one("#audience-input", Input).value.strip() or "general beginner",
            user_id=self.query_one("#user-id-input", Input).value.strip() or "default",
            style=self.query_one("#style-input", Input).value.strip() or "clear, engaging popular science",
            max_iterations=max_iterations,
        )
        log = self.query_one("#generate-log", RichLog)
        log.clear()
        log.write("[bold]开始生成...[/bold]")

        async def progress(stage: str, message: str) -> None:
            log.write(f"[bold cyan]{stage}[/bold cyan] {message}")

        try:
            settings = load_settings(max_iterations=max_iterations)
            result = await GenerationService(settings).generate(request, progress=progress)
        except Exception as exc:
            log.write(f"[red]生成失败：{exc}[/red]")
            return
        log.write(f"[bold green]Generated {result.run_id}[/bold green]")
        log.write(f"Article: {result.artifacts[0].path}")
        log.write("")
        log.write(result.final_article.content)
        self.refresh_status()

    @on(Button.Pressed, "#memory-show")
    def show_memory(self) -> None:
        user_id = self.query_one("#memory-user-id", Input).value.strip() or "default"
        log = self.query_one("#memory-log", RichLog)
        log.clear()
        log.write(MemoryStore(load_settings().data_dir).show(user_id))

    @on(Button.Pressed, "#memory-search")
    def search_memory(self) -> None:
        user_id = self.query_one("#memory-user-id", Input).value.strip() or "default"
        query = self.query_one("#memory-query", Input).value.strip()
        log = self.query_one("#memory-log", RichLog)
        log.clear()
        results = MemoryStore(load_settings().data_dir).search(user_id, query)
        if not results:
            log.write("没有找到匹配记忆。")
            return
        for item in results:
            log.write(f"{item.score:.2f} {item.title}: {item.summary} ({item.path})")

    @on(Button.Pressed, "#memory-add")
    def add_memory(self) -> None:
        title = self.query_one("#memory-title", Input).value.strip()
        summary = self.query_one("#memory-summary", Input).value.strip()
        if not title or not summary:
            self.notify("标题和摘要不能为空", severity="warning")
            return
        user_id = self.query_one("#memory-user-id", Input).value.strip() or "default"
        tags = self.query_one("#memory-tags", Input).value
        section = self.query_one("#memory-section", Input).value.strip() or "knowledge"
        written = MemoryStore(load_settings().data_dir).apply_updates(
            user_id,
            [
                MemoryUpdate(
                    section=section,
                    title=title,
                    summary=summary,
                    tags=[tag.strip() for tag in tags.split(",") if tag.strip()],
                    confidence=0.8,
                    source_run="tui-manual",
                )
            ],
        )
        self.query_one("#memory-log", RichLog).write(
            f"Updated: {', '.join(written) if written else 'no changes'}"
        )

    @on(Button.Pressed, "#run-show")
    def show_run(self) -> None:
        run_id = self.query_one("#run-id-input", Input).value.strip()
        log = self.query_one("#run-log", RichLog)
        log.clear()
        if not run_id:
            self.notify("请填写 run_id", severity="warning")
            return
        path = load_settings().data_dir / "runs" / run_id / "state.json"
        if not path.exists():
            log.write(f"Run not found: {run_id}")
            return
        log.write(json.dumps(read_json(path), ensure_ascii=False, indent=2))

    @on(Input.Submitted, "#command-input")
    async def command_submitted(self, event: Input.Submitted) -> None:
        raw = event.value.strip()
        event.input.value = ""
        if not raw:
            return
        log = self.query_one("#generate-log", RichLog)
        log.write(f"[bold]> {raw}[/bold]")

        async def progress(stage: str, message: str) -> None:
            log.write(f"[bold cyan]{stage}[/bold cyan] {message}")

        try:
            result = await dispatch_slash_command(raw, progress=progress)
        except SlashCommandError as exc:
            log.write(f"[red]{exc}[/red]")
            return
        except Exception as exc:
            log.write(f"[red]命令执行失败：{exc}[/red]")
            return
        if result.action == "exit":
            self.exit()
            return
        if result.action == "install":
            self.open_install()
            return
        if result.message:
            log.write(result.message)
        self.refresh_status()


def run_tui() -> None:
    PopAgentTUI().run()
