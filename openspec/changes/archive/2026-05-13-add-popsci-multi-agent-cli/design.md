## 上下文

`pop-agent` 当前没有可运行应用，只有 README、OpenSpec 配置和两份 Claude Code 调研报告。上级 `Auto-PopSci` 项目提供了 Python/FastAPI 评测经验，但本变更不直接依赖其代码。目标是在本仓库建立可运行的 Python 多 Agent 科普生成核心，并同时服务 CLI v1 与未来 Web/API。

## 目标 / 非目标

**目标：**
- 提供可运行的 CLI 文字科普生成闭环。
- 使用教师、学生、聚合、事实检查、编辑 Agent 的固定流水线。
- 以 Markdown 保存用户认知记忆，并用 JSON 索引高效检索。
- 使用 OpenAI-compatible LLM adapter，同时提供 mock backend。
- 提供 FastAPI app 和多模态 artifact 协议，便于未来 Next.js 和图片/视频扩展。

**非目标：**
- 不在 v1 实现 Next.js 前端页面。
- 不在 v1 实现真实图片或视频生成。
- 不复制 Claude Code 泄露源码，只借鉴架构思想。
- 不直接集成上级 `Auto-PopSci` 评测模块，后续可作为 evaluator adapter。

## 决策

- **Python core + Typer CLI + FastAPI API。** Python 贴近相邻科普项目生态，FastAPI 能自然承接未来 Web，Typer 提供可维护 CLI。
- **业务内核单一来源。** CLI 和 API 都调用 `pop_agent.core`，避免两套流程分叉。
- **Agent 由 Python 类和 prompt 模板组成。** v1 先不实现动态 Markdown agent loader，保证最小可运行；数据结构保留 agent name、role、model、max_turns，后续可扩展为 Markdown spec。
- **OpenAI-compatible adapter + mock adapter。** 真实环境用 base_url/model/api_key，测试用 mock 保证稳定。
- **Markdown 记忆 + JSON index。** Markdown 便于人工阅读，JSON index 用于按 topic/tag/keyword/confidence 搜索，避免每次加载全部记忆。
- **自动写入记忆。** 生成结束后自动提取候选认知变化并写入 changelog；每条记忆带 source run 和 confidence，降低长期污染风险。
- **artifact-first 输出。** final article 也是 artifact，API/CLI 不依赖单字符串结构，为图片/视频预留接口。

## 风险 / 权衡

- 自动记忆可能误判用户知识状态 → 每条记忆记录来源、置信度和 changelog，便于追踪和后续回滚。
- Mock 后端输出质量有限 → 测试只验证流程、schema 和存储，真实质量由 OpenAI-compatible 后端承担。
- v1 没有真实检索 fact checker → 保留结构化风险检查接口，先检查稿件内部声明和简化风险，后续接搜索工具。
- Markdown 搜索不是语义向量检索 → v1 用关键词/标签/主题匹配，接口保留替换为 embedding index 的空间。
