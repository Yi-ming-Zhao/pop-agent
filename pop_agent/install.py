from __future__ import annotations

import os
from pathlib import Path

import httpx

from .config import Settings
from .llm import make_llm
from .user_config import UserConfig, save_user_config


async def test_user_config_connection(config: UserConfig) -> tuple[bool, str]:
    if config.llm_backend == "mock":
        save_user_config(config)
        return True, "Mock 配置可用：生成流程将不访问网络。"
    if not config.api_key:
        return False, "API key 不能为空。"
    if not config.base_url:
        return False, "Base URL 不能为空。"
    if not config.model:
        return False, "模型名不能为空。"

    settings = Settings(
        data_dir=Path(config.data_dir or "data").expanduser(),
        llm_backend=config.llm_backend,
        api_key=config.api_key,
        base_url=config.base_url.rstrip("/"),
        model=config.model,
        max_iterations=1,
        clarity_threshold=8,
        request_timeout=config.request_timeout or 30,
        max_retries=1,
        deepseek_thinking=config.deepseek_thinking or "disabled",
    )
    try:
        llm = make_llm(settings)
        text = await llm.complete(
            system="You are a connectivity test. Reply with ok.",
            user="请只回复 ok。",
            temperature=0,
        )
    except Exception as exc:  # pragma: no cover - exact network failures vary by provider.
        return False, format_connection_error(exc)
    save_user_config(config)
    preview = text.strip().replace("\n", " ")[:80]
    return True, f"连接测试成功：{preview or 'ok'}"


def save_user_config_without_test(config: UserConfig) -> tuple[bool, str]:
    if config.llm_backend != "mock" and not config.api_key:
        return False, "API key 不能为空。"
    if config.llm_backend != "mock" and not config.base_url:
        return False, "Base URL 不能为空。"
    if config.llm_backend != "mock" and not config.model:
        return False, "模型名不能为空。"
    path = save_user_config(config)
    return True, f"已保存配置：{path}\n未执行连接测试。若之后生成仍失败，请检查代理或网络。"


def format_connection_error(exc: Exception) -> str:
    message = str(exc) or str(getattr(exc, "__cause__", "")) or repr(exc) or exc.__class__.__name__
    if isinstance(exc, httpx.HTTPStatusError):
        return format_http_status_error(exc, message)
    proxy = (
        os.getenv("HTTPS_PROXY")
        or os.getenv("https_proxy")
        or os.getenv("HTTP_PROXY")
        or os.getenv("http_proxy")
        or ""
    )
    lines = [f"连接测试失败：{message}"]
    lowered = message.lower()
    if "tls/ssl" in lowered or "eof" in lowered:
        lines.append("诊断：TLS 握手被提前关闭，常见原因是代理端口/节点不可用，或目标域名没有走正确代理。")
    elif "timed out" in lowered or "timeout" in lowered:
        lines.append("诊断：连接超时，常见原因是直连不可达、代理未启动或网络规则未命中。")
    if proxy:
        lines.append(f"检测到代理：{proxy}")
        lines.append("建议：确认该代理端口可用，并让 api.deepseek.com 走可用代理节点。")
    else:
        lines.append("当前未检测到 HTTP(S)_PROXY 环境变量。")
    lines.append("你也可以先点击“保存当前配置”，修好网络后再生成。")
    return "\n".join(lines)


def format_http_status_error(exc: httpx.HTTPStatusError, message: str) -> str:
    status_code = exc.response.status_code
    lines = [f"连接测试失败：HTTP {status_code}"]
    if status_code == 401:
        lines.append("诊断：服务端已收到请求，但认证失败。网络和代理已经连通。")
        lines.append("请检查 DeepSeek API key 是否完整、有效、未过期，并确认没有粘贴多余字符。")
        lines.append("如果刚重新生成 key，请在安装向导中重新粘贴后再次测试。")
        return "\n".join(lines)
    if status_code == 403:
        lines.append("诊断：认证通过但没有权限访问该资源或模型。")
        lines.append("请确认账号权限、余额和模型访问权限。")
        return "\n".join(lines)
    if status_code == 404:
        lines.append("诊断：接口地址不存在。")
        lines.append("DeepSeek 默认 Base URL 应为 https://api.deepseek.com。")
        return "\n".join(lines)
    if status_code == 429:
        lines.append("诊断：触发频率限制或额度限制。")
        lines.append("请稍后重试，或检查账号额度。")
        return "\n".join(lines)
    if status_code >= 500:
        lines.append("诊断：服务端错误或上游临时不可用。")
        lines.append("可以稍后重试；如果持续失败，再检查代理节点稳定性。")
        return "\n".join(lines)
    lines.append(message)
    return "\n".join(lines)
