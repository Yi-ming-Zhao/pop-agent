from pop_agent.install import format_connection_error, save_user_config_without_test
from pop_agent.user_config import UserConfig, load_user_config

import httpx


def test_format_connection_error_mentions_proxy(monkeypatch):
    monkeypatch.setenv("HTTPS_PROXY", "http://127.0.0.1:21990")
    message = format_connection_error(
        RuntimeError("TLS/SSL connection has been closed (EOF) (_ssl.c:997)")
    )
    assert "TLS" in message
    assert "http://127.0.0.1:21990" in message
    assert "保存当前配置" in message


def test_format_connection_error_for_401_does_not_blame_proxy(monkeypatch):
    monkeypatch.setenv("HTTPS_PROXY", "http://127.0.0.1:21990")
    request = httpx.Request("POST", "https://api.deepseek.com/chat/completions")
    response = httpx.Response(401, request=request)
    message = format_connection_error(
        httpx.HTTPStatusError("401 Unauthorized", request=request, response=response)
    )
    assert "认证失败" in message
    assert "网络和代理已经连通" in message
    assert "代理端口" not in message


def test_save_user_config_without_test(tmp_path, monkeypatch):
    monkeypatch.setenv("POP_AGENT_CONFIG_DIR", str(tmp_path / "cfg"))
    ok, message = save_user_config_without_test(
        UserConfig(
            provider="deepseek",
            llm_backend="openai-compatible",
            api_key="sk-test",
            base_url="https://api.deepseek.com",
            model="deepseek-v4-pro",
        )
    )
    assert ok
    assert "已保存配置" in message
    assert load_user_config().api_key == "sk-test"
