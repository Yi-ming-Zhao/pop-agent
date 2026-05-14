from __future__ import annotations

import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from .user_config import config_dir


SERVICE_NAME = "pop-agent-api.service"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765


@dataclass(frozen=True)
class DaemonInstallResult:
    mode: str
    path: Path
    started: bool
    message: str


def install_api_daemon(
    *,
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    data_dir: str | Path | None = None,
    start: bool = True,
) -> DaemonInstallResult:
    project_root = Path(__file__).resolve().parents[1]
    resolved_data_dir = Path(data_dir or "data").expanduser()
    systemd_dir = Path.home() / ".config" / "systemd" / "user"
    systemctl = shutil.which("systemctl")
    if systemctl:
        service_path = systemd_dir / SERVICE_NAME
        service_path.parent.mkdir(parents=True, exist_ok=True)
        service_path.write_text(
            render_systemd_service(
                project_root=project_root,
                data_dir=resolved_data_dir,
                host=host,
                port=port,
            ),
            encoding="utf-8",
        )
        os.chmod(service_path, 0o600)
        started = False
        message = f"已安装 systemd user service：{service_path}"
        reload_result = subprocess.run(
            [systemctl, "--user", "daemon-reload"],
            capture_output=True,
            text=True,
            check=False,
        )
        if reload_result.returncode == 0 and start:
            enable_result = subprocess.run(
                [systemctl, "--user", "enable", "--now", SERVICE_NAME],
                capture_output=True,
                text=True,
                check=False,
            )
            started = enable_result.returncode == 0
            if started:
                message += f"\n已启动：{SERVICE_NAME}"
            else:
                message += (
                    "\nservice 已写入，但自动启动失败。"
                    f"\n可手动运行：systemctl --user start {SERVICE_NAME}"
                    f"\n错误：{(enable_result.stderr or enable_result.stdout).strip()}"
                )
        elif reload_result.returncode != 0:
            message += (
                "\nsystemd daemon-reload 失败，但 service 文件已写入。"
                f"\n错误：{(reload_result.stderr or reload_result.stdout).strip()}"
            )
        return DaemonInstallResult("systemd", service_path, started, message)

    script_path = config_dir() / "daemon" / "start-api.sh"
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(
        render_daemon_script(
            project_root=project_root,
            data_dir=resolved_data_dir,
            host=host,
            port=port,
        ),
        encoding="utf-8",
    )
    os.chmod(script_path, 0o700)
    return DaemonInstallResult(
        "script",
        script_path,
        False,
        f"未检测到 systemctl，已生成启动脚本：{script_path}\n运行该脚本即可启动本机 API daemon。",
    )


def render_systemd_service(
    *,
    project_root: Path,
    data_dir: Path,
    host: str,
    port: int,
) -> str:
    return (
        "[Unit]\n"
        "Description=pop-agent local API daemon\n"
        "After=network.target\n\n"
        "[Service]\n"
        "Type=simple\n"
        f"WorkingDirectory={project_root}\n"
        f"Environment=POP_AGENT_DATA_DIR={data_dir}\n"
        f"ExecStart={sys.executable} -m uvicorn pop_agent.api:app --host {host} --port {port}\n"
        "Restart=on-failure\n"
        "RestartSec=3\n\n"
        "[Install]\n"
        "WantedBy=default.target\n"
    )


def render_daemon_script(
    *,
    project_root: Path,
    data_dir: Path,
    host: str,
    port: int,
) -> str:
    return (
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        f"cd {shell_quote(project_root)}\n"
        f"export POP_AGENT_DATA_DIR={shell_quote(data_dir)}\n"
        f"exec {shell_quote(Path(sys.executable))} -m uvicorn pop_agent.api:app --host {host} --port {port}\n"
    )


def shell_quote(value: Path | str) -> str:
    raw = str(value)
    return "'" + raw.replace("'", "'\"'\"'") + "'"
