# 🎯 PaceNote — AI 驱动的研发工作流框架

> **从需求到代码，全链路 AI 辅助研发管线**

PaceNote 是一套基于 VS Code + GitHub Copilot 的**研发工作流编排框架**。它将软件研发拆解为三个阶段，每个阶段由专门的 AI Skill 驱动，形成从需求到代码的端到端自动化管线。

---

## ✨ 核心能力

### 🔄 三阶段研发管线

```
需求/Issue/PBI                    设计文档（6 份）                  可运行的代码
      │                                │                                │
      ▼                                ▼                                ▼
┌──────────────┐    标记桥     ┌──────────────┐    标记桥     ┌──────────────┐
│ 阶段1: 返讲  │ ──────────→  │ 阶段2: 设计  │ ──────────→  │ 阶段3: 编码  │
│ #pbi-reviewer│              │ #roundtable  │              │ #coding-agent│
└──────────────┘              └──────────────┘              └──────────────┘
      │                              │                              │
  ■ 解析需求                   ■ 5角色并行论辩              ■ 拓扑排序任务
  ■ 匹配领域专家               ■ 架构/效率/质量/成本/实施    ■ subAgent逐任务编码  
  ■ 输出检查清单                ■ 自动评审与打分              ■ 暂停点人工确认
  ■ 生成返讲文档                ■ 6份设计交付物               ■ 变更报告
```

### 🧠 Skill 生态系统

- **15 个核心 Skills** — 覆盖需求、设计、编码、诊断、经验固化的完整研发流程
- **自发现机制** — 新增 Skill 自动生效，无需中央注册
- **域专家模板 v4** — 用 AI 快速为你的项目生成领域专家
- **经验固化闭环** — 自动提炼最佳实践并写入知识库

### 🤖 多 Agent 协作

- **GuidedDev Agent** — 引导式三阶段管线，状态持久化，跨会话恢复
- **PlanPlus Agent** — 规划+执行通用 Agent，研究→方案→实施
- **ProjectSetup Agent** — 新项目从 0 到 1 接入框架

---

## 🚀 快速开始（3 步）

### 前置条件

- VS Code (≥ 1.100) + GitHub Copilot 订阅（需 Agent 模式）
- Python 3.10+

### Step 1: 部署到你的项目（2 分钟）

```bash
git clone https://github.com/BaoBao1996121/PaceNote.git
python PaceNote/scripts/setup_project.py --target /path/to/your-project
```

配置向导会交互式引导你完成：
- 📋 收集项目信息（名称、是否有平台层）
- 📦 复制 15 个核心 Skills + 3 个 Agent 定义
- ⚙️ 自动替换配置文件中的占位符
- 📁 创建项目文档结构（含 AI 填充提示词）
- ✅ 验证部署完整性

### Step 2: 填充领域知识（20-60 分钟）

用 VS Code 打开你的项目，在 Copilot Chat 中输入：

```
@ProjectSetup 帮我完成项目接入
```

ProjectSetup Agent 会引导你完成：
1. **平台架构发现** → 生成 `platform-architecture` Skill
2. **域专家批量生成** → 为每个业务模块创建域专家
3. **项目文档填充** → 生成检查清单、模块清单、依赖关系

> 💡 每个需要填充的文件都**内置了 AI 提示词**——你只需复制提示词给 Copilot，它会引导你完成。

### Step 3: 开始使用

```
@GuidedDev 帮我分析这个需求：[粘贴你的需求描述]
```

GuidedDev 会自动执行三阶段管线：需求返讲 → 设计评审 → 编码实现。

> 💡 不确定从哪开始？试试 `#workflow-router`

---

<details>
<summary>📌 进阶用法（手动部署 / 按类别过滤）</summary>

#### 手动复制（不使用配置向导）

```bash
# 复制 Skills
cp -r PaceNote/templates/skills/* your-project/.github/skills/

# 复制 Agent 定义
cp PaceNote/templates/GuidedDev.agent.md your-project/.github/
cp PaceNote/templates/PlanPlus.agent.md your-project/.github/
cp PaceNote/templates/ProjectSetup.agent.md your-project/.github/

# 复制 Copilot 指令（⚠️ 需要手动替换 {{...}} 占位符）
cp PaceNote/templates/copilot-instructions.md your-project/.github/
```

#### 按类别过滤部署

```bash
# 仅部署通用 Skills
python PaceNote/scripts/deploy_skills.py --target /path/to/project --categories common

# 预览将部署哪些 Skills
python PaceNote/scripts/deploy_skills.py --target /path/to/project --categories common --dry-run
```

#### 单独生成域专家

```
#app-skill-wizard 帮我为 [模块名] 生成一个域专家 Skill
```

</details>

---

## 📁 目录结构

```
PaceNote/
├── templates/                       # 部署到目标项目的模板
│   ├── copilot-instructions.md      # Copilot 指令模板
│   ├── pbi-review-document.md       # 需求评审文档模板
│   ├── GuidedDev.agent.md           # 三阶段管线 Agent
│   ├── PlanPlus.agent.md            # 规划执行 Agent
│   ├── ProjectSetup.agent.md        # 项目接入 Agent
│   │
│   └── skills/                      # Skill 库（核心 + 示例）
│       ├── _templates/              # 域专家模板 v4
│       ├── pbi-reviewer/            # 需求返讲
│       ├── roundtable-debate/       # 圆桌会议（5 agent 设计评审）
│       ├── coding-agent/            # 设计驱动编码
│       ├── expert-index/            # 专家索引
│       ├── workflow-router/         # 工作流路由
│       ├── shared-operational-rules/# 全局运维规则
│       ├── experience-codifier/     # 经验固化
│       ├── bug-diagnosis-expert/    # Bug 诊断
│       ├── git-blame/               # 代码追溯
│       ├── mcp-builder/             # MCP 开发指南
│       ├── platform-architecture/   # 平台架构（需填充）
│       ├── project-onboarding/      # 项目接入
│       ├── app-skill-wizard/        # Skill 创建向导
│       └── examples/                # 示例域专家
│           └── shopping-cart-expert/ # 电商购物车示例
│
├── scripts/                         # 工具脚本
│   ├── setup_project.py             # ⭐ 一站式配置向导（推荐入口）
│   ├── lint_skills.py               # Skill 格式验证
│   └── deploy_skills.py             # Skill 分类部署（进阶）
│
├── data/                            # 配置示例
│   ├── shared_config.example.json   # 连接配置模板
│   └── skill_categories.example.json# Skill 分类配置模板
│
├── docs/                            # 文档
│   ├── architecture.md              # 框架架构
│   ├── user-guide.md                # 使用手册
│   ├── creating-domain-experts.md   # 域专家创建指南
│   └── workflow-overview.md         # 工作流图解
│
└── examples/                        # 完整项目示例
    └── e-commerce/                  # 电商项目配置示例
```

---

## 🔑 核心概念

### Skill 自发现

每个 Skill 由 `SKILL.md` 文件定义，包含 YAML frontmatter：

```yaml
---
name: my-expert
description: |
  触发关键词: xxx、yyy、zzz
---
```

AI 通过扫描所有 `SKILL.md` 的 `description` 字段自动路由——**新增 Skill 即刻生效，无需任何注册**。

### 标记系统（跨阶段数据桥）

阶段间通过 Markdown 内嵌标记传递结构化数据：

| 标记 | 写入者 | 读取者 | 用途 |
|------|--------|--------|------|
| `KEY_OUTPUT_FOR_IMPL` | 设计角色 | 实施规划者 | 各角色设计总结 |
| `CODING_TASK_LIST` | 成本派角色 | 编码 Agent | 任务拆解表 |
| `CODING_IMPL:{taskId}` | 实施派角色 | 编码 Agent | 实现骨架 |

### 域专家体系

使用 `#app-skill-wizard` 可以快速为你的业务模块生成域专家。每个专家遵循 **v4 统一模板**，包含：
- 模块职责与场景入口
- 踩坑陷阱表格
- 依赖关系声明
- 配置映射清单

---

## 📖 核心 Skill 一览

| Skill | 用途 | 触发方式 |
|-------|------|----------|
| `#pbi-reviewer` | 需求返讲：解析→检查清单→返讲文档 | "帮我分析这个需求" |
| `#roundtable-debate` | 圆桌会议：5 角色设计评审 | "帮我做设计评审" |
| `#coding-agent` | 设计驱动编码：读取设计→逐任务编码 | "帮我根据设计编码" |
| `#expert-index` | 专家推荐：智能匹配领域专家 | "推荐专家" |
| `#workflow-router` | 工作流入口：引导选择阶段 | "帮我"/"工作流" |
| `#experience-codifier` | 经验固化：自动提炼最佳实践 | 任务完成后自动触发 |
| `#bug-diagnosis-expert` | Bug 诊断：模式识别+实时诊断 | "诊断 Bug" |
| `#app-skill-wizard` | 域专家生成：交互式创建 Skill | "创建域专家" |
| `#platform-architecture` | 架构知识：代码层级识别 | 涉及平台代码时 |
| `#project-onboarding` | 项目接入：生成完整配置 | 新项目初始化 |

---

## 🏗️ 你需要做什么

PaceNote 提供了完整的**工作流骨架**，但需要你为自己的项目填充**领域知识**：

| 需要填充的内容 | 填充方式 | 预计耗时 |
|---------------|---------|---------|
| 平台架构知识 | 用 AI 对话填充 `platform-architecture/SKILL.md` | 30 分钟 |
| 域专家（每个业务模块一个）| 使用 `#app-skill-wizard` 自动生成 | 每个 15 分钟 |
| 项目检查清单 | 按模板填充 `_templates/project-requirement-checklist.md` | 20 分钟 |
| 功能模块清单 | 按模板填充 `_templates/project-module-list.md` | 10 分钟 |
| Skill 分类配置 | 参考 `skill_categories.example.json` 配置 | 5 分钟 |

> 💡 **所有需要填充的模板都内置了 AI 提示词**——你只需把提示词丢给 Copilot，它会引导你完成填充。

---

## 🤝 适用场景

- ✅ 中大型项目需要规范化需求→设计→编码流程
- ✅ 团队希望用 AI 辅助设计评审
- ✅ 想让 AI 深入理解业务上下文而非通用回答
- ✅ 希望积累可复用的领域知识和最佳实践
- ✅ 多人协作项目需要统一 AI 工作方式

---

## 📄 License

MIT License — 自由使用、修改、分发。

---

## 🙏 致谢

PaceNote 源自一线研发团队的实战经验，在超过 200 个 PBI 的需求分析、设计评审和编码实现中持续打磨而成。
