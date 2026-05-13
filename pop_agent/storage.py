from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from pydantic import BaseModel

from .models import RunPaths


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_json(path: Path, model_or_data: BaseModel | dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(model_or_data, BaseModel):
        data = model_or_data.model_dump(mode="json")
    else:
        data = model_or_data
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def create_run_paths(data_dir: Path) -> RunPaths:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = f"run_{stamp}_{uuid4().hex[:8]}"
    run_dir = data_dir / "runs" / run_id
    paths = RunPaths(
        run_id=run_id,
        run_dir=run_dir,
        drafts_dir=run_dir / "drafts",
        feedback_dir=run_dir / "feedback",
        final_dir=run_dir / "final",
    )
    for path in [paths.drafts_dir, paths.feedback_dir, paths.final_dir]:
        path.mkdir(parents=True, exist_ok=True)
    return paths
