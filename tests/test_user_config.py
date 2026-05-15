import os
import stat

from pop_agent.config import load_settings
from pop_agent.user_config import (
    UserConfig,
    format_user_config,
    load_user_config,
    save_user_config,
)


def test_user_config_save_load_permissions_and_redaction(tmp_path, monkeypatch):
    monkeypatch.setenv("POP_AGENT_CONFIG_DIR", str(tmp_path / "cfg"))
    config = UserConfig(
        provider="deepseek",
        llm_backend="openai-compatible",
        api_key="sk-1234567890",
        base_url="https://api.deepseek.com",
        model="deepseek-v4-pro",
    )
    path = save_user_config(config)

    assert load_user_config().model == "deepseek-v4-pro"
    if os.name != "nt":
        assert stat.S_IMODE(path.parent.stat().st_mode) == 0o700
        assert stat.S_IMODE(path.stat().st_mode) == 0o600
    text = format_user_config()
    assert "sk-1...7890" in text
    assert "sk-1234567890" not in text


def test_load_settings_uses_user_config_and_env_override(tmp_path, monkeypatch):
    monkeypatch.setenv("POP_AGENT_CONFIG_DIR", str(tmp_path / "cfg"))
    monkeypatch.delenv("POP_AGENT_LLM_BACKEND", raising=False)
    monkeypatch.delenv("POP_AGENT_MODEL", raising=False)
    monkeypatch.delenv("POP_AGENT_BASE_URL", raising=False)
    monkeypatch.delenv("POP_AGENT_API_KEY", raising=False)
    save_user_config(
        UserConfig(
            provider="deepseek",
            llm_backend="openai-compatible",
            api_key="from-config",
            base_url="https://api.deepseek.com",
            model="deepseek-v4-pro",
            data_dir=str(tmp_path / "data-from-config"),
        )
    )

    settings = load_settings()
    assert settings.llm_backend == "openai-compatible"
    assert settings.api_key == "from-config"
    assert settings.model == "deepseek-v4-pro"
    assert settings.data_dir == tmp_path / "data-from-config"

    monkeypatch.setenv("POP_AGENT_MODEL", "env-model")
    assert load_settings().model == "env-model"


def test_load_settings_accepts_openai_compatible_env_aliases(tmp_path, monkeypatch):
    monkeypatch.setenv("POP_AGENT_CONFIG_DIR", str(tmp_path / "cfg"))
    monkeypatch.delenv("POP_AGENT_API_KEY", raising=False)
    monkeypatch.delenv("POP_AGENT_BASE_URL", raising=False)
    monkeypatch.delenv("POP_AGENT_MODEL", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "from-openai-env")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://api.deepseek.com")
    monkeypatch.setenv("OPENAI_MODEL", "deepseek-chat")

    settings = load_settings(llm_backend="openai-compatible")

    assert settings.api_key == "from-openai-env"
    assert settings.base_url == "https://api.deepseek.com"
    assert settings.model == "deepseek-chat"
