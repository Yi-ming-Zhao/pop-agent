## 1. 项目骨架

- [x] 1.1 创建 Python 包结构、依赖配置和 CLI 入口。
- [x] 1.2 定义核心数据模型、运行状态、artifact 和配置对象。

## 2. LLM 与 Agent 运行时

- [x] 2.1 实现 OpenAI-compatible LLM adapter 和 mock adapter。
- [x] 2.2 实现教师、学生、聚合、事实检查、编辑 Agent。
- [x] 2.3 实现多 Agent 生成循环、停止条件和运行记录落盘。

## 3. 用户记忆系统

- [x] 3.1 实现 Markdown 用户记忆读写、自动更新和 changelog。
- [x] 3.2 实现记忆 JSON 索引、搜索和学生 Agent 初始化上下文。

## 4. 接口层

- [x] 4.1 实现 Typer CLI 的 generate、memory 和 run 命令。
- [x] 4.2 实现 FastAPI 预留接口并复用同一核心服务。

## 5. 文档与验证

- [x] 5.1 添加测试覆盖 mock 生成流程、记忆搜索、停止条件、CLI/API。
- [x] 5.2 更新 README，说明安装、配置、CLI、API、记忆和多模态扩展。
- [x] 5.3 运行 OpenSpec 校验和 Python 测试并修复问题。
