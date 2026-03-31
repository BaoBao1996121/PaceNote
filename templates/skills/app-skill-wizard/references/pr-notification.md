# PR 创建与飞书通知

> 本文件由 `app-skill-wizard` Step 3 按需加载。
> 两种模式：**本地脚本模式**（多根工作区）和 **MCP 远程模式**（纯目标项目）。

---

## 模式选择

| 模式 | 前提条件 | Step 3 实现方式 |
|------|---------|-----------------|
| **本地脚本** | 工具项目已检出到本地 + 多根工作区 | `create_skill_pr.ps1` |
| **MCP 远程** | 目标项目 MCP 已配置 HSW Collection | MCP `create_branch` → `create_commit` → `create_pull_request` |

AI 根据 Step 0 中用户选择的运行模式决定使用哪种。

---

## 模式 A：本地脚本（`create_skill_pr.ps1`）

### 调用方式

在**工具项目根目录**执行（通过 `run_in_terminal`）：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/create_skill_pr.ps1 `
    -AppName "{AppName}" -AppPrefix "{app}" -ModuleCount {N} `
    -Mode "{Mode}"
```

### 参数说明

| 参数 | 必需 | 说明 |
|------|:----:|------|
| `-AppName` | ✅ | 应用显示名（如 `CardiacCT`） |
| `-AppPrefix` | ✅ | 命名前缀（如 `cardiacct`） |
| `-ModuleCount` | ✅ | 模块数量 |
| `-Mode` | ✅ | `PRAndNotify`（PR+飞书）/ `PROnly`（仅PR）/ `Skip` |
| `-BranchName` | ⬜ | 默认 `skill/{AppPrefix}-experts` |
| `-CommitMessage` | ⬜ | 默认 `feat: add {AppName} expert skills ({N} modules)` |
| `-PRTitle` | ⬜ | 默认同 CommitMessage |
| `-PRDescription` | ⬜ | 默认生成 Markdown 描述 |
| `-FilesToStage` | ⬜ | 默认 `templates/skills/{prefix}-*/SKILL.md` + `references/*.md` + `skill_categories.json` |

### 退出码

| 码 | 含义 | 处理 |
|---|------|------|
| 0 | 全部成功 | 展示 PR 链接 + 通知状态 |
| 1 | 配置错误（无 PAT / 无 remote） | 提示用户运行 GUI 配置 |
| 2 | Git 操作失败 | 检查分支/权限 |
| 3 | PR 创建失败 | 检查 PAT 权限 + Collection 匹配 |
| 4 | 部分成功（PR 成功但通知失败） | 展示 PR 链接，提示手动通知 |

### 结果 JSON 解析

脚本在 `===RESULT_JSON_BEGIN===` 和 `===RESULT_JSON_END===` 之间输出 JSON：

```json
{
    "success": true,
    "branch": "skill/cardiacct-experts",
    "default_branch": "master",
    "pr_id": 20501,
    "pr_url": "https://your-devops-server.example.com/pullrequest/20501",
    "notifications": [
        {"name": "YourName", "email": "your.email@example.com", "status": "sent"}
    ],
    "exit_code": 0
}
```

AI 需要用正则 `===RESULT_JSON_BEGIN===\s*([\s\S]*?)\s*===RESULT_JSON_END===` 从终端输出中提取 JSON。

### PAT 匹配逻辑

脚本从 `data/shared_config.json` + `data/user_preferences.json` 合并配置，按 `git remote get-url origin` 的 Collection URL 匹配 `collection_pats` 中的 PAT。

**常见 401 原因**：`git remote` 的 Collection（如 `HSW`）≠ `org_url` 的 Collection（如 `uGalaxy`）。脚本已处理此情况——它从 remote URL 解析 Collection，独立于 `org_url` 匹配 PAT。

---

## 模式 B：MCP 远程（纯目标项目模式）

### 前提条件

目标项目的 MCP 配置中存在面向 **HSW Collection** 的 azureDevOps server（key: `azureDevOpsHSW`），用于访问工具仓库 `AdvAppCommonKnowledge`。

### 执行步骤

#### B1. 创建分支

```
MCP create_branch:
  projectId: "pioneers"
  repositoryId: "AdvAppCommonKnowledge"
  sourceBranch: "master"
  newBranch: "skill/{app}-experts"
```

> ⚠️ 使用 `azureDevOpsHSW` server（不是默认的 `azureDevOps`）。

#### B2. 推送文件变更

对每个 SKILL.md 文件，使用 `create_commit` 推送：

```
MCP create_commit:
  projectId: "pioneers"
  repositoryId: "AdvAppCommonKnowledge"
  branchName: "skill/{app}-experts"
  commitMessage: "feat: add {AppName} expert skills ({N} modules)"
  changes:
    - path: "templates/skills/{app}-{mod}-expert/SKILL.md"
      patch: "diff --git ... (新文件全量 patch，--- /dev/null)"
    - path: "data/skill_categories.json"
      search: '"presets": {'
      replace: '"presets": {\n    "{AppName}应用开发": ["platform", "{app}"],'
```

**注意事项**：
- 新文件使用 `--- /dev/null` 格式的 unified diff
- `skill_categories.json` 修改使用 search/replace 模式（更安全）
- 每个 commit 最多包含合理数量的文件变更，必要时分多次 commit
- `create_commit` 要求 `search` 文本必须精确匹配文件当前内容

#### B3. 创建 PR

```
MCP create_pull_request:
  projectId: "pioneers"
  repositoryId: "AdvAppCommonKnowledge"
  title: "feat: add {AppName} expert skills ({N} modules)"
  description: "## 新增 Skill\n\n应用: **{AppName}**\n模块数量: **{N}**\n\n由 `#app-skill-wizard` 自动生成"
  sourceRefName: "refs/heads/skill/{app}-experts"
  targetRefName: "refs/heads/master"
  reviewers: ["your.email@example.com"]  # 或用户选择的审阅人
```

#### B4. 飞书通知

使用飞书 MCP 的 `send_message` 工具发送通知，或者直接使用 lark MCP `mcp_lark_tool_batch_send_msg`：

- **收件人**: 从 CP2 用户选择获取（默认: YourName）
- **消息内容**: PR 链接 + 应用名 + 模块数量

### 错误处理

| 场景 | 处理 |
|------|------|
| `azureDevOpsHSW` MCP 不可用 | 提示运行 GUI 重新配置，或手动添加 MCP server |
| `create_commit` search 不匹配 | 先 `get_file_content` 读取最新内容，调整 search 文本 |
| `create_pull_request` 409 冲突 | 同名 PR 已存在，改用 `list_pull_requests` 查找 |
| 飞书通知失败 | 不阻断，降级为展示 PR 链接让用户手动通知 |

---

## 飞书卡片通知格式

两种模式最终通知效果一致：

```
📋 新 Skill PR 待审阅
━━━━━━━━━━━━━━━━━━
应用: {AppName}
Skill 数量: {N} 个模块
分支: skill/{app}-experts
提交时间: {yyyy-MM-dd HH:mm:ss}

[查看 PR]  ← 按钮，链接到 PR 页面
```

---

## 配置依赖

| 配置文件 | 模式 A 读取 | 模式 B 读取 |
|---------|:-----------:|:-----------:|
| `data/shared_config.json` → `lark_config` | ✅ 飞书 token | ⬜ 用 MCP |
| `data/shared_config.json` → `devops_config.collection_pats` | ✅ PAT 匹配 | ⬜ MCP 已配 PAT |
| `data/user_preferences.json` → `devops_config.pat` | ✅ 回退 PAT | ⬜ 不需要 |
