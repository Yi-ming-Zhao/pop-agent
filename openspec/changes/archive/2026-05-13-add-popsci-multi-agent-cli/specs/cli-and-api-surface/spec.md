## ADDED Requirements

### 需求:命令行生成入口
系统必须提供命令行生成入口，允许用户指定主题、目标读者、用户 ID、最大迭代轮数和 LLM 后端。

#### 场景:CLI 生成文章
- **当** 用户运行 generate 命令并提供主题
- **那么** 系统必须输出最终文章摘要、运行 ID 和结果文件路径

### 需求:命令行记忆管理
系统必须提供命令行记忆管理入口，支持查看、搜索和更新用户记忆。

#### 场景:CLI 查看记忆
- **当** 用户运行 memory show 命令并提供 user_id
- **那么** 系统必须输出该用户的 Markdown 记忆内容或路径

### 需求:FastAPI 预留接口
系统必须提供 FastAPI 应用，使未来 Next.js 前端可以调用同一 Python 核心能力。

#### 场景:API 生成文章
- **当** 客户端调用 POST /api/generate
- **那么** 系统必须返回与 CLI 一致的运行 ID、最终文章、评分和 artifact 元数据

### 需求:Mock 后端
系统必须提供 mock LLM 后端，以便没有真实 API key 时运行测试和演示。

#### 场景:无 API key 测试
- **当** 测试配置使用 mock 后端
- **那么** 系统必须在不访问网络的情况下完成完整生成流程

### 需求:OpenAI-compatible 后端配置
系统必须支持通过环境变量配置 OpenAI-compatible 服务，包括 API key、base URL、模型名、请求超时、重试次数和供应商特定参数。

#### 场景:调用 DeepSeek
- **当** 用户配置 POP_AGENT_BASE_URL 为 https://api.deepseek.com 且 POP_AGENT_MODEL 为 deepseek-v4-pro
- **那么** 系统必须按 /chat/completions 发送非流式请求，并允许通过 POP_AGENT_DEEPSEEK_THINKING 控制 thinking 参数

#### 场景:临时网络失败
- **当** OpenAI-compatible 请求遇到传输错误或 5xx 响应
- **那么** 系统必须按配置的重试次数进行重试，且不得重试 4xx 客户端错误
