# pop-agent

`pop-agent` 是一个面向科普内容生成的多 Agent 系统。当前版本优先提供命令行体验，同时把核心能力封装成 Python 服务层，方便后续接入 FastAPI 和 Next.js 网页端。

## 核心能力

- **教师 Agent**：根据主题、目标读者和用户记忆生成/修订科普文章。
- **学生 Agent**：根据用户认知记忆模拟读者，输出理解评分、复述和困惑点。
- **反馈聚合 Agent**：把学生反馈归纳成必须修复和可选优化。
- **事实检查 Agent**：保留事实风险检查接口，v1 做结构化阻断/警告报告。
- **编辑 Agent**：在不改变事实含义的前提下润色最终稿。
- **Markdown 记忆系统**：保存用户认知能力、知识掌握、误解和表达偏好，并构建 JSON 搜索索引。
- **多模态 artifact 协议**：v1 只生成文字，输出结构已预留 `text | image | video`。

## 安装

```bash
python3 -m pip install -e ".[dev]"
```

默认使用 mock LLM 后端，可以不配置 API key 直接运行。

如需使用 OpenAI-compatible 后端：

```bash
export POP_AGENT_LLM_BACKEND=openai-compatible
export POP_AGENT_API_KEY=your-key
export POP_AGENT_BASE_URL=https://api.openai.com/v1
export POP_AGENT_MODEL=gpt-4o-mini
```

## CLI 使用

生成文章：

```bash
pop-agent generate \
  --topic "黑洞为什么不是洞" \
  --audience "初中生" \
  --user-id "student-001"
```

查看用户记忆：

```bash
pop-agent memory show --user-id student-001
```

搜索记忆：

```bash
pop-agent memory search "黑洞 事件视界" --user-id student-001
```

手动添加记忆：

```bash
pop-agent memory update \
  --user-id student-001 \
  --section knowledge \
  --title "黑洞基础" \
  --summary "用户知道黑洞和强引力有关，但不熟悉事件视界。" \
  --tags "黑洞,事件视界" \
  --confidence 0.8
```

查看运行记录：

```bash
pop-agent run show run_20260513T000000Z_abcd1234
```

## FastAPI 预留接口

启动 API：

```bash
uvicorn pop_agent.api:app --reload
```

主要接口：

- `POST /api/generate`
- `GET /api/runs/{run_id}`
- `GET /api/users/{user_id}/memory`
- `GET /api/users/{user_id}/memory?q=<query>`

未来 Next.js 前端应只调用这些接口，不重新实现生成逻辑。

## 数据目录

默认数据目录是 `data/`，可通过环境变量或 CLI 参数修改：

```bash
export POP_AGENT_DATA_DIR=/path/to/data
```

结构：

```text
data/
  runs/
    run_xxx/
      input.json
      state.json
      report.md
      drafts/
      feedback/
      final/article.md
  memory/
    users/{user_id}/
      profile.md
      knowledge.md
      preferences.md
      misconceptions.md
      changelog.md
    index/{user_id}.json
```

## 记忆格式

用户记忆使用 Markdown 保存，条目示例：

```markdown
## 关于黑洞的理解水平

<!-- tags: 黑洞, comprehension; confidence: 0.70; source_run: run_xxx -->

最近一次生成中，用户画像对应学生 Agent 的理解评分为 8/10。
```

系统会自动更新记忆，并维护 JSON 索引用于学生 Agent 初始化时检索相关认知状态。

## 多模态扩展

生成结果统一放在 `artifacts` 中：

```json
{
  "modality": "text",
  "title": "把复杂科学讲清楚",
  "path": "data/runs/.../final/article.md",
  "mime_type": "text/markdown"
}
```

后续图片或视频版本可以添加 `image` / `video` artifact，而不改变 run 的基本结构。

## 测试

```bash
pytest
openspec-cn validate add-popsci-multi-agent-cli
```

## OpenSpec

本实现对应变更：

```text
openspec/changes/add-popsci-multi-agent-cli/
```

其中包含 proposal、design、specs 和 tasks。
