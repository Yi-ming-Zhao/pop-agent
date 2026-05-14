from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from .user_config import load_user_config


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    llm_backend: str
    api_key: str | None
    base_url: str
    model: str
    max_iterations: int
    clarity_threshold: int
    request_timeout: float
    max_retries: int
    deepseek_thinking: str


def load_settings(
    *,
    data_dir: str | Path | None = None,
    llm_backend: str | None = None,
    model: str | None = None,
    max_iterations: int | None = None,
) -> Settings:
    load_dotenv()
    user_config = load_user_config()
    env = os.getenv

    def configured(
        env_names: str | tuple[str, ...],
        config_attr: str,
        default: str | None = None,
    ) -> str | None:
        names = (env_names,) if isinstance(env_names, str) else env_names
        for env_name in names:
            value = env(env_name)
            if value not in (None, ""):
                return value
        config_value = getattr(user_config, config_attr)
        if config_value not in (None, ""):
            return str(config_value)
        return default

    resolved_data_dir = Path(
        data_dir or configured("POP_AGENT_DATA_DIR", "data_dir", "data") or "data"
    ).expanduser()
    return Settings(
        data_dir=resolved_data_dir,
        llm_backend=llm_backend
        or configured("POP_AGENT_LLM_BACKEND", "llm_backend", "mock")
        or "mock",
        api_key=configured(("POP_AGENT_API_KEY", "OPENAI_API_KEY"), "api_key"),
        base_url=(
            configured(
                ("POP_AGENT_BASE_URL", "OPENAI_BASE_URL"),
                "base_url",
                "https://api.openai.com/v1",
            )
            or "https://api.openai.com/v1"
        ).rstrip("/"),
        model=model
        or configured(("POP_AGENT_MODEL", "OPENAI_MODEL"), "model", "gpt-4o-mini")
        or "gpt-4o-mini",
        max_iterations=max_iterations
        or int(configured("POP_AGENT_MAX_ITERATIONS", "max_iterations", "3") or "3"),
        clarity_threshold=int(os.getenv("POP_AGENT_CLARITY_THRESHOLD", "8")),
        request_timeout=float(
            configured("POP_AGENT_REQUEST_TIMEOUT", "request_timeout", "120") or "120"
        ),
        max_retries=int(configured("POP_AGENT_MAX_RETRIES", "max_retries", "3") or "3"),
        deepseek_thinking=configured(
            "POP_AGENT_DEEPSEEK_THINKING", "deepseek_thinking", "disabled"
        )
        or "disabled",
    )
