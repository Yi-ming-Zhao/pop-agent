import pytest

from pop_agent.tui.app import PopAgentTUI
from pop_agent.user_config import provider_config, save_user_config


@pytest.mark.asyncio
async def test_tui_starts_with_mock_config(tmp_path, monkeypatch):
    monkeypatch.setenv("POP_AGENT_CONFIG_DIR", str(tmp_path / "cfg"))
    save_user_config(provider_config("mock", data_dir=str(tmp_path / "data")))
    app = PopAgentTUI()
    async with app.run_test() as pilot:
        assert pilot.app.query_one("#topic-input") is not None
        assert "backend: mock" in str(pilot.app.query_one("#runtime-status").content)


@pytest.mark.asyncio
async def test_tui_opens_install_screen_without_config(tmp_path, monkeypatch):
    monkeypatch.setenv("POP_AGENT_CONFIG_DIR", str(tmp_path / "empty-cfg"))
    monkeypatch.delenv("POP_AGENT_LLM_BACKEND", raising=False)
    monkeypatch.delenv("POP_AGENT_API_KEY", raising=False)
    app = PopAgentTUI()
    async with app.run_test() as pilot:
        await pilot.pause()
        assert pilot.app.screen.query_one("#install-dialog") is not None
