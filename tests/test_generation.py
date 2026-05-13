import pytest

from pop_agent.config import load_settings
from pop_agent.models import GenerationRequest
from pop_agent.orchestrator import GenerationService


@pytest.mark.asyncio
async def test_mock_generation_creates_run_and_memory(tmp_path):
    settings = load_settings(data_dir=tmp_path, llm_backend="mock", max_iterations=3)
    service = GenerationService(settings)

    result = await service.generate(
        GenerationRequest(
            topic="黑洞为什么不是洞",
            audience="初中生",
            user_id="student-1",
            llm_backend="mock",
        )
    )

    assert result.run_id.startswith("run_")
    assert result.artifacts[0].modality == "text"
    assert result.final_article.content
    assert result.iterations
    assert result.memory_updates
    assert (tmp_path / "runs" / result.run_id / "state.json").exists()
    assert (tmp_path / "memory" / "users" / "student-1" / "knowledge.md").exists()


@pytest.mark.asyncio
async def test_generation_respects_max_iterations_with_heuristic(tmp_path):
    settings = load_settings(data_dir=tmp_path, llm_backend="mock", max_iterations=1)
    service = GenerationService(settings)
    result = await service.generate(
        GenerationRequest(topic="量子计算", audience="小学生", user_id="u1", max_iterations=1)
    )
    assert len(result.iterations) == 1
