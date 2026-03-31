```markdown
# 📦 知识库版本检查 & MCP 远程仓库工具

## 知识库版本检查（Skill 调用前自动执行）

**工具仓库路径**: `{{TOOL_REPO_PATH}}`

> 每次会话中**首次调用任意 Skill 之前**，静默执行以下检查（后续调用不再重复）。

**检查流程**:
1. 在终端执行: `git -C "{{TOOL_REPO_PATH}}" fetch origin master 2>&1`
2. 获取落后数量: `git -C "{{TOOL_REPO_PATH}}" rev-list HEAD..origin/master --count`
3. 如果 count == 0 → 不输出任何内容，直接执行 Skill
4. 如果 count > 0 → 使用 `ask_questions` 提示用户:

```
header: "知识库更新"
question: "检测到知识库有 {count} 个新更新。建议更新后再执行 Skill 以获得最佳效果。是否现在更新？"
options:
  - label: "立即更新"
    description: "执行 git pull 拉取最新知识库，然后继续当前任务"
    recommended: true
  - label: "跳过，继续任务"
    description: "使用当前版本继续，下次再更新"
```

5. 用户选择"立即更新" → 执行 `git -C "{{TOOL_REPO_PATH}}" pull origin master`
6. 用户选择"跳过" → 直接继续执行 Skill

> ⚠️ **注意**: 如果 git fetch 超时或失败（如无网络），静默跳过，不影响 Skill 正常执行。

---

## ☁️ 远程仓库 MCP 工具

<!-- 🤖 AI 填充指南
将以下提示词发送给你的 AI 助手：

---
我配置了远程代码仓库的 MCP 访问，仓库信息如下：
- 仓库管理平台: [Azure DevOps / GitHub / GitLab]
- 需要远程访问的仓库列表:
  - [仓库名1] (分支: [分支名])
  - [仓库名2] (分支: [分支名])

请帮我生成 MCP 工具使用规范，包含搜索代码和读取文件的参数模板。
---
-->

### 已配置的远程仓库

| 仓库名 | 分支 |
|--------|------|
| `{{PLATFORM_REPO}}` | `{{PLATFORM_BRANCH}}` |

### 🔴 强制规则：搜索和读取代码时必须指定仓库

**1. 搜索代码** - 必须指定仓库过滤器：

```json
{
  "filters": { "Repository": ["{{PLATFORM_REPO}}"] },
  "searchText": "<搜索关键词>"
}
```

**2. 读取文件** - 必须指定分支版本：

```json
{
  "repositoryId": "{{PLATFORM_REPO}}",
  "path": "/路径/文件名",
  "versionType": "branch",
  "version": "{{PLATFORM_BRANCH}}"
}
```

> ⚠️ **禁止**: 搜索时不指定仓库过滤器 — 会返回无关仓库的结果
> ⚠️ **禁止**: 读取文件时不指定分支版本 — 可能读到错误版本

### 💡 MCP 服务启动说明

MCP 服务首次使用时需要初始化，可能需要：
1. 等待 `npx` 下载 MCP 服务器包
2. 在 VS Code 输出面板查看 MCP 日志确认服务已启动
3. 如果工具不可用，尝试重新打开 Chat 窗口

> 📌 访问远程仓库时，同样可以使用本地域专家来指导开发。
> 域专家会指导 AI 先在工作区搜索代码，工作区没有再通过 MCP 搜索远程仓库。

```
