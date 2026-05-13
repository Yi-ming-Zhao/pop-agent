from fastapi.testclient import TestClient

import pop_agent.api as api_module
from pop_agent.config import load_settings


def test_api_generate_with_mock_tmpdir(tmp_path, monkeypatch):
    monkeypatch.setattr(api_module, "load_settings", lambda: load_settings(data_dir=tmp_path, llm_backend="mock"))
    client = TestClient(api_module.app)
    response = client.post(
        "/api/generate",
        json={"topic": "细胞为什么会分裂", "audience": "高中生", "user_id": "api-user"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["run_id"].startswith("run_")
    assert data["artifacts"][0]["modality"] == "text"

    run_response = client.get(f"/api/runs/{data['run_id']}")
    assert run_response.status_code == 200


def test_api_memory_search(tmp_path, monkeypatch):
    monkeypatch.setattr(api_module, "load_settings", lambda: load_settings(data_dir=tmp_path, llm_backend="mock"))
    client = TestClient(api_module.app)
    client.post(
        "/api/generate",
        json={"topic": "火山喷发", "audience": "小学生", "user_id": "api-user"},
    )
    response = client.get("/api/users/api-user/memory?q=火山")
    assert response.status_code == 200
    assert "results" in response.json()
