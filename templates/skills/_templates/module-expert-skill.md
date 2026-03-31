# 功能模块 Skill 统一模板 v4

> **以"确实有用"为唯一标准** — Copilot 靠这个 Skill 找到正确的文件、避免错误的假设。
> 适用于任意平台模块和应用模块。支持 平台生态（平台-*、app-* 等）及全新项目。
>
> **v4 新增**: 平台无关化，代码分层/配置格式/命名空间从 `project-profile.json` 动态注入。

---

## 设计原则

1. **准确性第一** — 所有接口名、类名、枚举名、命名空间、文件路径必须从**实际源码验证**，包括大小写。宁可少写不可写错
2. **索引而非复制** — 只写"名字+路径"让 Copilot 自己 read_file，不展开完整签名（签名会过时）
3. **写搜不到的** — 业务规则、隐性约束、常见陷阱、模块关系 = Copilot 搜代码搜不到的
4. **场景驱动** — "用户想做X → grep 搜Y → 在Z文件" 的三级映射
5. **禁止编造** — 绝不写伪代码或理想化的 API 调用示例；如需示例，只粘贴从源码中复制的真实片段

### v4 变更说明

此模板基于 v3 经验进化而来（v3 对 10 个 app-* 和 8 个 平台-* Skill 的实证对比优化）：
- **v4 新增**: 平台无关化 — 代码分层/配置格式/命名空间改为可配置占位符，从 `project-profile.json` 注入
- **v4 新增**: 来源标记注释（`<!-- source: ... -->`）记录生成质量信息
- **v4 新增**: 配置发现支持 XML/YAML/JSON 多格式，不再仅限 XML
- **v3 保留**: 接口名表格精确、陷阱表防幻觉、禁止伪代码 等核心规则不变
- **向后兼容**: 现有 平台 Skills 不受影响，模板变更只影响新生成的 Skills

---

## 模板结构

> **v4 变更**: 代码分层不再硬编码 FE(C#)/BE(C++)，改为从 `project-profile.json` 的 `layers` 动态构建。
> 对于 平台项目，layers=[{name:"FE",language:"C#"},{name:"BE",language:"C++"}] 等效于 v3 行为。

~~~markdown
---
name: {prefix}-{module}-expert
description: |
  {模块名}专家 - {一句话职责描述}
  触发词: {中文词1}, {中文词2}, {英文词1}, {英文词2}
---

<!-- generated-by: {generator} -->
<!-- source: {document|description|code-analysis|manual} -->
<!-- generated-at: {ISO8601} -->

# {模块名} 专家

> {模块核心职责，一行}

## 执行声明规范

**每次使用本 Skill 时，必须向用户明确告知：**

### 开始执行时
```
🔧 **正在执行: {模块名}专家** (`#{prefix}-{module}-expert`)

✅ 已加载 Skill 指引
⭕ 当前步骤: [步骤描述]
```

### 执行完成时
```
✅ **执行完成**: {模块名}专家

参考来源:
- Skill: `#{prefix}-{module}-expert`
- 应用代码: [来源: 工作区 src/]

产出物: [描述产出]
```

## 模块元信息

| 属性 | 值 |
|------|-----|
| 命名空间 | {namespace_pattern} |
| 代码位置 | {code_location_pattern} |
| 代码层级 | {layers_summary} |

> **平台 示例**: 命名空间 `{{PLATFORM_NAMESPACE}}.{Xxx}` / `{{PLATFORM_NS}}::AppCommonLib`
> **通用示例**: 命名空间 `com.example.{module}` 或 `{module}/src/`

## 核心概念

> 仅写 Copilot 搜不到的领域术语和隐式约定。控制在 5-8 行

| 术语 | 说明 |
|------|------|
| **{DomainTerm1}** | {一句话解释，不超25字} |
| **{DomainTerm2}** | {一句话解释} |

## 搜索策略

1. **本地工作区优先** — `grep_search` 搜索关键词
2. **无结果时** — 根据项目配置选择降级策略:
   - 如有 MCP 远程仓库: `get_file_content` 浏览 `{platform_repo}` 仓库
   - 无 MCP: 提示用户将缺失仓库添加到工作区

> **平台默认配置**: MCP 浏览 `{{PLATFORM_REPO}}` 仓库 `path="/{Module}/BE/include/"`
> **自定义项目**: 从 `project-profile.json` 的 `repos` 读取仓库名称和路径

## 代码入口（从源码验证）

> **v4 动态层级**: 以下子标题从 `project-profile.layers` 动态生成。
> 每个层级一个子标题，格式为 `### {layer.name} 入口 ({layer.language})`
> 无 profile 时保持 平台默认: FE(C#) + BE(C++) + CommonInterface

### {layer_1_name} 入口 ({layer_1_language})

| 类/接口 | 文件路径 | 职责 |
|---------|---------|------|
| `RealClassName` | `{path/to/file}` | {一句话} |

### {layer_2_name} 入口 ({layer_2_language})

| 类/接口 | 文件路径 | 职责 |
|---------|---------|------|
| `real_class_name` | `{path/to/file}` | {一句话} |

### 跨层共享接口（可选）

| 接口 | 文件路径 | 说明 |
|------|---------|------|
| `IXxx` | `{shared_interface_path}` | {用途} |

> **平台等效**: layer_1=[前端语言], layer_2=BE(C++), 跨层=CommonInterface

## 核心流程（可选）

> 仅在流程不能从代码结构直接推断时才写。限制 ≤10 个节点

```
用户操作 → FE ViewModel → SendCommand → BE Operation → [算法/数据处理] → NotifyFE → 刷新渲染
```

> 如果流程更复杂，可用 Mermaid，但节点不超过 10 个，禁止在节点中写伪代码

## 场景入口速查

| 用户想做什么 | grep 关键词 | 从哪个文件入手 |
|-------------|------------|--------------|
| {动词+场景} | `"{Keyword}"` | `{path/to/file}` |

## 调用模式（可选）

> **仅当存在不直观的调用约定时才写**。必须从源码原文复制，禁止编造。每段 ≤5 行，最多 2 段

```cpp
// 从 {file.cpp} 第 {N} 行复制
{真实的调用语句，原样粘贴}
```

## 常见陷阱 / 接口契约

> **必写段落**。Copilot 最容易幻觉的就是名称。5-10 行

| ❌ 错误名称 | ✅ 真实名称 | 说明 |
|------------|-----------|------|
| `WrongName` | `RealName` | {不存在什么，实际是什么} |
| `wrong::Namespace` | `real::Namespace` | {大小写、拼写区别} |

- ✅ {必须遵守的规则} — {原因}
- 🔗 {操作A} → 会影响 `{模块B}` — {怎么影响}

📖 历史 Bug 模式分析见 `references/bug-patterns.md`
📖 团队经验笔记见 `references/experience-notes.md`

## 运行时配置映射（🤖 自动解析 + 🔧 人工校验）

> 许多项目的运行时行为由配置文件驱动，Copilot 搜代码完全看不到。
> 生成 Skill 时 **优先自动读取配置文件提取映射**，提取后标注 `🤖` 待人工校验，校验通过后改为 `✅`。

### 配置文件自动发现

> ⚠️ **生成 Skill 时必须执行此发现流程**，不要跳过直接写占位符。

**发现逻辑**（按优先级尝试）：

```
1. 检查 project-profile.json 的 configDiscovery 字段:
   a. 如有 → 使用 configDiscovery.basePath 和 coreFiles
   b. 如无 → 使用以下默认探测逻辑

2. 默认探测（平台兼容）:
   a. appdata/{appname}/config/
   b. BE/appdata/{appname}/config/ + FE/appdata/{appname}/config/

3. 通用探测（非 平台项目）:
   a. config/
   b. settings/
   c. {仓库根}/*.{yaml,yml,json,xml,ini}

4. 都找不到 → ask_questions 让用户提供路径或标记为无配置
```

**配置格式分支**:

#### XML 配置（平台默认）

| 配置文件（相对于 config 目录） | 解析目标 | XML 节点 |
|------|------|------|
| `[后端配置文件]` | FE→BE 操作路由 + Operation 链 | `<Operation type="...">` |
| `BE/WorkflowController.xml` | Controller 级操作链 + 线程模型 | `<Operation type="...">`, `<ThreadModel>` |
| `[前端命令配置]` | BE→FE 消息路由 | `<OperationItem Key="..." MapToClassName="...">` |
| `[前端配置文件]` | Cell 初始化链 | `<Cell>` → `<InitializeItem>` |
| `FE/EventHandler.xml` | 系统事件→处理器映射 | `<EventHandlerItem>` |
| `[前端容器配置]` | Unity IoC 容器注册 | `<register>` |

#### YAML/JSON 配置

| 配置模式 | 解析目标 | 关键字段 |
|---------|---------|----------|
| 路由/端点配置 | 模块间路由映射 | `routes`, `endpoints`, `handlers` |
| 服务注册 | 依赖注入/服务发现 | `services`, `providers`, `plugins` |
| 权限/角色 | 功能权限映射 | `permissions`, `roles`, `features` |

#### 无配置文件

标记本段为 `🔧 待人工补充` 或直接删除。

**找不到时的 fallback 对话框**：

```
工具: ask_questions
参数:
  questions:
    - header: "ConfigPath"
      question: "未自动发现配置文件。请提供配置目录路径，或选择跳过。"
      allowFreeformInput: true
      options:
        - label: "暂时跳过"
          description: "配置映射段落将保留为人工补充占位符"
```

### 层间路由映射

> 🤖 **自动提取**: 根据配置格式从对应文件中提取层间通信路由。
> - XML: 读取 [项目配置文件] 的 `<Operation>` 节点
> - YAML/JSON: 读取路由配置的 `routes`/`handlers` 字段
> 提取后人工校验。

| 源层操作标识 | 目标层处理链 | 说明 | 状态 |
|-------------|-------------|------|:----:|
| `"{OperateType}"` | `Handler1 \| Handler2 \| ...` | {触发场景} | 🤖/✅ |

### 反向消息路由

> 🤖 **自动提取**: 从配置文件中提取反向通知/回调路由。
> - XML (平台): `[前端命令配置]` 的 `<OperationItem>` 节点
> - YAML/JSON: 事件/消息订阅配置
> 提取后人工校验。

| 源层通知 Key | 目标层处理类 | 说明 | 状态 |
|-------------|-------------|------|:----:|
| `"{NotifyKey}"` | `HandlerClassName` | {什么时候触发、收到后做什么} | 🤖/✅ |

### 处理链详情（可选）

> 🤖 **自动提取**: 核心场景的完整处理链。
> 提取后人工校验：确认执行顺序与实际运行时一致。

```
{场景名}: Step1 → Step2 → Step3 → ... → StepN   [🤖/✅]
```

### 线程与并发约束（🔧 需人工补充）

> 无相关约束则删除此段。

- ⚡ **线程类型**: {🤖 可从配置提取 或 🔧 人工补充}
- 🔒 **锁约束**: {🔧 人工补充: 是否涉及锁？获取顺序？}
- ⏳ **异步操作**: {🔧 人工补充: 哪些操作异步执行？完成后如何通知？}

### 算法/特殊处理约定（🔧 需人工补充）

> 仅当本模块涉及算法/特殊处理管线时填写，否则删除

- 📥 **输入要求**: {需要什么格式的输入？资源要求？}
- 📤 **输出格式**: {返回什么？存储到哪里？}
- 🔄 **管线位置**: {在处理管线中的位置和依赖}

## 上下游依赖

| 方向 | 模块 | 关系 |
|------|------|------|
| ⬆️ 上游 | `#{{PLATFORM_PREFIX}}-{xxx}-expert` | {本模块需要它的什么} |
| ⬇️ 下游 | `#{{PLATFORM_PREFIX}}-{yyy}-expert` | {它用本模块的什么} |
~~~

---

## 禁止写入的内容

> 以下内容经实证验证对 Copilot 代码生成**有害或无效**

| 禁止项 | 原因 | 验证依据 |
|--------|------|---------|
| **伪代码/示例代码块** | Copilot 会按伪代码生成调用，编译失败。验证发现 app-* Skill 中 76% 的代码示例符号（13/17）在代码库中不存在 | layout-expert `ViewFactory` / `RestoreItemDisplay` / `MsgChangeView` 全不存在；registration-expert 5/5 符号不存在 |

| **Q&A 常见问题** | 内容可归入"常见陷阱"表，Q&A 散文形式检索效率低 | 10/10 app-* 恰好 3 个 Q&A，高度模式化 |
| **设计理念散文** | Copilot 不需要理解"为什么这样设计"，只需知道"接口叫什么、在哪里" | app-* 每个含 3-5 段设计说明，扩大 token 消耗但不影响检索 |
| **未经验证的名称** | 写错比不写更危险。大小写也算错（`Voi` ≠ `VOI`、`Lut` ≠ `LUT`） | {{PLATFORM_REPO}}-tissue-expert `IGenerateVoiApplyToScene` 实际为 `IGenerateVOIApplyToScene` |

---

## Copilot 盲区分析（模板设计依据）

> 以下信息经调研确认 Copilot **无法或极难从代码中自动获得**，因此模板专门设计了"🔧 需人工补充"段落。

### 为什么 XML 配置映射是最大盲区？

本项目 FE↔BE 通信走字符串路由，运行时行为完全由 XML 配置驱动：

```
FE OperateType 字符串 → [[项目配置文件]] → BE C++ Operation 类链（| 分隔多个按序执行）
BE 通知 Key 字符串 → [CommandHanlder.xml] → FE C# Operation 类
```

**Copilot 搜代码只能看到两端**（FE 发送字符串、BE 类的实现），但**中间的 XML 映射完全不可见**。
例如 FE 发送 `"ChangeLayout"`，Copilot 无法知道 BE 端实际执行的是 7 个 Operation 的链式调用。

### 核心配置文件清单

| 配置文件 | 驱动什么行为 | Copilot 可发现性 |
|---------|------------|:-:|
| `appdata/{appname}/config/[后端配置文件]` | FE→BE 操作路由 + Widget/Model 注册 + Operation 链 | ⚠️ 可自动解析（需仓库路径） |
| `appdata/{appname}/config/BE/WorkflowController.xml` | Controller 级操作链 + 线程模型 + 预处理管线 | ⚠️ 可自动解析（需仓库路径） |
| `appdata/{appname}/config/[前端命令配置]` | BE→FE 消息路由 | ⚠️ 可自动解析（需仓库路径） |
| `appdata/{appname}/config/[前端配置文件]` | Cell 初始化链 | ⚠️ 可自动解析（需仓库路径） |
| `appdata/{appname}/config/FE/EventHandler.xml` | 系统事件→处理器映射 | ⚠️ 可自动解析（需仓库路径） |
| `appdata/{appname}/config/[前端容器配置]` | Unity IoC 容器注册 | ⚠️ 可自动解析（需仓库路径） |

> 📌 **路径规律**: 标准结构为 `appdata/{appname}/config/`，部分项目采用 `BE/appdata/{appname}/config/` + `FE/appdata/{appname}/config/` 分仓结构。
> Copilot 在生成 Skill 时应通过 `list_dir` / `file_search` 自动探测，找不到时用 `ask_questions` 对话框让用户提供。

### 其他盲区

| 信息类型 | 为什么搜不到 | 示例 |
|---------|------------|------|
| **线程模型** | `gpuid="-2"` 等配置语义在代码中无注释 | StreamingThread 约定 |
| **锁获取顺序** | 多把 mutex 的获取规则是隐性约定 | CPU/GPU 双 mutex |
| **异步操作清单** | 哪些 Operation 走 `IAsyncProc` 需逐文件追踪 | 自动分割、RefVOI 计算 |
| **算法输入约定** | 算法要什么格式/分辨率的输入是领域知识 | GPU 内存要求、Volume 格式 |
| **预处理阶段位置** | 8 阶段管线定义在代码中但阶段间依赖是隐性的 | SegmentOrgan 依赖 LabelingBone |

---

## 撰写指南

### 什么信息对 Copilot 检索真正有用？

| 有用的信息 | 没用的信息 |
|-----------|-----------|
| 真实的接口名 + 真实的文件路径 | 编造的理想化接口签名或示例代码 |
| grep 搜什么关键词能找到代码 | 重复代码中已有的 XML 注释 |
| "不要搜X，搜Y" 的名称纠正 | 可以通过 read_file 获得的完整签名 |
| 模块间的隐性依赖关系 | 显而易见的单模块内逻辑 |
| 业务约束和禁止事项 | 通用的编程最佳实践 |
| 5-8 行领域术语表 | 大段设计理念/架构哲学散文 |
| 真实调用语句（从源码复制） | 编写的演示代码（伪造的类名和方法） || **XML 配置中的运行时映射** | 代码中已有清晰注释的逻辑 |
| **线程/锁/异步约束** | 可从 lock/mutex 语句直接推断的简单场景 |
| **算法输入输出约定** | 算法内部实现细节 |
### 验证步骤（必做）

1. grep 每个接口/类名 → 确认在代码中真实存在
2. **大小写精确匹配** → `VOI` 不能写成 `Voi`，`LUT` 不能写成 `Lut`
3. 确认命名空间 → 查看 .csproj 文件名或 namespace 声明
4. 确认文件路径 → list_dir 验证文件存在
5. **文件名 vs 类名交叉验证** → 文件名和内部类名可能不一致（如 `{{APP_PREFIX}}LayoutHelper.cs` 内部类名实为 `LayoutUtilityAssist`）
6. 删除不确定的 → 宁可少写也不写没验证过的名称
7. 如写"调用模式"代码 → 必须标注源文件路径和行号，确认可 grep 到

### 段落取舍决策树

```
写 Skill 时对每个段落问自己：

Q1: Copilot 能通过 grep/read_file 搜到这个信息吗？
  → 能搜到 → 不写（除非名字容易搜错，那写陷阱表）
  → 搜不到 → Q2

Q2: 这个信息会影响 Copilot 生成代码的正确性吗？
  → 会 → 必须写（接口名对照、命名空间、约束）
  → 不会 → 不写（设计理念、架构哲学）

Q3: 这个信息存在于 XML 配置而非代码中吗？
  → 是 → Q4
  → 否 → 回到 Q1

Q4: 该 XML 配置文件能否在项目仓库中自动定位？
  → 能（在 appdata/{appname}/config/ 下）→ 自动 read_file 解析并填入，标注 🤖
  → 不能 → ask_questions 让用户提供路径，仍无法获取则标注 🔧 待人工补充
```

---

## 各段落体积参考

| 段落 | 建议行数 | 必选/可选 | 说明 |
|------|---------|----------|------|
| YAML frontmatter | 5-8 | 必选 | 触发词要全 |
| 执行声明规范 | 15-20 | 必选 | 固定格式，替换模块名和前缀 |
| 模块元信息 | 5-7 | 必选 | 表格，固定格式 |
| 核心概念 | 5-8 | **必选** | 术语表，不写散文 |
| 搜索策略 | 3-5 | 必选 | 本地优先 + MCP |
| 代码入口 | 15-40 | 必选 | 全部从源码验证 |
| 核心流程 | 2-8 | 可选 | 仅复杂流程时写 |
| 场景入口速查 | 5-15 | **必选** | 三列映射表 |
| 调用模式 | 3-10 | 可选 | 仅不直观调用时写，必须源码复制 |
| 常见陷阱 | 5-15 | **必选** | 防幻觉核心 |
| 运行时配置映射 | 10-30 | **按需必选** | 🤖 自动解析 + 🔧 人工校验 |
| 上下游依赖 | 3-8 | 必选 | 方向表 |
| Bug 模式指针 | 1 | **必选** | `📖 历史 Bug 模式分析见 references/bug-patterns.md` |
| 经验笔记指针 | 1 | **必选** | `📖 团队经验笔记见 references/experience-notes.md` |
| **总计** | **80-150** | — | 比 平台-*(~78) 稍长，比 app-*(~280) 大幅精简 |

### ⚠️ 内容完整性红线（强制）

> 此规则优先级高于行数限制。

1. **模板格式不可简化** — 执行声明规范（含 `**每次使用本 Skill 时...**` + 开始/完成代码块）、必填章节等固定格式必须完整保留，禁止压缩或省略
2. **必要内容不可删减** — 场景入口条目、陷阱表条目、依赖行、配置映射条目等经验证的内容，不得为了满足行数限制而删除或合并
3. **超限时拆分到 reference** — 若行数超出上限（应用层 ≤120 / 平台层 ≤150），将较大的独立章节（如运行时配置映射、大型表格）拆分到 `references/` 目录下的 `.md` 文件中
4. **SKILL.md 中保留指针** — 拆分后在原位置写: `📖 详细内容见 \`references/xxx.md\``
5. **reference 文件命名** — 使用语义化名称如 `config-mapping.md`、`viewmodel-list.md`
6. **🔒 共创文件不可覆盖** — `references/experience-notes.md`（团队手动编写）和 `references/bug-patterns.md`（LLM 生成）为共创内容，重新生成 SKILL.md 时**严禁删除或覆盖**这两个文件

---

## 平台约定参考

> 以下为不同平台的约定示例。生成新项目 Skill 时，从 `project-profile.json` 读取平台信息。

### {{PLATFORM_REPO}} 约定（平台生态默认）

| 约定 | 说明 |
|------|------|
| FE 命名空间 | `{{PLATFORM_NAMESPACE}}.Component.<模块名>` |
| BE 命名空间 | 多数在 `{{PLATFORM_NS}}::AppCommonLib` 或 `{{PLATFORM_NS}}::AppFramework` |
| BE 文件前缀 | 全部 `{{platform_be_prefix}}_` 开头 |
| 接口头文件 | `{{platform_be_prefix}}_*_interface.h` 或 `{{platform_be_prefix}}_*_assist_interface.h` |
| `_assist_interface` | 应用层需要实现的回调/策略接口 |
| FE 项目结构 | `CellInit/` → `UserControls/` → `ViewModels/` → `MMCommon/` |
| `MMCommon/` | 每个模块都有，是 MM 应用的特化实现 |
| `CommonInterface` | 跨模块共享接口的定义中心，按子目录分模块 |
| `Defines` | BE 全局枚举和常量的集中定义模块 |
| `Protocol` | protobuf 协议定义，FE↔BE 通信 |

### 自定义平台约定模板

> 新项目接入时，ProjectSetup Agent 会引导收集以下信息并填入此处。

| 约定 | 说明 |
|------|------|
| {layer_1} 命名空间 | `{namespace_pattern_1}` |
| {layer_2} 命名空间 | `{namespace_pattern_2}` |
| 文件命名规则 | `{file_naming_convention}` |
| 接口文件模式 | `{interface_file_pattern}` |
| 共享接口目录 | `{shared_interface_dir}` |
| 项目结构 | `{directory_conventions}` |

---

## 附录：两类现有 Skill 问题清单（供重构参考）

### app-* Skill 需修复项

| 优先级 | 问题 | 影响 |
|--------|------|------|
| **P0** | 全部缺少"常见陷阱"表（10/10 缺失） | Copilot 频繁编造不存在的接口名 |
| **P0** | 代码块示例含大量伪造符号（验证 76% 不存在） | Copilot 按伪代码生成调用 → 编译失败 |
| **P1** | 缺少"场景入口速查"三列表（10/10 缺失） | Copilot 难以快速定位入口文件 |
| **P1** | "执行声明规范"重复模板占 ~20 行（10/10 相同） | 浪费 token |
| **P2** | 部分接口表中文件名与真实类名不一致未标注 | 如 `{{APP_PREFIX}}LayoutHelper.cs` 内部类名为 `LayoutUtilityAssist` |

### 平台-* Skill 需修复项

| 优先级 | 问题 | 影响 |
|--------|------|------|
| **P1** | 大小写不精确（`Voi`→`VOI`、`Lut`→`LUT`） | Copilot 生成错误大小写的引用 |
| **P2** | 缺少领域术语表 | 对不熟悉领域的开发者上下文不足 |
