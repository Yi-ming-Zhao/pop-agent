import pytest

from pop_agent.slash_commands import dispatch_slash_command, parse_slash_command


def test_parse_slash_command():
    parsed = parse_slash_command('/generate --topic "黑洞"')
    assert parsed is not None
    assert parsed.command_name == "generate"
    assert parsed.args == '--topic "黑洞"'


@pytest.mark.asyncio
async def test_slash_help():
    result = await dispatch_slash_command("/help")
    assert result.action == "message"
    assert "/generate" in result.message
    assert "/memory" in result.message


@pytest.mark.asyncio
async def test_slash_memory_update_and_search(tmp_path):
    result = await dispatch_slash_command(
        "/memory update "
        f"--data-dir {tmp_path} "
        "--user-id alice "
        "--title 黑洞基础 "
        "--summary 用户知道黑洞和强引力有关 "
        "--tags 黑洞,引力"
    )
    assert "Updated:" in result.message

    search = await dispatch_slash_command(
        f"/memory search 黑洞 --user-id alice --data-dir {tmp_path}"
    )
    assert "黑洞基础" in search.message


@pytest.mark.asyncio
async def test_slash_generate_with_mock(tmp_path):
    result = await dispatch_slash_command(
        f'/generate --topic "黑洞为什么不是洞" --audience 初中生 --backend mock --data-dir {tmp_path}'
    )
    assert result.action == "message"
    assert "Generated run_" in result.message
    assert "好的科普" in result.message
