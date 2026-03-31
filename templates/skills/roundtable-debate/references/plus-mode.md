# Plus-Design 模式 v2.0 - 分层执行与 runSubagent 调用规范

**核心机制**：runSubagent分层执行 → Phase A（4角色并行）→ 检查点A → Phase B（实施派依赖执行）→ 检查点B → Phase C（设计评审组装）→ 6个文件交付

> 🔴 **v2.0 核心改进**：取消融合+核查循环，改为分层执行。实施派参考前4个角色的 KEY_OUTPUT，天然校准质量。

## 📚 详细文档导航

本文件为 Plus 模式主控文档，详细内容已按职责拆分：

| 阶段 | 文件 | 内容 |
|------|------|------|
| **第0步** | [context-collection.md](context-collection.md) | 创建工作目录 + 收集项目上下文（含步骤4/5/7平台检查） |
| **Phase A** | [prompts-phase-a.md](prompts-phase-a.md) | 4角色并行分析 Prompt 模板（架构/效率/质量/成本） |
| **Phase B** | [prompt-phase-b.md](prompt-phase-b.md) | 实施派 Prompt 模板（依赖 Phase A 产出） |
| **检查点+输出** | 本文件（下方） | runSubagent 规则、检查点机制、输出要求 |

> 💡 **AI 执行时**：先读本文件了解整体流程 → 🔴 **强制** read_file context-collection.md → 按需 read_file 其他子文件获取详细 Prompt 模板。
> ⚠️ **context-collection.md 不是可选的**，它包含步骤4/5/7的强制执行细节，跳过它将导致关键步骤缺失。

---

## 🔴 runSubagent 强制规则

```javascript
// ❌ 严禁：单Agent模拟
"假设我是架构师...现在切换为效率派..."

// ✅ 正确：每个角色独立子Agent（5个）
await runSubagent("架构派独立分析", prompt_架构派)
await runSubagent("效率派独立分析", prompt_效率派)
await runSubagent("质量派独立分析", prompt_质量派)
await runSubagent("成本派独立分析", prompt_成本派)
await runSubagent("实施派独立分析", prompt_实施派)  // 🆕
```

---

## 执行流程概览

### 第0步：创建工作目录 + 收集项目上下文（强制）

> 📖 **详细步骤见 [context-collection.md](context-collection.md)**

包含：0.0 检查返讲文档 → 0.1 检测模式 → 0.2 创建工作目录 → 0.3 收集7步：
- 步骤1-3（模块分析、expert skill、平台域专家 Skill）
- 🔴 步骤4（平台组件检查）
- 🔴 步骤5（接口名提取 + context-check.md）
- 步骤6（相似实现搜索）
- 🔴 步骤7（平台源码搜索）

### 检查点0：上下文收集评分（进入 Phase A 前，强制执行）

> 📖 **详细评分卡见 SKILL.md 检查点0**

读取 `context-check.md`，对照评分卡自评（Expert Skill 5分 + 接口名列表 10分 + 平台源码 15分 + 上下文注入 5分 = 35分）。
- 总分 ≥ 25 → 通过，进入 Phase A
- 总分 < 25 → 阻断，返回补充
- 不涉及平台的 PBI → 平台相关项 N/A，按满分计

### Phase A：4角色并行分析

> 📖 **详细 Prompt 模板见 [prompts-phase-a.md](prompts-phase-a.md)**

🔴 Phase A 的 4 个角色逻辑上相互独立（因工具限制按顺序启动），每个角色的 prompt 中注入隔离规则禁止读取其他角色的已有文件。

### Phase B：实施派依赖执行

> 📖 **详细 Prompt 模板见 [prompt-phase-b.md](prompt-phase-b.md)**

🔴 实施派在 Phase B 执行，必须在 Phase A 全部完成且通过检查点A后才启动。

---

## 🔴 检查点机制

### 🔴 检查点A（Phase A 完成后，启动 Phase B 前，强制执行）

对以下4个文件逐一执行 `read_file` 读取前10行，确认文件存在且内容 > 100 bytes：
- `{workDir}/01-architecture.md`
- `{workDir}/02-efficiency.md`
- `{workDir}/03-quality.md`
- `{workDir}/04-cost.md`

对每个文件执行 `grep_search("KEY_OUTPUT_FOR_IMPL_START")`，确认标记存在。

如果任何文件缺失、内容太少、或不含 KEY_OUTPUT 标记 → 重新启动对应 subAgent。

🔴 **必须显示检查结果**：
`✅ 检查点A：01 ✓ | 02 ✓ | 03 ✓ | 04 ✓ — KEY_OUTPUT 标记 4/4 存在`

### 提取 KEY_OUTPUT（检查点A 通过后）

对以下4个文件逐一执行提取：`01-architecture.md`、`02-efficiency.md`、`03-quality.md`、`04-cost.md`

1. 执行 `grep_search("KEY_OUTPUT_FOR_IMPL_START", { includePattern: "{workDir}/{文件名}" })` 定位标记的行号
2. 执行 `read_file("{workDir}/{文件名}", 标记起始行, 标记结束行)` 读取标记之间的内容
3. 将 4 份 KEY_OUTPUT 拼接为一个字符串，注入到实施派 prompt 中

### 🔴 检查点B（Phase B 完成后，强制执行）

执行 `read_file("{workDir}/05-implementation.md", 1, 10)` 确认文件存在且内容 > 100 bytes。

如果 05 文件缺失或内容太少 → 重新执行实施派 subAgent。

🔴 **必须显示检查结果**：
`✅ 检查点B：05-implementation.md ✓ — 文件存在且内容完整`

---

## 🔴 输出要求

### 执行过程展示（必须展示给用户）

```markdown
🪑 **圆桌会议 v2.0 执行过程**

### 第0步：收集上下文
- ✅ 读取 xxx-expert → 了解模块架构
- ✅ 读取 {{PLATFORM_REPO}}-xxx-expert → 提取接口名列表
- ✅ 搜索相似实现 → 复用机会
- ✅ 搜索平台源码 → 读取 N 个源文件（或 N/A）

### 📊 检查点0：上下文收集评分
{显示评分卡表格}
✅ 总分 {X}/35 → 通过

### Phase A：4角色并行分析
- ✅ 架构派🧠 → 01-architecture.md
- ✅ 效率派⚡ → 02-efficiency.md
- ✅ 质量派🛡️ → 03-quality.md
- ✅ 成本派💰 → 04-cost.md

### ✅ 检查点A：4个文件全部存在，KEY_OUTPUT 标记完整

### Phase B：实施派依赖执行
- ✅ 提取 KEY_OUTPUT 摘要（4份）
- ✅ 实施派👨‍💻 → 05-implementation.md

### ✅ 检查点B：05文件存在

### Phase C：设计评审文档组装
- ✅ 读取 design-review-template.md 模板
- ✅ 从 01-05 提取 DESIGN_REVIEW 标记区段（15个）
- ✅ 组装 06-design-review.md

🎯 **交付完成：6个文件已生成**
├── 01-architecture.md  (架构派🧠)
├── 02-efficiency.md   (效率派⚡)
├── 03-quality.md      (质量派🛡️)
├── 04-cost.md         (成本派💰)
├── 05-implementation.md (实施派👨‍💻) ← 编码核心参考
└── 06-design-review.md (主Agent组装) ← 评审文档

### 📊 交付评分卡
{显示交付评分卡表格，见 SKILL.md Phase D 交付评分卡}
✅ 总分 {X}/65 → 交付完成
```

### 最终交付物

> 🔴 **6个文件是最终交付物**：01-05 由 subagent 生成，06 由主Agent组装。不使用融合 subagent。

其中 `05-implementation.md` 是编码的核心参考，`06-design-review.md` 是团队评审文档。
