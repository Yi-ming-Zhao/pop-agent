# cli-and-api-surface 规范增量

## 修改需求

### 需求:OpenAI-compatible 后端配置

系统必须支持通过环境变量配置 OpenAI-compatible 服务，包括 API key、base URL、模型名、请求超时、重试次数和供应商特定参数。

当项目专用环境变量和 OpenAI 风格别名同时存在时，项目专用环境变量必须优先。

系统必须支持以下环境变量别名：

- API key: `POP_AGENT_API_KEY` 或 `OPENAI_API_KEY`
- base URL: `POP_AGENT_BASE_URL` 或 `OPENAI_BASE_URL`
- 模型名: `POP_AGENT_MODEL` 或 `OPENAI_MODEL`

#### 场景:从供应商根地址调用 DeepSeek

- **当** 用户配置 `OPENAI_BASE_URL` 或 `POP_AGENT_BASE_URL` 为 `https://api.deepseek.com`
- **并且** 用户选择 OpenAI-compatible 后端
- **那么** 系统必须向 `https://api.deepseek.com/v1/chat/completions` 发送非流式请求
- **并且** 除非 `POP_AGENT_DEEPSEEK_THINKING` 设置为非 disabled 值，否则必须省略 DeepSeek `thinking` 参数

#### 场景:从 SDK 风格 base URL 调用供应商

- **当** 用户配置的 base URL 以 `/v1` 结尾
- **那么** 系统必须只追加一次 `/chat/completions`

#### 场景:CLI 展示生成进度

- **当** 用户运行 CLI `generate` 命令
- **那么** 系统必须在最终文章输出前打印多 Agent 生成流水线的阶段进度

#### 场景:忽略不可读用户配置

- **当** 用户配置文件无法读取或解析
- **那么** 系统必须将用户配置视为未设置
- **并且** 显式参数和环境变量仍然必须生效
