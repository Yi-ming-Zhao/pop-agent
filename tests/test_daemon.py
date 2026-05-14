from pathlib import Path

from pop_agent.daemon import render_daemon_script, render_systemd_service


def test_render_systemd_service_contains_api_command(tmp_path):
    text = render_systemd_service(
        project_root=tmp_path,
        data_dir=tmp_path / "data",
        host="127.0.0.1",
        port=8765,
    )
    assert "pop-agent local API daemon" in text
    assert "-m uvicorn pop_agent.api:app" in text
    assert "--host 127.0.0.1 --port 8765" in text


def test_render_daemon_script_quotes_paths(tmp_path):
    project_root = tmp_path / "project with space"
    data_dir = tmp_path / "data with space"
    text = render_daemon_script(
        project_root=project_root,
        data_dir=data_dir,
        host="127.0.0.1",
        port=8765,
    )
    assert "uvicorn pop_agent.api:app" in text
    assert "project with space'" in text
    assert "data with space'" in text
