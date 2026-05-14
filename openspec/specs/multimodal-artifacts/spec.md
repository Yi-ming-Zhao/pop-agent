# multimodal-artifacts 规范

## 目的
定义生成结果的统一 artifact 协议，使文字版本和未来图片、视频版本共享同一运行状态与 API 响应结构。
## 需求
### 需求:统一 Artifact 协议
系统必须使用统一 artifact 结构描述生成结果，支持 text、image、video 模态。

#### 场景:文字 v1 输出
- **当** v1 完成生成
- **那么** 系统必须生成 text artifact，并保留 image 和 video 模态的扩展字段

### 需求:多模态接口占位
系统必须在运行状态和 API 响应中保留多模态 artifact 列表，不得将最终输出硬编码为单一字符串。

#### 场景:未来添加图片
- **当** 后续版本新增图片生成 Agent
- **那么** 系统必须能通过新增 image artifact 扩展而不改变 run 基础结构
