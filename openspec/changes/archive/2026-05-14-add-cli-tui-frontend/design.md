# 设计

## 架构
新增三层：

1. 用户配置层
   - 新增 `pop_agent.user_config`，负责定位用户配置目录、加载/保存 provider 配置、生成 provider 预设、脱敏显示。
   - `load_settings()` 继续作为唯一运行时配置入口，优先级为显式参数 > 环境变量 > 用户配置 > 默认值。

2. 命令分发层
   - 新增 `pop_agent.slash_commands`，提供命令元数据、解析器和异步分发器。
   - 命令处理函数复用 `GenerationService`、`MemoryStore` 和 run storage，不重新实现业务逻辑。

3. TUI 层
   - 新增 `pop_agent.tui.app`，使用 Textual 构建全屏界面。
   - 主界面包含生成、记忆、运行记录、设置、帮助几个标签页，并在底部保留 slash command 输入框。
   - 首次使用或用户主动执行 `/install` 时显示安装向导。

## 用户配置
配置文件默认位于：

```text
$POP_AGENT_CONFIG_DIR/config.json
$XDG_CONFIG_HOME/pop-agent/config.json
~/.config/pop-agent/config.json
```

写入时创建 `0700` 目录和 `0600` 配置文件。API key 只在本地保存，展示时必须脱敏。

## TUI 交互
- 零基础用户可以只使用表单：填写主题、读者、用户 ID 后点击生成。
- 生成过程中展示多 Agent 阶段日志：读取记忆、教师草稿、学生反馈、反馈聚合、事实检查、编辑和记忆更新。
- 进阶用户可以用 `/generate`、`/memory`、`/run`、`/settings`、`/install`、`/help`、`/exit`。

## 服务层扩展
`GenerationService.generate()` 增加可选 progress callback。CLI/API 不传 callback 时行为不变；TUI 传入 callback 以更新阶段日志。
