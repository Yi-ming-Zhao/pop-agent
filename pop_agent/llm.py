from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any

import httpx

from .config import Settings


class LLMClient(ABC):
    @abstractmethod
    async def complete(
        self,
        *,
        system: str,
        user: str,
        temperature: float = 0.2,
    ) -> str:
        raise NotImplementedError


class OpenAICompatibleLLM(LLMClient):
    def __init__(self, settings: Settings) -> None:
        if not settings.api_key:
            raise ValueError("POP_AGENT_API_KEY is required for OpenAI-compatible backend")
        self.settings = settings

    async def complete(
        self,
        *,
        system: str,
        user: str,
        temperature: float = 0.2,
    ) -> str:
        payload = {
            "model": self.settings.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": temperature,
        }
        headers = {"Authorization": f"Bearer {self.settings.api_key}"}
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self.settings.base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


class MockLLM(LLMClient):
    async def complete(
        self,
        *,
        system: str,
        user: str,
        temperature: float = 0.2,
    ) -> str:
        if "TASK:teacher" in system:
            return json.dumps(
                {
                    "title": "把复杂科学讲清楚",
                    "synopsis": "用熟悉的台阶把陌生概念一步步讲明白。",
                    "content": (
                        "科学问题常常像一座高楼。直接把读者带到顶层，"
                        "他们会迷路；更好的做法是先找到已经熟悉的第一层。"
                        "本文先解释现象，再说明原因，最后给出一个生活类比。"
                        "如果遇到新术语，我们会先用一句话定义，再继续往下讲。"
                    ),
                },
                ensure_ascii=False,
            )
        if "TASK:student" in system:
            return json.dumps(
                {
                    "comprehension_score": 8,
                    "interest_score": 7,
                    "restatement": "文章说复杂知识要从我已经懂的东西开始解释。",
                    "confusion_points": [],
                    "recommendation": "stop",
                },
                ensure_ascii=False,
            )
        if "TASK:aggregator" in system:
            return json.dumps(
                {
                    "common_issues": [],
                    "must_fix": [],
                    "nice_to_have": [],
                    "summary": "学生反馈显示当前稿件已经足够清晰。",
                },
                ensure_ascii=False,
            )
        if "TASK:fact_checker" in system:
            return json.dumps(
                {
                    "blocking_issues": [],
                    "warnings": [],
                    "summary": "未发现明显事实阻断问题。",
                },
                ensure_ascii=False,
            )
        if "TASK:editor" in system:
            return json.dumps(
                {
                    "title": "把复杂科学讲清楚",
                    "synopsis": "从熟悉的知识出发，一步步走向新概念。",
                    "content": (
                        "好的科普像带人上楼：先站在读者熟悉的一层，"
                        "再一层一层往上走。每出现一个新术语，都先解释它"
                        "是什么意思；每讲一个原因，都补上中间那一级台阶。"
                        "这样，复杂科学不会变得简单粗暴，而是变得可以理解。"
                    ),
                },
                ensure_ascii=False,
            )
        return "{}"


def make_llm(settings: Settings) -> LLMClient:
    if settings.llm_backend == "mock":
        return MockLLM()
    if settings.llm_backend in {"openai", "openai-compatible"}:
        return OpenAICompatibleLLM(settings)
    raise ValueError(f"Unsupported LLM backend: {settings.llm_backend}")


def parse_json_object(text: str, fallback: dict[str, Any]) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.removeprefix("json").strip()
    try:
        value = json.loads(cleaned)
        return value if isinstance(value, dict) else fallback
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start >= 0 and end > start:
            try:
                value = json.loads(cleaned[start : end + 1])
                return value if isinstance(value, dict) else fallback
            except json.JSONDecodeError:
                return fallback
    return fallback
