import subprocess
import sys
from pathlib import Path


def test_web_frontend_assets_follow_handoff_contract():
    html = Path("web/src/index.html").read_text(encoding="utf-8")
    css = Path("web/src/styles.css").read_text(encoding="utf-8")
    js = Path("web/src/app.js").read_text(encoding="utf-8")

    assert "design_handoff_pop_agent" in css
    assert "design_handoff_pop_agent" in js
    assert 'grid-template-columns: 248px minmax(0, 1fr) 320px' in css
    assert "--paper: #F7F3E8" in css
    assert "--accent: #1F3A5F" in css
    assert 'const STATE_ORDER = ["empty", "filled", "running", "success", "failed"]' in js
    assert "Teacher" in js
    assert "Student" in js
    assert "Fact check" in js
    assert "Editor" in js
    assert '<div id="app"' in html


def test_web_frontend_builds_into_dist():
    result = subprocess.run(
        [sys.executable, "bootstrap.py", "ui-build"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "Built Web frontend" in result.stdout
    assert Path("web/dist/index.html").exists()
    assert Path("web/dist/styles.css").exists()
    assert Path("web/dist/app.js").exists()

