from pop_agent.llm import chat_completions_url


def test_chat_completions_url_accepts_api_root():
    assert (
        chat_completions_url("https://api.deepseek.com")
        == "https://api.deepseek.com/v1/chat/completions"
    )


def test_chat_completions_url_accepts_v1_base():
    assert (
        chat_completions_url("https://api.openai.com/v1")
        == "https://api.openai.com/v1/chat/completions"
    )


def test_chat_completions_url_accepts_full_endpoint():
    assert (
        chat_completions_url("https://example.test/v1/chat/completions")
        == "https://example.test/v1/chat/completions"
    )
