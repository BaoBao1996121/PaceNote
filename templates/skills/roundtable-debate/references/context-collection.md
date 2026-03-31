# 第0步：创建工作目录 + 收集项目上下文（强制）

> ⚠️ **开始子Agent分析前，主Agent必须先检查输入、确定模式、创建工作目录并收集项目上下文**

## 0.0 检查需求返讲文档（首先执行）

按以下优先级检查用户是否提供了需求返讲文档：

1. **优先级1**：用户在请求中直接提供了返讲文档内容（含"需求返讲"或"返讲文档"关键词）→ 直接提取内容使用
2. **优先级2**：用户提供了 `.md` 文件路径 → 执行 `read_file(文件路径)` 读取
3. **优先级3**：以上都没有 → 询问用户：
   > "是否有最新的需求返讲文档？如果有，请提供内容或文件路径；如果没有，将直接基于 PBI 描述进行设计"

如果获取到返讲文档内容，将其作为 `contextBlock` 的一部分（`## 需求返讲文档` 区段），注入后续所有 subAgent prompt。

## 0.1 检测模式：首次 or 修订

检查同 PBI 是否已有圆桌会议产出：

1. 执行 `list_dir("{projectRoot}/.copilot-temp")`，筛选以 `roundtable-` 开头的目录
2. 对每个匹配的目录，执行 `read_file("{目录}/01-architecture.md", 1, 10)` 读取文件头几行
3. 检查文件内容是否包含当前 PBI ID：
   - **匹配** → 询问用户选择修订模式或重新执行
   - **不匹配** → 继续检查下一个目录
4. 全部不匹配 → 首次模式，分配新编号

**修订模式**：读取已有 01-06 → 分析修改意见 → 定向修改受影响文档 → 检查级联影响 → 更新 06 变更记录 → Phase D 重新发布

**首次模式**：继续下方 0.2 → Phase A → B → C → D 完整流程

## 0.2 创建工作目录（首次模式，必须最先执行）

1. 确保临时目录存在：如果 `{projectRoot}/.copilot-temp` 不存在，执行 `create_directory` 创建
2. 查找现有编号：`list_dir(".copilot-temp")` 筛选 `roundtable-*` 目录，提取最大编号
3. 分配新编号：最大编号 + 1，格式 3 位数补零（如 `001`、`002`）
4. 创建工作目录：`create_directory("{projectRoot}/.copilot-temp/roundtable-{NNN}")`

后续所有文件都写入这个工作目录。

## 0.3 收集步骤（首次模式，共7步）

> ⚠️ **以下7个步骤全部为自然语言指令，AI 必须按顺序逐步执行，不是示例代码！**
> 🔴 **步骤4/5/7 是核心步骤，禁止跳过。**

**步骤1：分析 PBI 涉及哪些模块**

根据 PBI 标题和描述中的关键词，判断涉及的功能模块。例如 `["voi", "save", "tissue"]`。

**步骤2：读取相关 expert skill**

对每个涉及的模块，执行 `read_file("{project}/.github/skills/{模块名}-expert/SKILL.md")`。

**步骤3：读取平台层 expert skill**

执行 `read_file("{project}/.github/skills/{{PLATFORM_PREFIX}}-{领域}-expert/SKILL.md")`，如 `{{PLATFORM_REPO}}-datasave-expert`。

**步骤3B：读取运行时配置文件（了解 FE↔BE 通路映射）**

当 PBI 涉及 FE↔BE 通信时，读取项目中的 XML 配置文件：

1. **发现配置路径**：
   - 标准路径: `file_search("**/appdata/*/config/[你的配置目录]/[配置文件]")`
   - 拆分路径: `file_search("**/BE/appdata/*/config/[你的配置目录]/[配置文件]")`
   - 均未找到 → 跳过，标注「⚠️ 未找到运行时配置文件」

2. **读取核心文件**（3 个核心 + 3 个可选）：
   - `[后端配置文件]` — FE→BE Operation 路由、Widget/Model 注册
   - `BE/WorkflowController.xml` — Controller 级 Operation 链
   - `[前端命令配置]` — BE→FE 消息路由（注意文件名拼写）
   - 可选: `[前端配置文件]`、`FE/EventHandler.xml`、`[前端容器配置]`

3. **提取模块相关条目**：按步骤1识别的模块关键词筛选 XML 条目，注入 contextBlock「运行时配置映射」区段

### 🔴 步骤4：判断 PBI 是否涉及平台组件（必须执行）

检查 PBI 标题/描述是否包含以下任一关键词：
`DataLoad` / `DataSave` / `ROI` / `VOI` / `TissueControl` / `MaskData` / `Volume` /
`Layout` / `Cine` / `VRT` / `Palette` / `Density` / `SUV` / `DataLinkage` / `ImageTools`

- **匹配** → 标记 `涉及平台组件 = 是`，继续步骤5
- **不匹配** → 标记 `涉及平台组件 = 否`，步骤5写N/A，步骤7整体跳过

🔴 **必须显示判定结果**：
`📋 步骤4判定：涉及平台组件 = {是/否}，匹配关键词：{列表，或“无”}`

### 🔴 步骤5：提取接口名列表 + 创建 context-check.md（必须执行）

**5a.** 如果步骤4判定涉及平台组件：从步骤3读取的 平台域专家 Skill 中，提取「核心接口速查」表中的**所有接口名和类名**。

**5b.** 执行 `create_file("{workDir}/context-check.md", 内容)`，写入结构：
- PBI 信息（ID、是否涉及平台组件、匹配关键词）
- 接口名列表（从 平台域专家 Skill 提取，或 N/A）
- 平台源文件清单（待步骤7完成后填写）

🔴 **阻断点**：确认 context-check.md 已创建，否则不得继续步骤6。

**步骤6：搜索相似实现**

执行 `grep_search("ExportFormat|nifti|导出|Export")` 等与 PBI 相关的关键词，搜索本地项目中的相似代码。

🔴 **必须至少执行1次 grep_search 并显示结果**：
`📋 步骤6：搜索了 {N} 个关键词，发现 {M} 处相似实现`

### 🔴 步骤7：搜索平台层源码（涉及平台组件时强制执行，不可跳过）

> ⚠️ **步骤4标记「涉及平台组件 = 是」时，此步骤为强制步骤。**
> **步骤4标记「涉及平台组件 = 否」时，跳过步骤7，直接进入检查点0。**

**7a. 使用步骤5提取的接口名列表作为搜索关键词**

从 `{workDir}/context-check.md`「接口名列表」获取接口名/类名。

降级策略：Tier 1 skill接口速查表 → Tier 2 skill代码搜索建议 → Tier 3 PBI英文关键词

🔴 **不要在应用代码里搜 平台 引用来提取类名** — `using` 语句只有命名空间，没有类名。

**7b. 读取平台源码（本地优先 → MCP 降级）**

**路径A — 本地优先**：
1. `grep_search("接口名", { includePattern: "**/{{PLATFORM_REPO}}/**" })` 定位文件
2. `read_file("头文件.h")` + `read_file("实现文件.cpp")`

**路径B — MCP 降级**（`search_code` 在 On-Premise 不可用，必须用目录浏览方式）：
1. 从 expert skill 获取**模块路径**（如 `BitmapPalette/`），浏览模块根目录：
   `mcp_azuredevops_get_file_content({ repositoryId: "{{PLATFORM_REPO}}", path: "/模块名", versionType: "branch", version: "{{PLATFORM_BRANCH}}" })`
2. 浏览 `BE/src/` 或 `BE/include/` 子目录，定位 `.h` 和 `.cpp` 文件：
   `mcp_azuredevops_get_file_content({ ..., path: "/模块名/BE/src" })`
3. 读取**头文件 + 实现文件**（两者都必须读取）：
   `mcp_azuredevops_get_file_content({ ..., path: "/模块名/BE/src/xxx.cpp" })`
   `mcp_azuredevops_get_file_content({ ..., path: "/模块名/BE/include/{{PLATFORM_PREFIX}}-component-xxx/yyy.h" })`

> 🔴 **只读头文件不够** — 头文件只有签名，必须读取 `.cpp` 实现才能理解逻辑

**7c. 验证检查点（硬阻断 — 不通过则禁止进入检查点0）**

确认至少读取了 **1 个 {{PLATFORM_REPO}} 平台源文件**，并满足以下路径校验：

🔴 **文件路径校验规则**：读取的源文件必须满足以下至少一条：
- 文件路径包含 `{{PLATFORM_REPO}}/` 目录
- 文件通过 MCP 从 `{{PLATFORM_REPO}}` 仓库获取

以下**不算**“平台源文件”：
- ❗ 应用层代码（路径含 `src/{{APP_NAMESPACE}}/` 或类似应用层目录）
- ❗ expert skill 文档中的代码片段摘抄
- ❗ 项目临时文件（如 `docs/temp_*.cs`）

**通过** → 将文件路径追加到 `{workDir}/context-check.md`「平台源文件清单」，标注来源和分类：

```markdown
## 平台源文件清单（步骤7填写）
- ✅ 已读取 {N} 个平台源文件
- 文件列表:
  - {{{PLATFORM_REPO}}/文件路径} — 来源: 本地/MCP — ✅ 平台层
```

**未通过**：
1. 降级到下一 Tier 重试 7b
2. 全部失败 + MCP 不可用 → 降级出口（允许继续，5/15分）
3. 🔴 **MCP 可用但未搜索/未读取** → **禁止进入检查点0**，重新执行 7b
4. 🔴 **读取了文件但路径不含 `{{PLATFORM_REPO}}/` 且非 MCP 获取** → **不计分**，重新搜索正确的平台源文件

🔴 **必须显示搜索路径和结果**：
`📋 步骤7：路径{A/B}，搜索了 {接口名列表}，读取了 {N} 个 {{PLATFORM_REPO}} 文件`

> 🔴 **强制规则**：最终必须读取平台**完整源码**（头文件+实现），不能仅停留在 skill 文档描述层面。

🔴 **阻断点**：步骤7完成（或跳过）后，必须进入检查点0评分，禁止直接启动 runSubagent。

---

## 🔴 检查点0前置验证（在评分前强制执行）

进入检查点0评分之前，必须确认以下每个步骤都有**可见的执行记录**（工具调用或输出格式）：

- [ ] 步骤4：有关键词匹配判定（`📋 步骤4判定：...`）
- [ ] 步骤5：context-check.md 已创建（`create_file` 调用记录）
- [ ] 步骤6：有 `grep_search` 调用记录（`📋 步骤6：...`）
- [ ] 步骤7：有平台源码搜索记录（`📋 步骤7：...`）或“不涉及平台”跳过标注

缺少任一项 → 返回执行该步骤，不得直接评分。

---

## 上下文注入格式（注入到每个 Prompt 开头）

将以下收集结果**全部**注入到每个 subAgent 的 prompt 中：

| 注入项 | 来源步骤 | 说明 |
|--------|----------|------|
| 现有架构 | 步骤2-3 读取的 expert skill | 模块架构、接口规范 |
| 平台能力 | 步骤3 读取的 平台域专家 Skill | 可复用的平台能力 |
| 运行时配置 | 步骤3B 读取的 XML 配置文件 | FE↔BE Operation/消息路由注册 |
| 🔴 接口名列表 | 步骤5 context-check.md | 步骤7搜索关键词 |
| 相似实现代码 | 步骤6 grep_search 发现的代码片段 | 复用参考 |
| 🔴 平台源码 | 步骤5接口名 → 步骤7 read_file 或 MCP 读到的完整源码 | 头文件签名 + 关键方法实现 |
| 项目规范 | expert skill 中的命名/文件组织规范 | 编码规范 |

🔴 **特别注意**：步骤7搜索到的平台源码**必须填入"平台源码"区域**，不能遗漏！
