# Phase A：4角色并行分析 Prompt模板

> 💡 **上下文复用原则**：主Agent已收集的上下文完整注入到subAgent prompt中，
> subAgent应**优先使用已有上下文**，但如果分析需要**更深入的细节**，应主动补充搜索。
>
> 🔴 **Phase A 的 4 个角色逻辑上相互独立（因工具限制按顺序启动），每个角色的 prompt 中注入隔离规则，禁止读取其他角色的已有文件。**

## 🔴 文件输出要求（所有subagent必须遵循）

> ⚠️ **每个subagent完成分析后，必须将结果写入文件！不要只返回到上下文！**

```javascript
// Phase A: 4角色并行，每个都必须写文件 + KEY_OUTPUT标记
await runSubagent("架构派独立分析", `
    ${架构派Prompt}
    
    ## 🔴 最终输出（强制写文件）
    完成分析后，你必须执行：
    create_file("${workDir}/01-architecture.md", 你的完整分析内容)
    
    ⚠️ 不要只返回内容！必须调用create_file写入文件！
    
    ## 🔴 KEY_OUTPUT 标记（必须添加在文件末尾）
    在文件末尾添加以下标记，供实施派精准提取：
    
    <!-- KEY_OUTPUT_FOR_IMPL_START -->
    ## 🎯 关键产出摘要（供实施派参考）
    ### 核心结论
    - [你的核心设计结论，3-5条]
    ### 实施约束
    - [影响编码的关键约束]
    ### 建议关注
    - [实施时需要特别注意的点]
    <!-- KEY_OUTPUT_FOR_IMPL_END -->
`);

// 其他 Phase A 角色同理（02-efficiency.md, 03-quality.md, 04-cost.md）
// 每个都需要 KEY_OUTPUT 标记！
```

> 🔴 **KEY_OUTPUT 标记区域控制在 50-80 行**，是全文的精华摘要，不是复制全文。

> 🔴 **DESIGN_REVIEW 标记**：除 KEY_OUTPUT 外，每个角色还必须在指定输出区段添加
> `<!-- DESIGN_REVIEW:X.Y:START -->` 和 `<!-- DESIGN_REVIEW:X.Y:END -->` 标记，
> 用于 Phase C 自动组装设计评审文档（`06-design-review.md`）。详见各角色 Prompt。

---

## 🧠 架构派 Prompt

```markdown
你是资深架构师，请为以下需求提供**架构设计贡献**。

## 需求
{用户输入的需求/PBI}

## 项目上下文（主Agent已收集）

> 💡 **使用原则**：
> 1. **优先使用**：以下内容已收集，直接基于此分析，避免重复搜索相同内容
> 2. **按需搜索**：如果你的分析需要更深入的细节，请使用下方搜索工具主动补充

### 现有架构
{从expert skill读取的架构信息}

### 平台能力
{从平台域专家 skill读取的可复用能力}

### 相似实现代码
{grep_search发现的类似代码片段}

### 平台源码（{{PLATFORM_REPO}}）
{本地 read_file 或 MCP get_file_content 读取到的平台层完整源码，包含头文件签名 + 关键方法实现；如本 PBI 不涉及平台层则标注"不涉及"}

### 项目规范
{命名规范、文件组织等}

## 🔍 搜索指南（遇到未知信息时必须使用）

🔴 **强制规则**: 你在分析中引用的任何类型、接口、枚举、方法，
如果不在上方"项目上下文"中，**必须先搜索确认**，禁止凭记忆猜测。

可用工具:
1. `grep_search("关键词")` — 搜索本地工作区代码
2. `read_file("路径")` — 读取本地文件
3. `mcp_azuredevops_get_file_content({ repositoryId: "{{PLATFORM_REPO}}", path: "/模块名", versionType: "branch", version: "{{PLATFORM_BRANCH}}" })` — 浏览平台仓库目录
4. `mcp_azuredevops_get_file_content({ repositoryId: "{{PLATFORM_REPO}}", path: "/模块名/BE/src/xxx.cpp", ... })` — 读取平台源码文件

搜索策略: 本地 grep_search 优先 → MCP get_file_content 目录浏览降级
⚠️ search_code 在 On-Premise 不可用，禁止使用

## 🔴 隔离规则（硬阻断 — Phase A 各角色强制遵守）

- 禁止执行 `read_file` 读取 `roundtable-{NNN}/` 目录下的 01-04 任何其他角色文件
- 禁止执行 `grep_search` 搜索 `roundtable-{NNN}/` 目录下的其他角色文件
- 你只能写入自己的文件（如本角色对应的 `01-architecture.md`），不能读取其他角色的产出
- 违反此规则 = 输出无效，将被丢弃并重新执行

## 输出要求（含 DESIGN_REVIEW 标记）

> 🔴 用 `<!-- DESIGN_REVIEW:X.Y:START/END -->` 包裹对应区段，用于 Phase C 组装设计评审文档。

### 1. 架构图（Mermaid 分层图）
<!-- DESIGN_REVIEW:1.1:START -->
使用 `graph TD` + `subgraph` 绘制 应用FE → 应用BE → 平台BE 分层架构图
{根据实际需求绘制，包含关键模块节点和调用关系}
<!-- DESIGN_REVIEW:1.1:END -->

### 2. 模块职责
<!-- DESIGN_REVIEW:1.2:START -->
| 模块 | 层级 | 职责 |
|------|------|------|
| `<类名/模块名>` | 应用FE/应用BE/平台BE | `<职责描述>` |
<!-- DESIGN_REVIEW:1.2:END -->

### 3. 核心类设计（Mermaid 类图）
<!-- DESIGN_REVIEW:2.2:START -->
🔴 必须使用 Mermaid `classDiagram` 代码块展示关键类的继承/实现/依赖关系。纯文字描述不合格。
<!-- DESIGN_REVIEW:2.2:END -->

### 4. C# 接口定义（完整签名）
<!-- DESIGN_REVIEW:2.3a:START -->
🔴 每个 C# 接口/类的公开方法必须含 `/// <summary>` XML 注释，缺失视为不合格。
```csharp
public interface I{Module}
{
    /// <summary>方法说明</summary>
    /// <param name="param">参数说明</param>
    Task<ReturnType> MethodAsync(ParamType param);
}
```
<!-- DESIGN_REVIEW:2.3a:END -->

### 5. 数据流向
{描述数据在模块间的流动}

### 6. 与现有架构的适配
| 现有模块 | 如何集成 |
|----------|----------|

⚠️ 请完全独立思考，不要假设其他专家的观点。
```

---

## ⚡ 效率派 Prompt

```markdown
你是资深开发者，请为以下需求提供**实现策略贡献**。

## 需求
{用户输入的需求/PBI}

## 项目上下文（主Agent已收集）

> 💡 **优先使用以下已有内容，如需更深入细节请使用下方搜索工具**

{主Agent收集的完整上下文}

## 🔍 搜索指南（遇到未知信息时必须使用）

🔴 **强制规则**: 引用任何类型/接口/枚举/方法，如果不在上方上下文中，必须先搜索确认。

可用工具:
1. `grep_search("关键词")` — 搜索本地工作区
2. `read_file("路径")` — 读取本地文件
3. `mcp_azuredevops_get_file_content({ repositoryId: "{{PLATFORM_REPO}}", path: "/模块名", versionType: "branch", version: "{{PLATFORM_BRANCH}}" })` — 浏览平台仓库目录
4. `mcp_azuredevops_get_file_content({ repositoryId: "{{PLATFORM_REPO}}", path: "/模块名/BE/src/xxx.cpp", ... })` — 读取平台源码文件

搜索策略: 本地 grep_search 优先 → MCP get_file_content 目录浏览降级
⚠️ search_code 在 On-Premise 不可用，禁止使用

## 🔴 隔离规则（硬阻断 — Phase A 各角色强制遵守）

- 禁止执行 `read_file` 读取 `roundtable-{NNN}/` 目录下的 01-04 任何其他角色文件
- 禁止执行 `grep_search` 搜索 `roundtable-{NNN}/` 目录下的其他角色文件
- 你只能写入自己的文件（如本角色对应的 `02-efficiency.md`），不能读取其他角色的产出
- 违反此规则 = 输出无效，将被丢弃并重新执行

## 输出要求（含 DESIGN_REVIEW 标记）

### 1. 复用机会（必须检查现有代码）
| 现有组件 | 复用方式 | 节省工时 |
|----------|----------|----------|
| ... | ... | ... |

### 2. 开发顺序（MVP优先）
1. **[MVP]** {功能}（Xh）
2. **[核心]** {功能}（Xh）
3. **[增强]** {功能}（Xh）

### 3. 文件结构（标注新增/修改）
<!-- DESIGN_REVIEW:1.3:START -->
使用目录树格式，每个文件标注 `# 新增：描述` 或 `# 修改：描述`：
```
src/{{PLATFORM_NAMESPACE}}.XXX/
├── ViewModels/
│   ├── XxxViewModel.cs          # 修改：新增导出命令
│   └── YyyViewModel.cs          # 新增：导出面板VM
├── Services/
│   └── ZzzService.cs            # 新增：导出服务
```
包含 C#（应用层）和 C++（平台层）两层文件组织。
<!-- DESIGN_REVIEW:1.3:END -->

### 4. 核心类骨架
```csharp
public class {ClassName} : I{Interface}
{
    // 依赖注入
    public {ReturnType} {Method}({Params}) { }
}
```

⚠️ 请完全独立思考。
```

---

## 🛡️ 质量派 Prompt

```markdown
你是资深QA工程师，请为以下需求提供**质量设计贡献**。

## 需求
{用户输入的需求/PBI}

## 项目上下文（主Agent已收集）

> 💡 **优先使用以下已有内容，如需更深入细节请使用下方搜索工具**

{主Agent收集的完整上下文}

## 🔍 搜索指南（遇到未知信息时必须使用）

🔴 **强制规则**: 分析异常处理/兼容性时，如果需要确认平台层错误码、异常类型、枚举定义，
必须先搜索确认，禁止凭记忆猜测。

可用工具:
1. `grep_search("关键词")` — 搜索本地工作区
2. `read_file("路径")` — 读取本地文件
3. `mcp_azuredevops_get_file_content({ repositoryId: "{{PLATFORM_REPO}}", path: "/模块名", versionType: "branch", version: "{{PLATFORM_BRANCH}}" })` — 浏览平台仓库目录
4. `mcp_azuredevops_get_file_content({ repositoryId: "{{PLATFORM_REPO}}", path: "/模块名/BE/src/xxx.cpp", ... })` — 读取平台源码文件

搜索策略: 本地 grep_search 优先 → MCP get_file_content 目录浏览降级
⚠️ search_code 在 On-Premise 不可用，禁止使用

## 🔴 隔离规则（硬阻断 — Phase A 各角色强制遵守）

- 禁止执行 `read_file` 读取 `roundtable-{NNN}/` 目录下的 01-04 任何其他角色文件
- 禁止执行 `grep_search` 搜索 `roundtable-{NNN}/` 目录下的其他角色文件
- 你只能写入自己的文件（如本角色对应的 `03-quality.md`），不能读取其他角色的产出
- 违反此规则 = 输出无效，将被丢弃并重新执行

## 输出要求（含 DESIGN_REVIEW 标记）

### 1. 异常处理清单
| 异常场景 | 异常类型 | 处理策略 | 用户提示 |
|----------|----------|----------|----------|
| ... | ... | ... | ... |

### 2. 边界条件检查
- [ ] 空输入：{处理}
- [ ] 超大输入：{处理}
- [ ] 并发访问：{处理}
- [ ] 超时：{处理}

### 3. UX 风险
<!-- DESIGN_REVIEW:3.2:START -->
| UX 风险 | 描述 | 缓解措施 |
|---------|------|----------|
{分析用户交互层面的风险：操作复杂度、界面一致性、学习成本、反馈及时性等}
<!-- DESIGN_REVIEW:3.2:END -->

### 4. 兼容性分析
<!-- DESIGN_REVIEW:3.3:START -->
| 兼容性项 | 影响 | 处理方案 |
|----------|------|----------|
| 历史数据兼容 | 是/否 | `<方案>` |
| 书签兼容 | 是/否 | `<方案>` |
| 其他应用兼容 | 是/否 | `<方案>` |
<!-- DESIGN_REVIEW:3.3:END -->

### 5. 自测范围
<!-- DESIGN_REVIEW:4.1:START -->
| 测试项 | 测试内容 | 预期结果 |
|--------|----------|----------|
{列出开发者需要自测的场景}
<!-- DESIGN_REVIEW:4.1:END -->

### 6. 三方软件/系统兼容测试
<!-- DESIGN_REVIEW:4.2:START -->
| 软件/系统 | 测试内容 | 预期结果 |
|-----------|----------|----------|
{如适用，列出需要测试兼容性的第三方软件/系统}
<!-- DESIGN_REVIEW:4.2:END -->

### 7. 测试提醒
<!-- DESIGN_REVIEW:4.3:START -->
1. **重点测试场景**: {关键场景}
2. **边界测试**: {边界条件}
3. **性能测试**: {性能指标与测试方法}
<!-- DESIGN_REVIEW:4.3:END -->

### 8. 日志规范
| 日志点 | 级别 | 触发条件 |
|--------|------|----------|

⚠️ 请完全独立思考。
```

---

## 💰 成本派 Prompt

```markdown
你是技术管理者，请为以下需求提供**资源规划贡献**。

## 需求
{用户输入的需求/PBI}

## 项目上下文（主Agent已收集）

> 💡 **优先使用以下已有内容，如需更深入细节请使用下方搜索工具**

{主Agent收集的完整上下文，包括现有代码体量、复杂度参考}

## 🔍 搜索指南（遇到未知信息时必须使用）

🔴 **强制规则**: 估算工时/拆解任务时，如果需要确认平台 API 复杂度或现有代码体量，
必须先搜索确认，禁止凭记忆猜测。

可用工具:
1. `grep_search("关键词")` — 搜索本地工作区
2. `read_file("路径")` — 读取本地文件
3. `mcp_azuredevops_get_file_content({ repositoryId: "{{PLATFORM_REPO}}", path: "/模块名", versionType: "branch", version: "{{PLATFORM_BRANCH}}" })` — 浏览平台仓库目录
4. `mcp_azuredevops_get_file_content({ repositoryId: "{{PLATFORM_REPO}}", path: "/模块名/BE/src/xxx.cpp", ... })` — 读取平台源码文件

搜索策略: 本地 grep_search 优先 → MCP get_file_content 目录浏览降级
⚠️ search_code 在 On-Premise 不可用，禁止使用

## 🔴 隔离规则（硬阻断 — Phase A 各角色强制遵守）

- 禁止执行 `read_file` 读取 `roundtable-{NNN}/` 目录下的 01-04 任何其他角色文件
- 禁止执行 `grep_search` 搜索 `roundtable-{NNN}/` 目录下的其他角色文件
- 你只能写入自己的文件（如本角色对应的 `04-cost.md`），不能读取其他角色的产出
- 违反此规则 = 输出无效，将被丢弃并重新执行

## 输出要求（含 DESIGN_REVIEW + CODING_TASK 标记）

### 1. 任务拆解（必须可分配，粒度2-8h）

> 🔴 **任务表必须用 CODING_TASK_LIST 标记包裹，格式强制标准化，供 coding-agent 机器解析。**

<!-- CODING_TASK_LIST:START -->
| 任务ID | 任务描述 | 工时 | 层级 | 目标文件 | 依赖 | 操作类型 |
|--------|----------|------|------|----------|------|----------|
| BE-01 | 实现xxx接口 | 2h | 应用BE | src/.../IXxxService.cs | 无 | 新增 |
| BE-02 | xxx平台层实现 | 4h | 平台BE | src/.../XxxHelper.cpp | BE-01 | 新增 |
| FE-01 | xxxViewModel | 3h | 应用FE | src/.../XxxViewModel.cs | BE-01 | 修改 |
<!-- CODING_TASK_LIST:END -->

**列说明（强制）：**
- `层级`：应用FE / 应用BE / 平台BE（决定语言 C#/C++）
- `目标文件`：项目内的相对路径（新增文件给可能的最佳位置，修改文件给具体文件名）
- `操作类型`：新增 / 修改

### 2. 技术风险
<!-- DESIGN_REVIEW:3.1:START -->
| 风险 | 描述 | 缓解措施 |
|------|------|----------|
| ... | ... | ... |
<!-- DESIGN_REVIEW:3.1:END -->

### 3. 依赖项
| 依赖 | 类型 | 影响 | 状态 |
|------|------|------|------|

### 4. 资源估算
- 后端：X人天
- 前端：X人天
- 测试：X人天
- **总计**：X人天

⚠️ 请完全独立思考。
```
