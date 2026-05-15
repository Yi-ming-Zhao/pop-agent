# cli-and-api-surface 规范

## 目的
定义命令行、API、LLM 后端配置和真实服务调用稳定性要求，使 CLI 与未来 Web 前端共享同一核心能力。
## 需求
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

项目专用环境变量必须优先于 OpenAI 风格别名。系统必须支持以下环境变量别名：

- API key: `POP_AGENT_API_KEY` 或 `OPENAI_API_KEY`
- base URL: `POP_AGENT_BASE_URL` 或 `OPENAI_BASE_URL`
- 模型名: `POP_AGENT_MODEL` 或 `OPENAI_MODEL`

运行时配置检测必须把 `OPENAI_API_KEY` 视为有效 API key 配置来源，以免 TUI 在已有
OpenAI-compatible 配置时误判为未配置。

#### 场景:调用 DeepSeek
- **当** 用户配置 `OPENAI_BASE_URL` 或 `POP_AGENT_BASE_URL` 为 `https://api.deepseek.com`
- **并且** 用户选择 OpenAI-compatible 后端
- **那么** 系统必须向 `https://api.deepseek.com/v1/chat/completions` 发送非流式请求
- **并且** 除非 `POP_AGENT_DEEPSEEK_THINKING` 设置为非 disabled 值，否则必须省略 DeepSeek `thinking` 参数

#### 场景:使用 SDK 风格 base URL
- **当** 用户配置的 base URL 以 `/v1` 结尾
- **那么** 系统必须只追加一次 `/chat/completions`

#### 场景:临时网络失败
- **当** OpenAI-compatible 请求遇到传输错误或 5xx 响应
- **那么** 系统必须按配置的重试次数进行重试，且不得重试 4xx 客户端错误

#### 场景:CLI 展示生成进度
- **当** 用户运行 CLI `generate` 命令
- **那么** 系统必须在最终文章输出前打印多 Agent 生成流水线的阶段进度

#### 场景:忽略不可读用户配置
- **当** 用户配置文件无法读取或解析
- **那么** 系统必须将用户配置视为未设置
- **并且** 显式参数和环境变量仍然必须生效

#### 场景:TUI 识别 OpenAI 风格 API key
- **当** 用户配置文件选择 OpenAI-compatible 后端并设置 base URL 和模型名
- **并且** 环境变量只提供 `OPENAI_API_KEY`
- **那么** 系统必须认为运行时配置已存在
- **并且** 不得因为缺少 `POP_AGENT_API_KEY` 而强制打开安装向导

### 需求: 用户级配置优先级
系统必须支持用户级配置文件，并将其作为环境变量和显式参数之外的默认配置来源。

#### 场景: 从用户配置加载模型
- **当** 用户配置文件包含 `llm_backend`、`base_url`、`model` 和 `api_key`
- **并且** 没有对应环境变量覆盖
- **那么** `load_settings()` 必须返回用户配置中的值

#### 场景: 环境变量覆盖用户配置
- **当** 用户配置文件和环境变量同时设置同一个字段
- **那么** 环境变量必须优先于用户配置

### 需求: 用户配置安全写入
系统必须安全写入本地用户配置，避免在展示时泄露完整 API key。

#### 场景: 保存配置文件
- **当** 系统保存用户配置
- **那么** 配置目录权限应为仅当前用户可读写执行
- **并且** 配置文件权限应为仅当前用户可读写

#### 场景: 展示配置
- **当** 用户查看设置
- **那么** API key 必须被脱敏显示

### 需求: 依赖诊断和自动安装命令
系统必须提供命令行依赖诊断和自动安装入口，使用户在 TUI 依赖缺失时仍可修复环境。

#### 场景: Clone 后 Bootstrap
- **当** 用户刚 clone 仓库且 `pop-agent` 命令尚未安装
- **那么** 系统必须提供不依赖第三方包的 bootstrap 入口，用于检查环境和安装项目依赖

#### 场景: Source Install 流程
- **当** 用户运行 `python3 bootstrap.py install && python3 bootstrap.py build && python3 bootstrap.py ui-build`
- **并且** 用户运行 `python3 bootstrap.py link`
- **那么** 系统必须安装依赖、验证 Python/TUI 构建，并把当前 checkout 作为可执行命令链接到当前 Python 环境

#### 场景: PNPM Source Install 流程
- **当** 用户运行 `pnpm install && pnpm build && pnpm ui:build`
- **并且** 用户运行 `pnpm link --global`
- **那么** 系统必须通过 pnpm scripts 安装 Python 依赖、验证构建，并暴露可转发到 Python CLI 的 `pop-agent` 命令

#### 场景: Onboard 安装 daemon
- **当** 用户运行 `pop-agent onboard --install-daemon`
- **那么** 系统必须写入初始用户配置
- **并且** 安装本机 FastAPI daemon 的 systemd user service 或 fallback 启动脚本

#### 场景: 诊断依赖
- **当** 用户运行 `pop-agent doctor`
- **那么** 系统必须列出运行依赖是否已安装

#### 场景: 安装依赖
- **当** 用户运行 `pop-agent install-deps`
- **那么** 系统必须执行本项目的依赖安装流程

#### 场景: TUI 依赖缺失
- **当** 用户运行 `pop-agent tui` 且 Textual 未安装
- **那么** 系统必须提示用户先运行 `pop-agent install-deps`