# Design

## Configuration Resolution

`load_settings()` keeps the existing precedence order:

1. Explicit function arguments.
2. Environment variables.
3. User config file.
4. Defaults.

For OpenAI-compatible fields, environment lookup now accepts both project-specific and OpenAI-style names:

- API key: `POP_AGENT_API_KEY`, then `OPENAI_API_KEY`
- Base URL: `POP_AGENT_BASE_URL`, then `OPENAI_BASE_URL`
- Model: `POP_AGENT_MODEL`, then `OPENAI_MODEL`

Project-specific variables stay first so existing deployments are not changed.

## Endpoint Normalization

The LLM client derives the request URL once during initialization:

- `https://api.deepseek.com` becomes `https://api.deepseek.com/v1/chat/completions`
- `https://api.openai.com/v1` becomes `https://api.openai.com/v1/chat/completions`
- A full `/chat/completions` endpoint is preserved

This removes duplicated call-site string concatenation and makes provider presets and user overrides behave consistently.

## DeepSeek Thinking Parameter

The `thinking` payload key is provider-specific. It is now omitted when `deepseek_thinking` is `disabled`, matching default OpenAI-compatible request behavior. It is only included when a user explicitly sets a non-disabled value.

## Observability

The CLI passes a progress callback into `GenerationService.generate()`, so users can see each pipeline stage. The LLM client also logs the sanitized base URL, model, message count, attempt number, and timeout.

## Failure Handling

Unreadable or malformed user config files are treated like missing config. This prevents a local file permission problem from blocking mock mode or explicit environment-based execution.
