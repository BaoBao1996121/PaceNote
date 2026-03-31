# Bug 诊断执行流程

> 本文件由 `bug-diagnosis-expert` Skill 按需加载，包含两种模式的详细执行步骤。
> 💡 **完整的交互式引导流程**（环境检测 → 配置补全 → 数据采集 → 分析）请使用：
> `@GuidedDev` → 选择"🐛 Bug 修复/分析" → "🔍 分析历史 Bug"

---

## 模式 A：生成/更新 Bug 模式库

### 概览

```
  [数据已在 data/bug_analysis/ 中]
            ↓
  #bug-diagnosis-expert 模式A
            ↓
  读取 JSON → 读取关键 Diff → AI 分析 → 生成 bug-patterns.md
                                      → 追加 AI 建议到 experience-notes.md
```

> 数据采集（脚本运行、环境配置）由 `@GuidedDev` Bug 分析管线统一处理。
> 本 Skill 仅负责"数据已就绪"后的 AI 分析环节。

### Step 1: 确认数据就绪

检查 `data/bug_analysis/` 目录：

```
list_dir("data/bug_analysis/")
```

预期看到：
- `{module}.json` — 模块级 Bug 数据
- `diffs/` — 全量 diff 文件目录

**如果目录不存在或为空** → 输出提示并终止模式 A：

```
⚠️ 暂无 Bug 分析数据。
🚀 推荐使用 @GuidedDev → "🐛 Bug 修复/分析" → "🔍 分析历史 Bug"
   它会帮你完成环境检测、配置补全、数据采集的全部交互流程。
```

### Step 2: 选择分析目标

使用 ask_questions 让用户选择模块（列出所有可用的 JSON 文件）。

### Step 3: 深度分析

分析策略（按数据量调整）：

| Bug 数量 | 策略 |
|---------|------|
| ≤ 20 | 全量读取所有 Bug + 全部关联 Diff |
| 20-50 | 全量 Bug 元数据 + 高频文件的 Diff + 跨模块 Bug 的 Diff |
| > 50 | 统计摘要优先 + 选读 Top-10 高频文件的典型 Diff |

**分析每个 Diff 时关注**：

1. **修改了什么函数/方法** — 从 `diff --git` 和 `@@` 行提取
2. **为什么改** — 结合 PR description 和 commit comment 理解根因
3. **改动模式** — 是加了检查条件？修了状态同步？补了通知？
4. **涉及的配置** — XML/JSON 配置文件的变更往往揭示路由和映射关系

### Step 4: 交叉关联

将 Diff 分析结果与以下信息交叉：
- 模块 Skill 的「常见陷阱」— 看是否有新的陷阱需要补充
- 模块 Skill 的「上下游依赖」— 看跨模块 Bug 是否在已知依赖路径上
- `docs/{{APP_NAME}}-功能依赖关系.md` — 验证联动 Bug 的影响范围

### Step 5: 输出

1. 生成 `references/bug-patterns.md`（可覆盖）
2. 追加 AI 建议到 `references/experience-notes.md`（仅追加到 🤖 区域）
3. 如果发现与现有「常见陷阱」矛盾的信息，向用户报告（不自动修改 SKILL.md）

---

## 模式 B：实时 Bug 诊断（完整流程）

### 概览

```
用户输入 Bug ID 或描述
        ↓
  识别涉及模块
        ↓
  加载模块知识（bug-patterns + experience-notes + SKILL.md）
        ↓
  [可选] 按需读取相关 Diff
        ↓
  输出诊断报告
```

### Step 1: 信息收集

**输入方式 A — Bug ID**：

```bash
# 在终端中运行
python scripts/get_bug_prs.py {bug_id} --show-changes
```

从输出中提取：Bug 标题、状态、关联 PR、变更文件。

**输入方式 B — 问题描述**：

直接从用户描述中提取关键词。

### Step 2: 模块识别

优先级：
1. Bug 标题中的 `[AppName]` 标签
2. 变更文件路径匹配（如 `FE/LesionSeg/` → lesion-segmentation）
3. 关键词匹配（"分割" → lesion-segmentation）
4. 无法确认时 → ask_questions

### Step 3: 知识聚合

按以下顺序加载知识（每个都用 read_file）：

```
1. templates/skills/{module}-expert/references/bug-patterns.md
   → 高频嫌疑文件、Bug 类型分布、修复模式

2. templates/skills/{module}-expert/references/experience-notes.md
   → 团队经验：嫌疑文件速查、隐性依赖、调试技巧

3. templates/skills/{module}-expert/SKILL.md
   → 代码入口、常见陷阱、上下游依赖

4. docs/{{APP_NAME}}-功能依赖关系.md（搜索相关模块章节）
   → 下游影响矩阵
```

### Step 4: 匹配与推理

综合以上知识：
- **嫌疑文件排序**：bug-patterns 的高频文件 ∩ experience-notes 的经验标记 → P0
- **历史相似 Bug**：从 JSON 数据中搜索标题/复现步骤相似的 Bug
- **影响范围**：从依赖关系文档判断下游模块

### Step 5: 输出诊断报告

格式见 SKILL.md 中的「输出诊断建议」模板。

---

## 数据采集参考

> 数据采集的交互式引导已内置在 `@GuidedDev` Bug 分析管线中。
> 以下为手动运行时的快速参考。

### 脚本常用命令

```bash
# 采集 {{APP_NAME}} 最近半年的 Bug（含 diff）
python scripts/analyze_bug_prs.py --app {{APP_NAME}} --days 180

# 快速模式（仅元数据，不拉取 diff）
python scripts/analyze_bug_prs.py --app {{APP_NAME}} --days 365 --no-diff

# 测试单个 Bug
python scripts/analyze_bug_prs.py --bug-id 1099814
```

### 前置配置（user_preferences.json）

```json
{
  "devops_config": { "pat": "...", "org_url": "...", "project": "YourProject" },
  "bug_analysis_config": { "local_repo_path": "D:/repos/{{PLATFORM_REPO}}" }
}
```

---

## 输出目录结构

```
data/bug_analysis/
├── lesion-segmentation.json     ← 模块级索引
├── dataload.json
├── registration.json
├── layout.json
├── _unmapped.json               ← 未匹配模块的 Bug
└── diffs/
    ├── 12345_PR20100.diff       ← Bug#12345 的 PR#20100 全量 diff
    ├── 12345_PR20101.diff
    └── ...
```
