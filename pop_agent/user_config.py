from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


CONFIG_FILENAME = "config.json"


@dataclass(frozen=True)
class ProviderPreset:
    provider: str
    label: str
    llm_backend: str
    base_url: str
    model: str
    requires_api_key: bool
    deepseek_thinking: str = "disabled"


@dataclass
class UserConfig:
    provider: str = "mock"
    llm_backend: str = "mock"
    api_key: str | None = None
    base_url: str | None = None
    model: str | None = None
    max_iterations: int | None = None
    request_timeout: float | None = None
    max_retries: int | None = None
    deepseek_thinking: str | None = None
    data_dir: str | None = None

    def redacted(self) -> dict[str, Any]:
        data = asdict(self)
        data["api_key"] = redact_secret(self.api_key)
        return data


PROVIDER_PRESETS: dict[str, ProviderPreset] = {
    "deepseek": ProviderPreset(
        provider="deepseek",
        label="DeepSeek",
        llm_backend="openai-compatible",
        base_url="https://api.deepseek.com",
        model="deepseek-v4-pro",
        requires_api_key=True,
        deepseek_thinking="disabled",
    ),
    "openai": ProviderPreset(
        provider="openai",
        label="OpenAI-compatible",
        llm_backend="openai-compatible",
        base_url="https://api.openai.com/v1",
        model="gpt-4o-mini",
        requires_api_key=True,
    ),
    "mock": ProviderPreset(
        provider="mock",
        label="Mock local demo",
        llm_backend="mock",
        base_url="",
        model="mock",
        requires_api_key=False,
    ),
}


def config_dir() -> Path:
    explicit = os.getenv("POP_AGENT_CONFIG_DIR")
    if explicit:
        return Path(explicit).expanduser()
    xdg_home = os.getenv("XDG_CONFIG_HOME")
    if xdg_home:
        return Path(xdg_home).expanduser() / "pop-agent"
    return Path.home() / ".config" / "pop-agent"


def user_config_path() -> Path:
    return config_dir() / CONFIG_FILENAME


def load_user_config(path: Path | None = None) -> UserConfig:
    resolved = path or user_config_path()
    try:
        if not resolved.exists():
            return UserConfig()
        data = json.loads(resolved.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return UserConfig()
    if not isinstance(data, dict):
        return UserConfig()
    allowed = set(UserConfig.__dataclass_fields__)
    clean = {key: value for key, value in data.items() if key in allowed}
    return UserConfig(**clean)


def save_user_config(config: UserConfig, path: Path | None = None) -> Path:
    resolved = path or user_config_path()
    resolved.parent.mkdir(parents=True, exist_ok=True)
    os.chmod(resolved.parent, 0o700)
    tmp_path = resolved.with_suffix(".json.tmp")
    tmp_path.write_text(json.dumps(asdict(config), ensure_ascii=False, indent=2), encoding="utf-8")
    os.chmod(tmp_path, 0o600)
    tmp_path.replace(resolved)
    os.chmod(resolved, 0o600)
    return resolved


def provider_config(
    provider: str,
    *,
    api_key: str | None = None,
    base_url: str | None = None,
    model: str | None = None,
    data_dir: str | None = None,
    max_iterations: int | None = None,
    request_timeout: float | None = 120,
    max_retries: int | None = 3,
) -> UserConfig:
    preset = PROVIDER_PRESETS.get(provider, PROVIDER_PRESETS["mock"])
    return UserConfig(
        provider=preset.provider,
        llm_backend=preset.llm_backend,
        api_key=api_key or None,
        base_url=(base_url or preset.base_url or None),
        model=model or preset.model,
        max_iterations=max_iterations,
        request_timeout=request_timeout,
        max_retries=max_retries,
        deepseek_thinking=preset.deepseek_thinking,
        data_dir=data_dir or None,
    )


def has_runtime_configuration() -> bool:
    if (
        os.getenv("POP_AGENT_LLM_BACKEND")
        or os.getenv("POP_AGENT_API_KEY")
        or os.getenv("OPENAI_API_KEY")
    ):
        return True
    path = user_config_path()
    if not path.exists():
        return False
    config = load_user_config(path)
    if config.llm_backend == "mock":
        return True
    return bool(config.api_key and config.base_url and config.model)


def redact_secret(value: str | None) -> str | None:
    if not value:
        return None
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}...{value[-4:]}"


def format_user_config(config: UserConfig | None = None) -> str:
    cfg = config or load_user_config()
    lines = ["User configuration:"]
    for key, value in cfg.redacted().items():
        lines.append(f"- {key}: {value if value not in (None, '') else '(unset)'}")
    lines.append(f"- path: {user_config_path()}")
    return "\n".join(lines)