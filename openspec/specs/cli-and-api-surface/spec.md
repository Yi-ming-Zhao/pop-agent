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

#### 场景:调用 DeepSeek
- **当** 用户配置 POP_AGENT_BASE_URL 为 https://api.deepseek.com 且 POP_AGENT_MODEL 为 deepseek-v4-pro
- **那么** 系统必须按 /chat/completions 发送非流式请求，并允许通过 POP_AGENT_DEEPSEEK_THINKING 控制 thinking 参数

#### 场景:临时网络失败
- **当** OpenAI-compatible 请求遇到传输错误或 5xx 响应
- **那么** 系统必须按配置的重试次数进行重试，且不得重试 4xx 客户端错误

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
