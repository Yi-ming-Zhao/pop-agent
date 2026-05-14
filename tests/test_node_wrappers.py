import json
import shutil
import subprocess
from pathlib import Path

import pytest


def test_package_json_exposes_pnpm_scripts_and_bins():
    data = json.loads(Path("package.json").read_text(encoding="utf-8"))
    assert data["scripts"]["build"] == "python3 bootstrap.py build"
    assert data["scripts"]["ui:build"] == "python3 bootstrap.py ui-build"
    assert data["scripts"]["postinstall"] == "python3 bootstrap.py install"
    assert data["bin"]["pop-agent"] == "./bin/pop-agent.mjs"


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_node_pop_agent_wrapper_help():
    result = subprocess.run(
        ["node", "bin/pop-agent.mjs", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "doctor" in result.stdout


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_node_bootstrap_wrapper_help():
    result = subprocess.run(
        ["node", "bin/pop-agent-bootstrap.mjs", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "ui-build" in result.stdout
