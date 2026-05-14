## 1. OpenSpec

- [x] 1.1 创建 TUI 前端变更 proposal、design、tasks 和规格增量。
- [x] 1.2 通过 `openspec-cn validate add-cli-tui-frontend` 校验变更。

## 2. 配置和安装

- [x] 2.1 实现用户级配置文件读写、provider 预设、脱敏展示和配置优先级合并。
- [x] 2.2 实现安装向导可用的连接测试与配置保存逻辑。

## 3. Slash Commands

- [x] 3.1 实现 slash command 元数据、解析器和异步分发器。
- [x] 3.2 支持 `/help`、`/generate`、`/memory`、`/run`、`/settings`、`/install`、`/exit`。

## 4. 全屏 TUI

- [x] 4.1 实现 `pop-agent tui` 全屏 Textual 应用。
- [x] 4.2 实现生成、记忆、运行记录、设置、帮助标签页和底部 slash command 输入。
- [x] 4.3 实现首次使用安装向导，并支持从 TUI 重新打开。
- [x] 4.4 在 TUI 中展示多 Agent 生成阶段进度和最终文章路径。

## 5. 文档和测试

- [x] 5.1 更新 README，说明 TUI、安装向导、slash commands 和用户配置。
- [x] 5.2 增加配置、slash command 和 TUI 启动测试。
- [x] 5.3 运行 Python 测试和 OpenSpec 校验。
