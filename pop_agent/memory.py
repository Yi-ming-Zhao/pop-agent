from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from .models import MemorySearchResult


MEMORY_FILES = {
    "profile": "profile.md",
    "knowledge": "knowledge.md",
    "preferences": "preferences.md",
    "misconceptions": "misconceptions.md",
}


@dataclass(frozen=True)
class MemoryUpdate:
    section: str
    title: str
    summary: str
    tags: list[str]
    confidence: float
    source_run: str


class MemoryStore:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir

    def user_dir(self, user_id: str) -> Path:
        return self.data_dir / "memory" / "users" / safe_id(user_id)

    def index_path(self, user_id: str) -> Path:
        return self.data_dir / "memory" / "index" / f"{safe_id(user_id)}.json"

    def ensure_user(self, user_id: str) -> None:
        directory = self.user_dir(user_id)
        directory.mkdir(parents=True, exist_ok=True)
        defaults = {
            "profile": "# 用户认知画像\n\n",
            "knowledge": "# 知识掌握\n\n",
            "preferences": "# 表达偏好\n\n",
            "misconceptions": "# 常见误解\n\n",
        }
        for section, filename in MEMORY_FILES.items():
            path = directory / filename
            if not path.exists():
                path.write_text(defaults[section], encoding="utf-8")
        changelog = directory / "changelog.md"
        if not changelog.exists():
            changelog.write_text("# 记忆变更记录\n\n", encoding="utf-8")
        self.rebuild_index(user_id)

    def show(self, user_id: str) -> str:
        self.ensure_user(user_id)
        parts = []
        for filename in MEMORY_FILES.values():
            path = self.user_dir(user_id) / filename
            parts.append(f"<!-- {filename} -->\n{path.read_text(encoding='utf-8')}")
        return "\n\n".join(parts)

    def apply_updates(self, user_id: str, updates: list[MemoryUpdate]) -> list[str]:
        self.ensure_user(user_id)
        written: list[str] = []
        for update in updates:
            filename = MEMORY_FILES.get(update.section, MEMORY_FILES["knowledge"])
            path = self.user_dir(user_id) / filename
            entry = format_memory_entry(update)
            existing = path.read_text(encoding="utf-8")
            if update.summary not in existing:
                path.write_text(existing.rstrip() + "\n\n" + entry + "\n", encoding="utf-8")
                written.append(f"{update.section}: {update.title}")
        if written:
            changelog = self.user_dir(user_id) / "changelog.md"
            with changelog.open("a", encoding="utf-8") as fh:
                for item in written:
                    fh.write(f"- {item}\n")
            self.rebuild_index(user_id)
        return written

    def rebuild_index(self, user_id: str) -> list[dict]:
        self.user_dir(user_id).mkdir(parents=True, exist_ok=True)
        entries: list[dict] = []
        for section, filename in MEMORY_FILES.items():
            path = self.user_dir(user_id) / filename
            if not path.exists():
                continue
            entries.extend(parse_memory_file(path, section))
        index = self.index_path(user_id)
        index.parent.mkdir(parents=True, exist_ok=True)
        index.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
        return entries

    def search(
        self,
        user_id: str,
        query: str,
        *,
        limit: int = 5,
    ) -> list[MemorySearchResult]:
        self.ensure_user(user_id)
        index_path = self.index_path(user_id)
        entries = json.loads(index_path.read_text(encoding="utf-8"))
        terms = tokenize(query)
        results: list[MemorySearchResult] = []
        for entry in entries:
            haystack = " ".join(
                [
                    entry.get("title", ""),
                    entry.get("summary", ""),
                    " ".join(entry.get("tags", [])),
                    entry.get("section", ""),
                ]
            ).lower()
            score = sum(1 for term in terms if term in haystack)
            if score == 0 and terms:
                continue
            confidence = float(entry.get("confidence", 0.5))
            results.append(
                MemorySearchResult(
                    path=entry["path"],
                    title=entry.get("title", ""),
                    summary=entry.get("summary", ""),
                    tags=entry.get("tags", []),
                    confidence=confidence,
                    score=score + confidence,
                )
            )
        return sorted(results, key=lambda item: item.score, reverse=True)[:limit]


def safe_id(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]+", "_", value).strip("_") or "default"


def tokenize(text: str) -> list[str]:
    return [part.lower() for part in re.split(r"\W+", text) if part.strip()]


def format_memory_entry(update: MemoryUpdate) -> str:
    tags = ", ".join(update.tags)
    return (
        f"## {update.title}\n\n"
        f"<!-- tags: {tags}; confidence: {update.confidence:.2f}; "
        f"source_run: {update.source_run} -->\n\n"
        f"{update.summary}\n"
    )


def parse_memory_file(path: Path, section: str) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    blocks = re.split(r"^##\s+", text, flags=re.MULTILINE)
    entries: list[dict] = []
    for block in blocks[1:]:
        lines = block.strip().splitlines()
        if not lines:
            continue
        title = lines[0].strip()
        body = "\n".join(lines[1:]).strip()
        meta = parse_meta(body)
        summary = re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL).strip()
        entries.append(
            {
                "path": str(path),
                "section": section,
                "title": title,
                "summary": summary,
                "tags": meta["tags"],
                "confidence": meta["confidence"],
            }
        )
    return entries


def parse_meta(body: str) -> dict:
    match = re.search(r"<!--(.*?)-->", body, re.DOTALL)
    if not match:
        return {"tags": [], "confidence": 0.5}
    raw = match.group(1)
    tags_match = re.search(r"tags:\s*([^;]+)", raw)
    confidence_match = re.search(r"confidence:\s*([0-9.]+)", raw)
    tags = []
    if tags_match:
        tags = [tag.strip() for tag in tags_match.group(1).split(",") if tag.strip()]
    confidence = 0.5
    if confidence_match:
        confidence = float(confidence_match.group(1))
    return {"tags": tags, "confidence": confidence}
