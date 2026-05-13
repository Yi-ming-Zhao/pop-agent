## 为什么

当前 `pop-agent` 只有调研报告和 OpenSpec 基础配置，尚没有可运行的科普生成系统。我们需要把 Claude Code 调研中得到的多 Agent、任务状态、上下文控制和记忆机制落到一个可运行的 CLI v1，为后续 FastAPI/Next.js 网页版和多模态输出打基础。

## 变更内容

- 新增 Python 多 Agent 科普生成核心：教师、学生、反馈聚合、事实检查和编辑 Agent。
- 新增命令行入口，支持根据主题、目标读者和用户记忆生成文字科普文章。
- 新增 Markdown 用户记忆系统，自动保存用户认知能力、知识掌握、误解和偏好，并提供高效搜索索引。
- 新增 FastAPI-ready 服务接口，CLI 和未来 Web 共享同一业务内核。
- 新增多模态 artifact 数据结构，v1 只生成文字，但保留图片和视频扩展接口。
- 新增 README、测试和 mock LLM 后端，保证无真实 API key 时也能验证闭环。

## 功能 (Capabilities)

### 新增功能
- `popsci-generation`: 多 Agent 文字科普生成、迭代评估、停止条件和运行状态落盘。
- `user-cognitive-memory`: Markdown 用户记忆、自动更新、搜索索引和学生 Agent 初始化。
- `cli-and-api-surface`: 命令行接口、FastAPI 预留接口和未来 Next.js 对接契约。
- `multimodal-artifacts`: 面向文字、图片、视频等模态的统一 artifact 输出协议，v1 仅启用文字。

### 修改功能

## 影响

- 新增 Python 包、CLI 入口、FastAPI app、测试和项目依赖配置。
- 新增 `data/` 运行时存储约定，保存用户记忆、索引、运行记录和生成结果。
- 更新 README，说明安装、配置、CLI、API、记忆格式和多模态扩展方式。
