from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    llm_backend: str
    api_key: str | None
    base_url: str
    model: str
    max_iterations: int
    clarity_threshold: int


def load_settings(
    *,
    data_dir: str | Path | None = None,
    llm_backend: str | None = None,
    model: str | None = None,
    max_iterations: int | None = None,
) -> Settings:
    load_dotenv()
    resolved_data_dir = Path(
        data_dir or os.getenv("POP_AGENT_DATA_DIR", "data")
    ).expanduser()
    return Settings(
        data_dir=resolved_data_dir,
        llm_backend=llm_backend or os.getenv("POP_AGENT_LLM_BACKEND", "mock"),
        api_key=os.getenv("POP_AGENT_API_KEY"),
        base_url=os.getenv(
            "POP_AGENT_BASE_URL", "https://api.openai.com/v1"
        ).rstrip("/"),
        model=model or os.getenv("POP_AGENT_MODEL", "gpt-4o-mini"),
        max_iterations=max_iterations
        or int(os.getenv("POP_AGENT_MAX_ITERATIONS", "3")),
        clarity_threshold=int(os.getenv("POP_AGENT_CLARITY_THRESHOLD", "8")),
    )
