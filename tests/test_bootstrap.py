import subprocess
import sys


def test_bootstrap_help():
    result = subprocess.run(
        [sys.executable, "bootstrap.py", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "install-deps" in result.stdout
    assert "ui-build" in result.stdout
    assert "pop-agent onboard --install-daemon" in result.stdout


def test_module_entrypoint_help():
    result = subprocess.run(
        [sys.executable, "-m", "pop_agent", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "doctor" in result.stdout
    assert "onboard" in result.stdout


def test_bootstrap_ui_build():
    result = subprocess.run(
        [sys.executable, "bootstrap.py", "ui-build"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "pop-agent" in result.stdout


def test_onboard_help():
    result = subprocess.run(
        [sys.executable, "-m", "pop_agent", "onboard", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "--install-daemon" in result.stdout
