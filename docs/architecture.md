# PaceNote 架构说明

## 整体架构

PaceNote 是一个**工作流编排框架**，而非独立应用。它的核心是一套部署在目标项目 `.github/` 目录下的 **Skills**（AI 指令文件）和 **Agent 定义**，通过 VS Code + GitHub Copilot 的原生能力驱动。

```
┌──────────────────────────────────────────────────────────────┐
│                       VS Code + Copilot                       │
│  ┌─────────────┐  ┌─────────────┐  ┌────────────────────┐   │
│  │ GuidedDev   │  │ PlanPlus    │  │ ProjectSetup       │   │
│  │ Agent       │  │ Agent       │  │ Agent              │   │
│  └──────┬──────┘  └──────┬──────┘  └─────────┬──────────┘   │
│         │                │                    │               │
│  ┌──────▼────────────────▼────────────────────▼──────────┐   │
│  │              Skill 路由层 (自发现)                      │   │
│  │  workflow-router → expert-index → frontmatter 扫描     │   │
│  └──────┬─────────────────┬───────────────────┬──────────┘   │
│         │                 │                   │               │
│  ┌──────▼──────┐  ┌──────▼──────┐  ┌─────────▼────────┐    │
│  │ 工作流 Skill │  │ 基础 Skill  │  │ 域专家 Skill     │    │
│  │ (管线阶段)   │  │ (通用能力)  │  │ (领域知识)       │    │
│  └─────────────┘  └─────────────┘  └──────────────────┘    │
│         │                                    ▲               │
│         │         ┌──────────────┐           │               │
│         └────────→│ 标记系统     │───────────┘               │
│                   │ (跨阶段桥梁) │                            │
│                   └──────────────┘                            │
└──────────────────────────────────────────────────────────────┘
```

---

## 三层 Skill 体系

### Layer 1: 工作流 Skills（框架提供）

控制研发流程的推进节奏：

| Skill | 职责 | subAgent 数 |
|-------|------|------------|
| `pbi-reviewer` | 需求返讲 | 0（单 Agent） |
| `roundtable-debate` | 设计评审 | 5（4 并行 + 1 依赖） |
| `coding-agent` | 编码实现 | N（每任务 1 个） |
| `workflow-router` | 入口路由 | 0 |

### Layer 2: 基础 Skills（框架提供）

提供可复用的通用能力：

| Skill | 职责 |
|-------|------|
| `expert-index` | 动态发现和推荐域专家 |
| `shared-operational-rules` | 对话管理、质量自检、代码规范 |
| `experience-codifier` | 经验提炼、知识固化 |
| `bug-diagnosis-expert` | Bug 模式识别 + 实时诊断 |
| `git-blame` | 代码追溯 |
| `mcp-builder` | MCP Server 开发指南 |
| `app-skill-wizard` | 域专家创建向导 |
| `project-onboarding` | 项目接入协议 |

### Layer 3: 域专家 Skills（用户生成）

封装你自己项目的业务知识：

- 由 `#app-skill-wizard` 交互式生成
- 遵循 `_templates/module-expert-skill.md` 模板 v4
- 每个域专家覆盖一个业务模块

---

## Skill 路由机制

```
用户输入
    │
    ▼
┌─────────────────────────────┐
│ 1. 读取 copilot-instructions│  ← 全局规则 + 路由声明
└────────────┬────────────────┘
             │
    ▼
┌─────────────────────────────┐
│ 2. workflow-router 匹配     │  ← 意图→阶段映射
│    "帮我分析需求"→pbi-reviewer │
│    "设计评审"→roundtable      │
│    "根据设计编码"→coding-agent │
└────────────┬────────────────┘
             │
    ▼
┌─────────────────────────────┐
│ 3. expert-index 扫描        │  ← 按需推荐域专家
│    list_dir + read_file     │
│    匹配 frontmatter 关键词   │
└────────────┬────────────────┘
             │
    ▼
┌─────────────────────────────┐
│ 4. Skill 执行               │  ← 加载 SKILL.md + references/
│    按指令逐步执行             │
└─────────────────────────────┘
```

**关键设计**: Skill 通过 YAML frontmatter 的 `description` 字段声明触发关键词，AI 扫描 `.github/skills/*/SKILL.md` 自动发现——**零注册、零配置**。

---

## 标记系统（跨阶段数据桥）

三个阶段之间通过 **Markdown 内嵌标记** 实现松耦合的数据传递：

```markdown
<!-- 设计阶段写入 -->
<!-- KEY_OUTPUT_FOR_IMPL_START: 01-架构派 -->
架构决策摘要...
<!-- KEY_OUTPUT_FOR_IMPL_END: 01-架构派 -->

<!-- 成本派写入 -->
<!-- CODING_TASK_LIST_START -->
| ID | 任务 | 依赖 | 文件 |
|----|------|------|------|
| T1 | 创建数据模型 | 无 | models/order.py |
| T2 | 实现 API | T1 | api/orders.py |
<!-- CODING_TASK_LIST_END -->

<!-- 实施派写入 -->
<!-- CODING_IMPL:T1_START -->
```python
class Order:
    # 实现骨架...
```
<!-- CODING_IMPL:T1_END -->
```

**优势**: 
- 阶段间松耦合——任一阶段可单独运行
- 人类可读——Markdown 格式可直接审阅
- 可增量更新——后续阶段可追加标记

---

## Agent 层

### GuidedDev — 引导式管线

```
对话开始
    │
    ▼
┌──────────────┐    用户提供需求    ┌──────────────┐
│  检测管线状态  │ ──────────────→ │ 阶段1: 返讲   │
│  (可恢复)     │                  │ #pbi-reviewer │
└──────────────┘                  └───────┬───────┘
                                          │ 返讲文档
                                          ▼
                                  ┌──────────────┐
                                  │ 阶段2: 设计   │
                                  │ #roundtable   │
                                  └───────┬───────┘
                                          │ 设计文档
                                          ▼
                                  ┌──────────────┐
                                  │ 阶段3: 编码   │
                                  │ #coding-agent │
                                  └──────────────┘
```

- **状态持久化**: 写入 `.copilot-temp/guided-dev/{ID}/pipeline-state.json`
- **跨会话恢复**: 新对话自动检测未完成的管线
- **门控检查点**: 每个阶段结束时需用户确认才进入下一阶段

### PlanPlus — 规划+执行

5 阶段工作流：Discovery → Alignment → Design → Refinement → Execution

适用于不按管线流程的自由编码任务。

### ProjectSetup — 项目接入

4 阶段接入管线：信息收集 → Skill 生成 → 配置生成 → 验证

---

## 经验固化闭环

```
任务完成
    │
    ▼
┌─────────────────┐
│ 自动评估         │  ← 是否有 unexpected patterns?
│ experience-codifier│
└────────┬────────┘
         │ 有
         ▼
┌─────────────────┐
│ 质量门（双层）    │  ← 非显而易见？可验证？可复现？
└────────┬────────┘
         │ 通过
         ▼
┌─────────────────┐
│ 分类到对应 Skill │  ← Skill 规则 / Agent 规则 / 模板
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 人工确认后写入    │  ← 强制确认，不自动写入
└─────────────────┘
```

这形成了一个**自进化系统**——框架在使用中持续积累更好的实践。

---

## 文件组织约定

```
your-project/
├── .github/
│   ├── copilot-instructions.md   ← 全局指令（PaceNote 生成）
│   ├── GuidedDev.agent.md        ← 管线 Agent
│   ├── PlanPlus.agent.md         ← 通用 Agent
│   └── skills/                   ← PaceNote Skills
│       ├── pbi-reviewer/
│       │   ├── SKILL.md          ← 主指令
│       │   └── references/       ← 子文件（按需加载）
│       ├── roundtable-debate/
│       ├── coding-agent/
│       ├── your-module-expert/   ← 你的域专家
│       └── ...
│
├── .copilot-temp/                ← 运行时临时文件
│   └── guided-dev/{ID}/
│       └── pipeline-state.json   ← 管线状态
│
└── docs/                         ← 设计文档输出位置
    └── design-reviews/
```
