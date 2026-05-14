# Fix OpenAI-Compatible LLM Stability

## Why

Real OpenAI-compatible providers can appear to hang during CLI/TUI generation because the CLI did not surface pipeline progress, common OpenAI environment variables were ignored, and provider base URLs were assembled inconsistently.

DeepSeek users commonly configure `OPENAI_API_KEY` and `OPENAI_BASE_URL`; those values should work without requiring separate `POP_AGENT_*` aliases. The LLM client should also normalize provider roots and SDK-style `/v1` base URLs into one stable chat completions endpoint.

## What Changes

- Accept OpenAI-compatible environment aliases: `OPENAI_API_KEY`, `OPENAI_BASE_URL`, and `OPENAI_MODEL`.
- Normalize chat completions URLs so provider roots and `/v1` base URLs both resolve correctly.
- Send DeepSeek `thinking` only when explicitly enabled.
- Log LLM attempts and failures without exposing API keys.
- Print CLI generation progress so long provider calls are observable.
- Treat unreadable or malformed user config files as absent configuration.

## Impact

- Affects CLI generation, TUI slash-command generation indirectly through the shared service, and OpenAI-compatible provider configuration.
- Adds focused unit coverage for environment aliases and URL normalization.
- No schema or storage migration is required.
