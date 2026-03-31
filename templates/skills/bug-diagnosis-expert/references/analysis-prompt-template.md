# Bug 分析 Prompt 模板

> 本文件由 `bug-diagnosis-expert` 模式A 加载，用于指导 AI 系统性地分析 JSON 数据和 Diff 文件。

---

## 分析框架

当读取完模块的 JSON 数据和关键 Diff 文件后，按以下 6 个维度逐一分析：

### 维度 0：代码级根因分析（勘误+综合）

> 🔴 **核心维度** — 综合开发者自述的原因分析与实际代码 diff，进行事实核查和深度归纳。

**输入**:
- `bugs[].related_prs[].developer_analysis` — 开发者在 PR 中填写的原因分析、解决方案、接口变更、影响范围
- `bugs[].related_prs[].function_changes` — 从 diff 自动提取的函数级变更目录
- `bugs[].related_prs[].review_comments` — PR 审查线程（reviewer 提出的问题和讨论）
- `bugs[].comments` — Bug 工作项讨论评论（开发者围绕问题的讨论）
- `bugs[].related_work_items` — 关联工作项（Bug↔Bug 或 Bug↔PBI 关系，揭示问题间的依赖）
- 对应的 diff 文件 — 完整的代码变更

**分析方法**:
1. 逐 Bug 读取开发者的 `root_cause` 和 `fix_approach`
2. 读取对应的 diff 文件和 `function_changes` 列表
3. **交叉验证**: 开发者说的原因是否与代码修改一致？
   - 开发者说"未触发刷新" → diff 中是否确实加了刷新调用？
   - 开发者说"共享指针问题" → diff 中是否修改了指针持有方式？
4. **补充/纠正**: 如果 diff 揭示了开发者未提及的修改（如额外的 null 检查、try-catch 包裹），标记为"补充发现"
5. **讨论线索**: 读取 Bug `comments` 和 PR `review_comments`，提取有价值的诊断线索：
   - Bug 评论中开发者对问题根因的讨论（如"怀疑是线程问题""复现发现与数据量有关"）
   - PR review 中 reviewer 指出的隐患（如"这里改了但另一个分支没改""建议加锁"）
   - 这些信息可补充 `developer_analysis` 中未涉及的上下文
6. **关联分析**: 从 `related_work_items` 中查看 Bug 间的关联关系：
   - 同一根因的多个 Bug（Related 关系）— 说明问题影响面更大
   - Bug 关联的 PBI — 说明在哪个功能开发过程中引入
7. **归纳**：将多个 Bug 的根因聚类，提炼为模块级别的系统性问题

**输出格式**:
```markdown
## 代码级根因分析

### Bug #{id}: {一句话标题}

| 项目 | 内容 |
|------|------|
| 开发者原因 | {developer_analysis.root_cause 原文摘要} |
| 代码验证 | ✅ 与 diff 一致 / ⚠️ diff 揭示额外问题 / ❌ 与 diff 不符 |
| 实际修改 | {从 function_changes + diff 归纳的修改摘要} |
| 修改函数 | `{ClassName::Method}` (文件路径) |
| AI 综合判断 | {综合开发者说法与代码事实后的一句话根因} |

### 系统性问题归纳
| 问题模式 | 涉及 Bug | 说明 |
|---------|---------|------|
| {模式名} | #{id1}, #{id2} | {从代码级根因归纳的系统性问题} |
```

---

### 维度 1：高频嫌疑文件

**输入**: `file_change_stats` 字段

**分析方法**:
1. 按 `bug_count` 降序排列
2. 对 `is_recurring: true` 的文件（≥3 次 Bug），读取其关联的 diff
3. 从 diff 中判断：是这个文件本身有设计缺陷（如状态管理复杂），还是被其他模块的变更连带影响

**输出格式**:
```markdown
| 排名 | 文件路径 | Bug 次数 | 典型场景 |
|------|---------|---------|---------|
| 1 | `{path}` | {n} | {从 diff 归纳的典型问题场景} |
```

---

### 维度 2：Bug 类型聚类

**输入**: `bugs[].title` + `bugs[].repro_steps` + `bugs[].resolution`

**分类参考**（按现象归类）:

| 类型关键词 | 分类 |
|-----------|------|
| 黑图/不显示/渲染异常 | 显示异常 |
| 崩溃/闪退/空引用/NullRef | 崩溃 |
| 状态不同步/残留/未清理 | 状态管理 |
| 配置缺失/XML未注册 | 配置遗漏 |
| 数据丢失/保存失败 | 数据完整性 |
| 性能/卡顿/超时 | 性能 |
| 切换场景后异常 | 场景切换 |

**输出格式**:
```markdown
| 类型 | 数量 | 占比 | 典型 Bug ID |
|------|------|------|------------|
| {类型} | {n} | {%} | #{id1}, #{id2} |
```

---

### 维度 3：跨模块联动 Bug

**输入**: `cross_module_bugs` + 对应的 diff 文件

**分析方法**:
1. 对每个跨模块 Bug，读取其 diff
2. 分辨：是修改了 A 模块导致 B 模块出问题（联动 Bug），还是 A 和 B 同时有独立 Bug
3. 提取联动模式（如"配准后未通知 VOI 重计算"）

**交叉验证**: 与 `docs/{{APP_NAME}}-功能依赖关系.md` 中的已知依赖进行比对

**输出格式**:
```markdown
| 触发模块 | 受影响操作 | Bug 数 | 典型模式 |
|---------|-----------|--------|---------|
| {模块A} → 本模块 | {具体影响} | {n} | #{id}: {一句话描述} |
```

---

### 维度 4：修复模式归纳

**输入**: `bugs[].related_prs[].developer_analysis` + `bugs[].related_prs[].function_changes` + `bugs[].related_prs[].review_comments` + diff 文件

**分析方法**:
1. 从 `developer_analysis.root_cause` 提取根因关键词（如"未触发刷新""忘了注册通知""状态未重置"）
2. 从 `developer_analysis.fix_approach` 了解开发者的修复思路
3. 从 `function_changes` 定位具体修改的函数，从 diff 中归纳修复手法（加了什么检查、补了什么调用）
4. 从 PR `review_comments` 中提取 reviewer 对修复方案的疑虑或改进建议
5. 交叉验证开发者自述与实际代码是否一致
6. 聚类相似的修复模式

**输出格式**:
```markdown
| 模式 | 频率 | 说明 |
|------|------|------|
| {模式名} | {高/中/低} | {描述 + 典型 diff 片段} |
```

---

### 维度 5：隐含规则提取

**输入**: 综合以上 4 个维度的分析 + diff 细节 + Bug 评论 + PR review 线程

**关注点**:
- 代码中**注释里提到的约束**（如 "// must call after xxx"）
- **命名不一致**导致的搜索陷阱（如 `Evalution` vs `Evaluation`）
- **线程/并发约束**（如 "只能在 UI 线程调用"）
- **XML 配置的隐式关联**（如 OperateType 字符串必须与某个 enum 匹配）
- **初始化顺序依赖**（如 "必须先 Init 再 Load"）
- **PR review 中暴露的规则**（reviewer 指出的注意事项、历史经验警告）
- **Bug 评论中提到的约束条件**（如"特定数据量才触发""仅在某个模态下复现"）

**输出格式**:
```markdown
## 隐含规则（从 Diff 提取）
- ✅ {规则描述} —— 来源: Bug #{id}, PR #{prId}
```

---

## 诊断检查表

> 基于以上 6 个维度的分析结果，按症状类型生成诊断检查表，供开发者排查新 Bug 时参考。

**生成方法**:
1. 从维度 2 的 Bug 类型聚类中提取各类型的常见症状
2. 从维度 0 的代码级根因分析中提取每个症状对应的排查步骤
3. 从维度 1 的高频嫌疑文件中关联首要排查文件

**输出格式**（追加到 bug-patterns.md 末尾）:
```markdown
## 诊断检查表

### 症状：{症状描述}（如"崩溃/闪退"）
1. [ ] 检查 `{高频嫌疑文件}` 中的 `{函数}` —— 历史 Bug #{id} 曾因此崩溃
2. [ ] 确认 {检查项} —— {原因说明}
3. [ ] ...

### 症状：{症状描述}（如"数据不显示"）
1. [ ] ...
```

---

## 输出质量检查

生成 `bug-patterns.md` 后，自查：

| 检查项 | 标准 |
|--------|------|
| 代码级根因有交叉验证 | 开发者自述与 diff 代码逐一比对，标注一致/不符/补充 |
| Bug 讨论和 review 线索已利用 | 有价值的评论已融入根因分析或隐含规则 |
| 高频文件有 diff 依据 | 不是纯粹按数量排序，而是有业务解释 |
| Bug 类型覆盖 ≥3 类 | 防止分类过粗 |
| 跨模块联动有具体模式 | 不是简单列出"跨了哪些模块" |
| 隐含规则有 Bug 来源 | 每条规则可追溯 |
| 修复模式有代码级描述 | "加了 null 检查"而非"修复了问题" |
| 诊断检查表按症状组织 | 每类症状有 2+ 条具体排查步骤 |
| 关联工作项已标注 | Bug↔Bug 关系揭示问题传播路径 |

---

## AI 建议生成规则

当分析发现以下类型的规则时，追加到 `experience-notes.md` 的 🤖 区域：

| 规则类型 | 是否生成建议 | 原因 |
|---------|:-----------:|------|
| 高频文件标记 | ✅ | 团队可以确认或补充更精确的嫌疑文件 |
| 隐性依赖发现 | ✅ | 需要人工验证是否普遍适用 |
| 命名陷阱 | ✅ | 团队确认后可固化 |
| 纯统计性结论 | ❌ | 已在 bug-patterns.md 中体现 |
| 代码级修复模式 | ❌ | 太细节，不适合经验笔记 |

生成格式：
```markdown
- ⏳ {建议内容} —— 🤖 AI {YYYY-MM-DD}，来源: Bug #{id}
```

---

## 附录：JSON 数据字段参考

> 每个模块 JSON 文件的数据结构说明，分析时按需使用。

### Bug 级别字段

| 字段路径 | 说明 | 用途 |
|---------|------|------|
| `bugs[].id` | Bug ID | 引用标识 |
| `bugs[].title` | 标题 | Bug 类型聚类 |
| `bugs[].state` | 状态（Done/Resolved/Closed） | 过滤条件 |
| `bugs[].severity` | 严重级别 | 加权分析 |
| `bugs[].repro_steps` | 重现步骤（前 1500 字符） | 场景理解 |
| `bugs[].resolution` | 解决描述 | 修复方式概述 |
| `bugs[].area_path` | 区域路径 | Area Path 模块匹配 |
| `bugs[].matched_modules` | 匹配的模块列表 | 归入哪个模块分析 |
| `bugs[].comments` | Bug 讨论评论列表 | 🆕 开发者围绕问题的讨论线索 |
| `bugs[].comments[].author` | 评论者 | 识别角色（开发/测试/PM） |
| `bugs[].comments[].text` | 评论内容（前 500 字符） | 诊断线索、补充上下文 |
| `bugs[].related_work_items` | 关联的其他工作项 | 🆕 Bug↔Bug / Bug↔PBI 关系 |
| `bugs[].related_work_items[].id` | 关联项 ID | 追踪关联 |
| `bugs[].related_work_items[].type` | 关联类型（Bug/PBI/Task） | 区分关系性质 |
| `bugs[].related_work_items[].relation` | 关系名（Related/Parent 等） | 理解关联语义 |

### PR 级别字段

| 字段路径 | 说明 | 用途 |
|---------|------|------|
| `bugs[].related_prs[].pr_id` | PR ID | 引用标识 |
| `bugs[].related_prs[].repo_name` | 所属仓库名 | 🆕 区分应用层/平台层修改 |
| `bugs[].related_prs[].title` | PR 标题 | 修复概述 |
| `bugs[].related_prs[].author` | 提交者 | 开发者识别 |
| `bugs[].related_prs[].developer_analysis` | 开发者自述分析 | 代码级根因核心来源 |
| `bugs[].related_prs[].function_changes` | 函数级变更目录 | diff 快速导航 |
| `bugs[].related_prs[].diff_file` | diff 文件路径 | 读取完整代码变更 |
| `bugs[].related_prs[].diff_stats` | diff 统计 | 变更规模评估 |
| `bugs[].related_prs[].changed_files` | 变更文件清单 | 高频文件统计 |
| `bugs[].related_prs[].review_comments` | PR Review 线程列表 | 🆕 reviewer 反馈和讨论 |
| `bugs[].related_prs[].review_comments[].file_path` | 评论关联文件 | 定位讨论焦点 |
| `bugs[].related_prs[].review_comments[].status` | 线程状态 | active/fixed/closed |
| `bugs[].related_prs[].review_comments[].author` | reviewer | 识别评审者 |
| `bugs[].related_prs[].review_comments[].content` | 评论内容（前 300 字符） | 审查意见、隐患提示 |

### 跨仓库分析提示

当 `repo_name` 为平台仓库（如 `{{PLATFORM_REPO}}`）时，说明该 Bug 的根因在平台层：
- 应用层可能只是触发者，根本修复在平台
- 跨层 Bug 的修复模式通常涉及接口变更或状态管理
- 这类 Bug 更可能影响多个应用
