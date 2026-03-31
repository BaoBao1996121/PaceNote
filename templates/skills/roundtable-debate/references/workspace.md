# 圆桌会议工作目录规范 v2.0

> ⚠️ **所有分析过程必须持久化到文件，避免上下文截断导致内容丢失。**
>
> 🔴 v2.1：6个文件交付（01-05 subagent生成 + 06 主Agent组装设计评审文档），不使用融合 subagent。

---

## 🔴 工作目录结构

```
{project}/.copilot-temp/
└── roundtable-{NNN}/              # NNN = 3位数编号 (001-999)
    │
    │── Phase A：4角色并行
    ├── 01-architecture.md         # 架构派🧠分析报告 + KEY_OUTPUT + DESIGN_REVIEW
    ├── 02-efficiency.md           # 效率派⚡分析报告 + KEY_OUTPUT + DESIGN_REVIEW
    ├── 03-quality.md              # 质量派🛡️分析报告 + KEY_OUTPUT + DESIGN_REVIEW
    ├── 04-cost.md                 # 成本派💰分析报告 + KEY_OUTPUT + DESIGN_REVIEW + CODING_TASK_LIST
    │
    │── Phase B：实施派依赖执行
    ├── 05-implementation.md       # 实施派👨‍💻（综合前4个KEY_OUTPUT）+ DESIGN_REVIEW + CODING_IMPL
    │
    │── Phase C：设计评审文档组装（主Agent执行）
    └── 06-design-review.md        # 设计评审文档（从01-05的DESIGN_REVIEW标记组装）
```

> ⚠️ **01-05** 由 subagent 生成，**06** 由主Agent组装（非subagent）。

---

## 🔴 编号分配规则（强制）

### 首次模式：分配新编号

圆桌会议启动时，按以下步骤分配工作目录：

1. 确保临时目录存在：如果 `{projectRoot}/.copilot-temp` 不存在，执行 `create_directory` 创建
2. 查找现有编号：`list_dir(".copilot-temp")` 筛选 `roundtable-*` 目录，提取最大编号
3. 分配新编号：最大编号 + 1，格式 3 位数补零（如 `001`、`002`）
4. 创建工作目录：`create_directory("{projectRoot}/.copilot-temp/roundtable-{NNN}")`

### 修订模式：复用已有目录

检测到同 PBI 已有产出时，复用已有目录：

1. 执行 `list_dir("{projectRoot}/.copilot-temp")` 筛选 `roundtable-*` 目录
2. 对每个匹配目录，执行 `read_file("{dir}/01-architecture.md", 1, 10)` 读取头几行
3. 检查内容是否包含当前 PBI ID
4. 匹配 → 复用该目录；不匹配 → 走首次模式

> ⚠️ 修订模式直接在已有文件上编辑，保留 KEY_OUTPUT / DESIGN_REVIEW / CODING 标记结构。

---

## 🔴 各阶段文件操作

### 第0步：创建工作目录

按上方“编号分配规则”创建工作目录。

### Phase A：4角色独立分析 → 写入文件 + KEY_OUTPUT

4个角色逻辑上相互独立（因工具限制按顺序启动），每个角色必须：
1. 将完整分析写入文件（调用 `create_file`）
2. 在文件末尾添加 KEY_OUTPUT 标记

🔴 **隔离规则**：每个角色的 prompt 中注入禁止读取其他角色文件的硬阻断规则，禁止 `read_file` 或 `grep_search` 访问 `roundtable-{NNN}/` 下其他角色的文件。

### 🔴 检查点A → 提取 KEY_OUTPUT

对以下4个文件逐一执行 `read_file` 读取前10行，确认文件存在且内容 > 100 bytes：
- `{workDir}/01-architecture.md`
- `{workDir}/02-efficiency.md`
- `{workDir}/03-quality.md`
- `{workDir}/04-cost.md`

对每个文件执行 `grep_search("KEY_OUTPUT_FOR_IMPL_START")`，确认标记存在。

如果任何文件缺失、内容太少、或不含 KEY_OUTPUT 标记 → 重新启动对应 subAgent。

检查点A 通过后，提取 KEY_OUTPUT：
1. 执行 `grep_search("KEY_OUTPUT_FOR_IMPL_START", { includePattern: "{workDir}/{文件名}" })` 定位行号
2. 执行 `read_file("{workDir}/{文件名}", 起始行, 结束行)` 读取标记间内容
3. 将 4 份 KEY_OUTPUT 拼接注入实施派 prompt

### Phase B：实施派依赖执行

实施派 prompt 包含前4个角色的 KEY_OUTPUT 摘要，执行 `runSubagent("实施派依赖分析", prompt)` 后文件写入 `05-implementation.md`。

### 🔴 检查点B

执行 `read_file("{workDir}/05-implementation.md", 1, 10)` 确认文件存在且内容 > 100 bytes。

如果 05 文件缺失或内容太少 → 重新执行实施派 subAgent。

---

## 📄 KEY_OUTPUT 标记格式

> 前4个角色（01-04）的文件末尾必须包含此标记，供实施派精准提取。

```markdown
<!-- KEY_OUTPUT_FOR_IMPL_START -->
## 🎯 关键产出摘要（供实施派参考）

### 核心结论
- [本角色的核心设计结论，3-5条，简明扼要]

### 实施约束
- [影响编码的关键约束，如技术选型、接口规范、平台限制等]

### 建议关注
- [实施时需要特别注意的点，如风险、依赖、兼容性等]
<!-- KEY_OUTPUT_FOR_IMPL_END -->
```

> 🔴 **控制在 50-80 行**，是全文精华摘要而非复制全文。
> 实施派通过 grep_search + read_file 精准提取，不会读全文。

---

## 📄 DESIGN_REVIEW 标记格式

> 所有角色（01-05）的输出中必须包含此标记，供 Phase C 组装设计评审文档。

```markdown
<!-- DESIGN_REVIEW:X.Y:START -->
{该章节的具体内容（表格/图/代码等）}
<!-- DESIGN_REVIEW:X.Y:END -->
```

### 标记编号与角色映射

| 标记 | 模板章节 | 来源角色 | 来源文件 |
|------|----------|----------|----------|
| `1.1` | 架构图 | 🧠架构派 | `01-architecture.md` |
| `1.2` | 模块职责 | 🧠架构派 | `01-architecture.md` |
| `1.3` | 文件结构 | ⚡效率派 | `02-efficiency.md` |
| `2.1` | 时序图 | 👨‍💻实施派 | `05-implementation.md` |
| `2.2` | 核心类设计 | 🧠架构派 | `01-architecture.md` |
| `2.3a` | 接口设计(C#) | 🧠架构派 | `01-architecture.md` |
| `2.3b` | 接口设计(C++) | 👨‍💻实施派 | `05-implementation.md` |
| `2.4` | 数据结构/Proto | 👨‍💻实施派 | `05-implementation.md` |
| `2.5` | 关键流程 | 👨‍💻实施派 | `05-implementation.md` |
| `3.1` | 技术风险 | 💰成本派 | `04-cost.md` |
| `3.2` | UX风险 | 🛡️质量派 | `03-quality.md` |
| `3.3` | 兼容性 | 🛡️质量派 | `03-quality.md` |
| `4.1` | 自测范围 | 🛡️质量派 | `03-quality.md` |
| `4.2` | 三方兼容测试 | 🛡️质量派 | `03-quality.md` |
| `4.3` | 测试提醒 | 🛡️质量派 | `03-quality.md` |

> 🔴 **KEY_OUTPUT 与 DESIGN_REVIEW 是两套独立标记**：
> - KEY_OUTPUT → Phase B（实施派提取前4角色核心结论）
> - DESIGN_REVIEW → Phase C（主Agent组装设计评审文档）

---

## 📄 CODING 标记格式（供 coding-agent 消费）

> 以下两种标记由圆桌会议生成，供下游 `#coding-agent` Skill 精准提取编码任务。
> 它们与 KEY_OUTPUT / DESIGN_REVIEW 互不干扰，是第三套独立标记体系。

### CODING_TASK_LIST（成本派 04-cost.md）

```markdown
<!-- CODING_TASK_LIST:START -->
| 任务ID | 任务描述 | 工时 | 层级 | 目标文件 | 依赖 | 操作类型 |
|--------|----------|------|------|----------|------|----------|
| BE-01 | ... | 4h | 应用BE | src/... | 无 | 新增 |
| BE-02 | ... | 2h | 平台BE | src/... | BE-01 | 修改 |
| FE-01 | ... | 3h | 应用FE | src/... | BE-01 | 新增 |
<!-- CODING_TASK_LIST:END -->
```

**列说明：**
- **任务ID**: 前缀 `BE-`（后端）/ `FE-`（前端）/ `PB-`（平台），序号两位
- **层级**: `应用FE` / `应用BE` / `平台BE`（对应项目架构层）
- **目标文件**: 相对于项目根的路径，如 `src/{{PLATFORM_NAMESPACE}}.VOI/Export/ExportService.cs`
- **操作类型**: `新增`（create_file）/ `修改`（replace_string_in_file）

### CODING_IMPL:{taskId}（实施派 05-implementation.md）

```markdown
<!-- CODING_IMPL:BE-01:START -->
```csharp
public class ExportService : IExportService
{
    // 实现骨架：关键方法签名 + 核心逻辑注释
    public async Task<ExportResult> ExportAsync(ExportRequest request)
    {
        // 1. 验证参数
        // 2. 获取数据
        // 3. 格式转换
        // 4. 写入文件
    }
}
```
<!-- CODING_IMPL:BE-01:END -->
```

> 每个 CODING_IMPL 块对应 CODING_TASK_LIST 中的一个任务ID。
> coding-agent 通过 `grep_search("CODING_IMPL:{taskId}:START")` 精准提取对应骨架。

### 三套标记体系总览

| 标记 | 生产者 | 消费者 | 用途 |
|------|--------|--------|------|
| `KEY_OUTPUT_FOR_IMPL` | 前4角色 (01-04) | 实施派 (Phase B) | 核心结论摘要 |
| `DESIGN_REVIEW:X.Y` | 所有角色 (01-05) | 主Agent (Phase C) + coding-agent | 设计评审文档组装 + 接口提取 |
| `CODING_TASK_LIST` | 成本派 (04) | coding-agent (Step 1) | 任务拆解表 |
| `CODING_IMPL:{taskId}` | 实施派 (05) | coding-agent (Step 2) | 逐任务实现骨架 |

---

## 📄 Phase C：设计评审文档组装

> 🔴 **Phase C 由主Agent直接执行**（非 subagent），避免内容丢失。

### 组装流程

1. 执行 `read_file("references/design-review-template.md")` 读取模板结构
2. 对以下5个文件逐一执行 `grep_search("DESIGN_REVIEW:.*:START", { includePattern: "{workDir}/{文件名}" })` 定位所有标记：
   - `01-architecture.md`、`02-efficiency.md`、`03-quality.md`、`04-cost.md`、`05-implementation.md`
3. 对每个匹配的标记，提取 START 到 END 之间的内容（`read_file` 按行范围读取）
4. 按模板结构组装，将各区段内容填入对应章节。§5 评审结论**留空**（人工填写）
5. 执行 `create_file("{workDir}/06-design-review.md", 组装后的内容)` 写入文件

### 06-design-review.md 格式

详见 `references/design-review-template.md`，包含：
- §1 概要设计（架构图、模块职责、文件结构）
- §2 详细设计（时序图、类图、接口、数据结构、关键流程）
- §3 可能存在的问题（技术风险、UX风险、兼容性）
- §4 自测与测试范围
- §5 评审结论（留空，人工填写）

---

## 📄 分析报告格式（01-05.md）

```markdown
# {角色}分析报告

> 圆桌会议: roundtable-{NNN}
> 角色: {角色emoji} {角色名}

---

## 1. 分析摘要
{3-5句话总结核心贡献}

## 2. 详细分析
{根据角色职责输出，参考 plus-mode.md 中的输出要求}

## 3. 关键发现
| 发现 | 影响 | 建议 |
|------|------|------|

<!-- KEY_OUTPUT_FOR_IMPL_START -->
## 🎯 关键产出摘要（供实施派参考）
### 核心结论
- ...
### 实施约束
- ...
### 建议关注
- ...
<!-- KEY_OUTPUT_FOR_IMPL_END -->
```

---

## 🔴 文件保留规则（强制 - 禁止删除）

- **永久保留**：任务完成后工作目录**必须保留**，不得删除
- 🚫 **禁止删除**：AI 在任何阶段都**不得**删除、清理、移除工作目录或其中任何文件
- 🚫 **禁止询问**：AI **不得**以任何形式（纯文本、对话框、ask_questions）向用户发起「是否保留/清理/删除中间产物或工作目录」的询问
- **参考价值**：保留的文件可供用户查阅、后续编码参考和 coding-agent 消费

---

## ⚠️ 常见错误

| 错误 | 后果 | 正确做法 |
|------|------|----------|
| subagent不写文件 | 上下文截断导致内容丢失 | 必须 `create_file()` |
| 缺少 KEY_OUTPUT 标记 | 实施派无法精准获取核心结论 | 文件末尾必须有标记 |
| 缺少 DESIGN_REVIEW 标记 | Phase C 无法组装设计评审文档 | 各区段必须有标记 |
| 缺少 CODING_TASK_LIST 标记 | coding-agent 无法解析任务 | 成本派04中添加标记 |
| 缺少 CODING_IMPL 标记 | coding-agent 无法提取骨架 | 实施派05中按任务ID添加 |
| Phase B 前不检查文件 | 可能基于不完整的输入执行 | 检查点A 验证文件存在 |
| 实施派不参考 KEY_OUTPUT | 与前4个角色脱节 | prompt 必须注入摘要 |
| Phase C 用 subagent | 内容丢失（读不完全文） | 主Agent直接执行 |

---

## 🔴 执行检查清单

| 阶段 | 检查项 | 文件 |
|------|--------|------|
| 第0步 | 工作目录已创建 | `.copilot-temp/roundtable-{NNN}/` |
| Phase A | 4个分析报告已写入 | `01-04.md` |
| 检查点A | 文件存在 + KEY_OUTPUT 标记完整 | `01-04.md` |
| Phase B | 实施派报告已写入 | `05-implementation.md` |
| 检查点B | 文件存在且内容充分 | `05-implementation.md` |
| Phase C | 设计评审文档已组装 | `06-design-review.md` |
