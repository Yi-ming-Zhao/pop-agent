from pop_agent.dependencies import (
    check_dependencies,
    format_dependency_report,
    missing_dependencies,
    project_root,
)


def test_dependency_report_includes_runtime_dependencies():
    report = format_dependency_report()
    assert "fastapi>=0.115" in report
    assert "textual>=0.89" in report


def test_runtime_dependencies_are_installed():
    missing = missing_dependencies()
    assert missing == []


def test_project_root_contains_pyproject():
    assert (project_root() / "pyproject.toml").exists()


def test_check_dependencies_can_include_dev():
    statuses = check_dependencies(include_dev=True)
    names = {status.dependency.import_name for status in statuses}
    assert "pytest" in names
    assert "pytest_asyncio" in names
