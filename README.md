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
- **真实模型兼容层**：OpenAI-compatible 后端支持超时、重试、DeepSeek thinking 参数和宽松 JSON 归一化。
- **全屏 TUI 前端**：提供零基础可用的终端界面、安装向导、生成表单、记忆管理、运行记录和 slash commands。

## 从零开始试用

刚 clone 下来时，`pop-agent` 命令还没有被安装到当前环境里，所以不能直接运行 `pop-agent doctor`。第一次应在仓库根目录运行：

```bash
python3 bootstrap.py doctor
python3 bootstrap.py install-deps
```

如果想使用类似 OpenClaw 的 source install 流程，可以运行：

```bash
git clone https://github.com/Yi-ming-Zhao/pop-agent.git
cd pop-agent
python3 bootstrap.py install && python3 bootstrap.py build && python3 bootstrap.py ui-build
python3 bootstrap.py link
pop-agent onboard --install-daemon
```

如果你更习惯 pnpm，也可以使用同样风格的命令：

```bash
git clone https://github.com/Yi-ming-Zhao/pop-agent.git
cd pop-agent
pnpm install && pnpm build && pnpm ui:build
pnpm link --global
pop-agent onboard --install-daemon
```

`pnpm install` 会通过 `postinstall` 调用 `python3 bootstrap.py install` 安装 Python 依赖；`pnpm link --global` 暴露的是一个 Node wrapper，它会转发到 `python3 -m pop_agent`。

这里的 `onboard --install-daemon` 会保存默认 Mock 配置，并安装本机 FastAPI daemon。支持 systemd user service 的环境会写入 `~/.config/systemd/user/pop-agent-api.service` 并尝试启动；否则会生成 `~/.config/pop-agent/daemon/start-api.sh` 启动脚本。

安装完成后再运行：

```bash
pop-agent doctor
pop-agent tui
```

如果 `pop-agent` 没有出现在 PATH，也可以使用模块入口：

```bash
python3 -m pop_agent doctor
python3 -m pop_agent tui
```

想一步进入演示界面，可以运行：

```bash
python3 bootstrap.py tui
```

它会在缺依赖时先安装依赖，再启动 TUI。

## 安装

```bash
python3 -m pip install -e ".[dev]"
```

默认使用 mock LLM 后端，可以不配置 API key 直接运行。

运行依赖：

- `fastapi>=0.115`
- `httpx>=0.27`
- `pydantic>=2.7`
- `python-dotenv>=1.0`
- `rich>=13.7`
- `textual>=0.89`
- `typer>=0.12`
- `uvicorn>=0.30`

开发/测试依赖：

- `pytest>=8.2`
- `pytest-asyncio>=0.23`

如果已经安装过 `pop-agent`，但依赖不完整，可以运行：

```bash
pop-agent doctor
pop-agent install-deps
```

TUI 的安装向导里也提供“检查依赖”和“安装/修复依赖”按钮。不过如果 `textual` 完全没安装，TUI 本身无法启动，这时应先使用 `python3 bootstrap.py install-deps`。

首次使用推荐直接启动全屏 TUI，并在安装向导里选择 DeepSeek、OpenAI-compatible 或 Mock：

```bash
pop-agent tui
```

安装向导会把用户级配置保存到 `$POP_AGENT_CONFIG_DIR/config.json`、`$XDG_CONFIG_HOME/pop-agent/config.json` 或 `~/.config/pop-agent/config.json`。配置目录权限为 `0700`，配置文件权限为 `0600`，界面和 `/settings` 只展示脱敏后的 API key。
如果连接测试提示 TLS/SSL EOF 或超时，通常是代理端口、代理规则或直连网络问题；可以先点击“保存当前配置”，修好代理后再生成。

如需使用 OpenAI-compatible 后端：

```bash
export POP_AGENT_LLM_BACKEND=openai-compatible
export POP_AGENT_API_KEY=your-key
export POP_AGENT_BASE_URL=https://api.openai.com/v1
export POP_AGENT_MODEL=gpt-4o-mini
export POP_AGENT_REQUEST_TIMEOUT=120
export POP_AGENT_MAX_RETRIES=3
```

`POP_AGENT_API_KEY`、`POP_AGENT_BASE_URL` 和 `POP_AGENT_MODEL` 也支持 OpenAI 风格别名
`OPENAI_API_KEY`、`OPENAI_BASE_URL` 和 `OPENAI_MODEL`。如果两组变量同时存在，`POP_AGENT_*`
优先。

DeepSeek 示例：

```bash
export POP_AGENT_LLM_BACKEND=openai-compatible
export POP_AGENT_API_KEY=your-deepseek-key
export POP_AGENT_BASE_URL=https://api.deepseek.com
export POP_AGENT_MODEL=deepseek-v4-pro
export POP_AGENT_DEEPSEEK_THINKING=disabled
```

如果本机使用 `mihomo`/Clash 一类代理，注意 `api.deepseek.com` 可能被 GeoIP 规则判定为直连。直连超时时，需要在代理规则中让 `api.deepseek.com` 走可用代理节点。

## CLI 使用

启动全屏 TUI：

```bash
pop-agent tui
```

TUI 面向零基础用户，包含：

- 生成页：填写主题、目标读者、用户 ID 后点击生成。
- 记忆页：查看、搜索、手动添加用户认知记忆。
- 运行页：输入 run ID 查看历史状态。
- 设置页：查看脱敏配置并重新打开安装向导。
- 底部命令栏：支持 slash commands。

TUI 内可用 slash commands：

```text
/help
/generate --topic "黑洞为什么不是洞" --audience "初中生" --user-id student-001 --backend mock
/memory show --user-id student-001
/memory search "黑洞 事件视界" --user-id student-001
/memory update --user-id student-001 --title "黑洞基础" --summary "用户知道黑洞和强引力有关" --tags "黑洞,引力"
/run show run_20260513T000000Z_abcd1234
/settings
/install
/exit
```

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

真实模型可能返回语义正确但形状不完全严格的 JSON，例如把 `confusion_points` 写成字符串列表。系统会在 Agent 边界将其归一化为包含 `issue`、`impact`、`evidence`、`suggestion` 的结构化反馈，再进入聚合、事实检查和记忆更新。

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
openspec-cn validate --specs
```

## OpenSpec

本实现对应已归档变更：

```text
openspec/changes/archive/2026-05-13-add-popsci-multi-agent-cli/
```

正式规范位于：

```text
openspec/specs/
```

其中包含 CLI/API、科普生成、用户认知记忆和多模态 artifact 协议。归档后的 DeepSeek 真实运行补充已同步到归档 change spec 和主 spec。