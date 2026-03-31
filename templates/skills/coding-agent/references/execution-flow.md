# Coding Agent 详细执行流程

> 本文件包含 Step 0-3 的完整伪代码实现，供主 Agent 参考执行。
> 核心原则：**串行逐任务、精准提取、不确定即暂停**。

---

## Step 0：发现与加载设计文档

### 0.1 扫描圆桌会议工作目录

```javascript
async function discoverDesignDocs(projectRoot) {
    const tempDir = `${projectRoot}/.copilot-temp`;
    
    // 1. 检查 .copilot-temp 是否存在
    if (!exists(tempDir)) {
        // ❌ 提示用户先运行圆桌会议生成设计文档
        return null;
    }
    
    // 2. 扫描所有 roundtable-* 目录
    const roundtables = list_dir(tempDir)
        .filter(d => d.startsWith("roundtable-"))
        .sort()
        .reverse(); // 最新的在前
    
    if (roundtables.length === 0) {
        // ❌ 没有圆桌会议产出
        return null;
    }
    
    // 3. 多个 → 让用户选择
    let workDir;
    if (roundtables.length > 1) {
        // 展示列表，标注最新的为推荐
        // 用户选择后设置 workDir
    } else {
        workDir = `${tempDir}/${roundtables[0]}`;
    }
    
    return workDir;
}
```

### 0.2 验证核心文件 + 加载主上下文

```javascript
async function loadDesignContext(workDir) {
    // 1. 验证必需文件
    const required = {
        "04-cost.md": "任务拆解表（CODING_TASK_LIST）",
        "05-implementation.md": "实现骨架（CODING_IMPL）"
    };
    for (const [file, purpose] of Object.entries(required)) {
        if (!exists(`${workDir}/${file}`)) {
            // ❌ 缺失：{file}（{purpose}），提示用户
            return null;
        }
    }
    
    // 2. 读取 05-implementation.md 全文（核心上下文）
    const implContent = read_file(`${workDir}/05-implementation.md`);
    
    // 3. 可选：检查 01-03 是否存在（按需提取）
    const optional = ["01-architecture.md", "02-efficiency.md", "03-quality.md"];
    const available = {};
    for (const file of optional) {
        available[file] = exists(`${workDir}/${file}`);
    }
    
    return { implContent, available };
}
```

---

## Step 1：解析任务表 + 拓扑排序

### 1.1 提取 CODING_TASK_LIST

```javascript
async function parseTaskList(workDir) {
    // 1. grep 定位标记
    const startMatch = grep_search("CODING_TASK_LIST:START", {
        includePattern: `${workDir}/04-cost.md`
    });
    const endMatch = grep_search("CODING_TASK_LIST:END", {
        includePattern: `${workDir}/04-cost.md`
    });
    
    if (!startMatch || !endMatch) {
        // ⚠️ 降级处理：尝试读取整个 04-cost.md 寻找任务表
        // 搜索 "| 任务ID |" 开头的表格
        const fallback = grep_search("\\| 任务ID", {
            includePattern: `${workDir}/04-cost.md`,
            isRegexp: true
        });
        // 从该行开始读取直到表格结束
    }
    
    // 2. 读取标记之间的内容
    const tableContent = read_file(`${workDir}/04-cost.md`, 
                                    startMatch.line + 1, endMatch.line - 1);
    
    // 3. 解析 Markdown 表格
    const tasks = parseMarkdownTable(tableContent);
    // 每行 → { id, desc, hours, layer, targetFile, depends, operation }
    
    return tasks;
}
```

### 1.2 拓扑排序

```javascript
function topologicalSort(tasks) {
    // 构建依赖图
    const graph = {};
    const inDegree = {};
    
    for (const task of tasks) {
        graph[task.id] = [];
        inDegree[task.id] = 0;
    }
    
    for (const task of tasks) {
        if (task.depends && task.depends !== "无" && task.depends !== "-") {
            // 依赖可能是逗号分隔的多个ID
            const deps = task.depends.split(/[,，]/).map(d => d.trim());
            for (const dep of deps) {
                if (graph[dep]) {
                    graph[dep].push(task.id);
                    inDegree[task.id]++;
                }
            }
        }
    }
    
    // BFS 拓扑排序
    const queue = Object.keys(inDegree).filter(id => inDegree[id] === 0);
    const order = [];
    
    while (queue.length > 0) {
        const current = queue.shift();
        order.push(current);
        for (const next of graph[current]) {
            inDegree[next]--;
            if (inDegree[next] === 0) {
                queue.push(next);
            }
        }
    }
    
    // 检查是否有环
    if (order.length !== tasks.length) {
        // ⚠️ 依赖存在循环，展示给用户处理
    }
    
    return order;
}
```

### 1.3 展示执行计划（等待用户确认）

```markdown
📋 **编码执行计划**（共 X 个任务）

| 序号 | 任务ID | 描述 | 层级 | 操作 | 目标文件 | 依赖 |
|------|--------|------|------|------|----------|------|
| 1 | BE-01 | ... | 应用BE | 新增 | src/... | - |
| 2 | BE-02 | ... | 平台BE | 新增 | src/... | BE-01 |
| 3 | FE-01 | ... | 应用FE | 修改 | src/... | BE-01 |

⏱️ 预计总工时: Xh
📁 涉及文件: Y 个（新增 A + 修改 B）

> 确认后开始编码，或告诉我需要调整的内容。
```

---

## Step 2：逐任务编码（核心循环）

### 2a. 精准上下文收集

> ⚠️ **以下6个步骤全部为必须执行的指令，不是示例代码！**
>
> 每个步骤的具体含义：
> 1. 精准提取该任务的实现骨架（`CODING_IMPL:{taskId}` 标记区段）
> 2. 按需提取接口定义（C# → `DESIGN_REVIEW:2.3a`，C++ → `DESIGN_REVIEW:2.3b`）
> 3. 修改任务 → 读取目标文件现有代码
> 4. 提取质量/自测要求（`DESIGN_REVIEW:4.1`）
> 5. 读取相关 expert skill
> 6. 🔴 **搜索平台层源码（涉及平台组件时强制执行）** — 见下方自然语言说明

### 🔴 步骤6 详细说明：搜索平台层源码

**触发条件**：任务层级含"平台"，或任务描述含 `DataLoad/DataSave/ROI/VOI/TissueControl/MaskData/Volume` 等平台关键词。

**6a. 从平台域专家 skill 提取搜索关键词**：
- 从步骤 5 读取的 {{PLATFORM_PREFIX}}-{领域}-expert skill 中，提取「核心接口速查」表中的接口名/类名（如 `[你的平台接口名]`、`[你的平台接口名]`）
- 提取「关键数据类型」中的类型名（如 `ExportConfig`、`Structure`）
- 🔴 **不要在应用代码里搜 using/include 来提取类名** — using 只有命名空间，没有类名
- **降级策略**：Tier 1 skill接口速查表 → Tier 2 skill代码搜索建议 → Tier 3 PBI英文关键词

**6b. 读取平台源码**（本地优先 → MCP 降级）：
- 本地：`grep_search("接口名", { includePattern: "**/{{PLATFORM_REPO}}/**" })` → `read_file(命中文件)`
- MCP：`mcp_azuredevops_search_code` → `mcp_azuredevops_get_file_content`

**6c. 验证检查点**：确认至少读取了 **1 个平台源文件**。未读取到则降级重试；全部失败则标注「⚠️ 未获取平台源码」。

将读取到的源码保存为 `context.platformSource`。

### 步骤1-6 伪代码参考

```javascript
async function collectTaskContext(task, workDir, implContent) {
    const context = {};
    
    // 1. 精准提取该任务的实现骨架（CODING_IMPL:{taskId}）
    const implStart = grep_search(`CODING_IMPL:${task.id}:START`, {
        includePattern: `${workDir}/05-implementation.md`
    });
    if (implStart) {
        const implEnd = grep_search(`CODING_IMPL:${task.id}:END`, {
            includePattern: `${workDir}/05-implementation.md`
        });
        context.skeleton = read_file(`${workDir}/05-implementation.md`,
                                     implStart.line, implEnd.line);
    } else {
        // ⚠️ 没有对应的 CODING_IMPL 标记
        // 降级：从05全文中搜索任务描述相关的代码块
        context.skeleton = "未找到专属实现骨架，请基于任务描述和接口定义编码";
    }
    
    // 2. 按需提取接口定义
    const lang = getLanguage(task.layer);
    if (lang === "C#") {
        context.interface = extractMarker(workDir, "01-architecture.md",
                                          "DESIGN_REVIEW:2.3a");
    } else if (lang === "C++") {
        context.cppInterface = extractMarker(workDir, "05-implementation.md",
                                             "DESIGN_REVIEW:2.3b");
    }
    
    // 3. 修改任务 → 读取现有代码
    if (task.operation === "修改") {
        context.existingCode = read_file(task.targetFile);
    }
    
    // 4. 提取异常处理/质量要求
    context.qualityRules = extractMarker(workDir, "03-quality.md",
                                         "DESIGN_REVIEW:4.1"); // 自测范围
    
    // 5. 读取相关 expert skill（可选，提升质量）
    // 根据 task.targetFile 的命名空间判断涉及哪个模块
    const moduleName = inferModule(task.targetFile);
    if (moduleName) {
        const expertPath = `${projectRoot}/.github/skills/${moduleName}-expert/SKILL.md`;
        if (exists(expertPath)) {
            context.expert = read_file(expertPath);
        }
    }
    
    // 6. 🔴 平台层源码（涉及平台组件时必做）
    //    触发：task.layer 含"平台"，或任务描述含平台关键词
    if (task.layer.includes("平台") || involvesPlatformKeywords(task.desc)) {
        // 6a. 从步骤5读取的 平台域专家 Skill 提取搜索关键词
        //     核心接口速查表 → [平台接口名，如 IServiceA, IServiceB] 等
        //     🔴 不要从 using/include 提取——using 只有命名空间，没有类名
        const skillInterfaceNames = extractFromSkill(
            context.expert, "核心接口速查"  // Tier 1
        );
        // 降级: Tier 2 = skill代码搜索建议, Tier 3 = PBI英文关键词
        const searchKeywords = skillInterfaceNames.length > 0
            ? skillInterfaceNames
            : extractFromSkill(context.expert, "代码搜索建议")
              || extractEnglishTerms(task.desc);
        
        const localPlatform = workspace.findFolder("{{PLATFORM_REPO}}");
        if (localPlatform) {
            // ✅ 本地优先：用 skill 提供的接口名 grep → read_file 读完整源码
            for (const name of searchKeywords) {
                const hits = grep_search(name, {
                    includePattern: "**/{{PLATFORM_REPO}}/**"
                });
                context.platformSource += read_file(hits[0].filePath);
            }
        } else {
            // 🔄 MCP 降级：用 skill 提供的接口名 search_code → get_file_content 读完整文件
            for (const name of searchKeywords) {
                const results = mcp_azuredevops_search_code({
                    searchText: name,
                    filters: { Repository: ["{{PLATFORM_REPO}}"] }
                });
                for (const file of results.files.slice(0, 3)) {
                    context.platformSource += mcp_azuredevops_get_file_content({
                        repositoryId: "{{PLATFORM_REPO}}",
                        path: file.path,
                        versionType: "branch", version: "{{PLATFORM_BRANCH}}"
                    });
                }
            }
        }
    }
    
    return context;
}

function getLanguage(layer) {
    if (layer.includes("平台")) return "C++";
    return "C#"; // 应用FE、应用BE 都是 C#
}
```

### 2b. runSubagent 编码

```javascript
async function executeTask(task, context) {
    // 构建 prompt（详见 references/subagent-prompt.md）
    const prompt = buildCodingPrompt(task, context);
    
    // 执行编码
    await runSubagent(`编码 ${task.id}: ${task.desc}`, prompt);
}
```

### 2c. 检查点

```javascript
async function verifyTask(task) {
    // 1. 验证文件已创建/修改
    if (task.operation === "新增" && !exists(task.targetFile)) {
        // ❌ 文件未创建，重试一次
        await runSubagent(`重试 ${task.id}`, retryPrompt);
        if (!exists(task.targetFile)) {
            return { status: "failed", reason: "文件未创建" };
        }
    }
    
    // 2. 检查 HUMAN_CHECK 标记
    const humanChecks = grep_search("HUMAN_CHECK", {
        includePattern: task.targetFile
    });
    
    if (humanChecks && humanChecks.length > 0) {
        // 🔴 暂停：展示需要人工确认的位置
        return {
            status: "needs_review",
            checks: humanChecks.map(m => ({
                line: m.line,
                content: m.text
            }))
        };
    }
    
    return { status: "completed" };
}
```

### 暂停与恢复

当遇到 HUMAN_CHECK 时：

```markdown
⚠️ **任务 {taskId} 需要人工确认**

在 `{targetFile}` 中发现 {N} 处需要确认：

**第 {line} 行:**
```{lang}
// 🔴 HUMAN_CHECK: {原因}
// 例如：不确定坐标系转换算法是用 LPS 还是 RAS
{周围代码上下文}
```

请告诉我：
1. 确认当前实现正确 → 我继续下一个任务
2. 修改建议 → 我更新代码后继续
3. 暂时跳过 → 标记保留，继续下一个任务
```

---

## Step 3：完成报告

```javascript
async function generateReport(tasks, results) {
    const report = [];
    let completed = 0, failed = 0, humanChecks = [];
    const newFiles = [], modifiedFiles = [];
    
    for (const task of tasks) {
        const result = results[task.id];
        if (result.status === "completed") completed++;
        else if (result.status === "failed") failed++;
        
        if (result.checks) {
            humanChecks.push(...result.checks.map(c => ({
                file: task.targetFile,
                ...c
            })));
        }
        
        if (task.operation === "新增") newFiles.push(task.targetFile);
        else modifiedFiles.push(task.targetFile);
    }
    
    // 输出报告（见 SKILL.md 中的报告格式）
}
```

---

## 辅助函数

### extractMarker — 从文件中提取标记区段

```javascript
async function extractMarker(workDir, fileName, markerId) {
    const filePath = `${workDir}/${fileName}`;
    const startMatch = grep_search(`${markerId}:START`, {
        includePattern: filePath
    });
    if (!startMatch) return null;
    
    const endMatch = grep_search(`${markerId}:END`, {
        includePattern: filePath
    });
    if (!endMatch) return null;
    
    return read_file(filePath, startMatch.line + 1, endMatch.line - 1);
}
```

### inferModule — 从文件路径推断模块名

```javascript
function inferModule(filePath) {
    // 从路径中提取模块名
    // 例如: src/{{PLATFORM_NAMESPACE}}.VOIExport/ → "voi"
    //       src/{{PLATFORM_NS_PREFIX}}VOI/ → "voi"
    const patterns = [
        /{{PLATFORM_NAMESPACE}}\.(.+)/,
        /{{PLATFORM_NS_PREFIX}}(\w+)/,
        /\/(\w+)Module\//
    ];
    for (const pat of patterns) {
        const match = filePath.match(pat);
        if (match) return match[1].toLowerCase();
    }
    return null;
}
```
