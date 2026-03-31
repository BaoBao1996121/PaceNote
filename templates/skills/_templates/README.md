# Skill 模板

本目录包含创建新 Skill 的标准模板。

## 模板类型

| 模板 | 用途 | 适用场景 |
|------|------|---------|
| `module-expert-skill.md` | **统一模块专家模板** | 平台模块 (平台-*) 和应用模块 (app-* 等) |

> ⚠️ **统一模板说明**：`module-expert-skill.md` 同时适用于平台模块和应用模块，
> 通过 `[平台必填]`、`[应用必填]`、`[可选]` 标记区分差异。
> 旧模板（workflow-skill.md、app-expert-skill.md、domain-skill.md 等）已归档至 `_archived/` 目录。

## 使用方法

### 手动创建

1. 复制对应模板到 `.github/skills/{skill-name}/SKILL.md`
2. 替换模板中的 `{占位符}` 为实际内容
3. 确保 YAML frontmatter 的 `name` 唯一
4. 保存后 Copilot 会自动加载

### 批量生成（推荐）

使用 `#app-skill-wizard` Skill 或 `ProjectSetup` Agent 自动生成模块专家 Skill。

### 验证 Skill

```bash
python scripts/lint_skills.py --skill <skill-name>
```

## 命名规范

- Skill 名称使用小写字母和连字符: `{{PLATFORM_REPO}}-roi-expert`
- 目录名与 Skill 名称一致
- 分支标识追加在名称后: `{{PLATFORM_REPO}}-components-roi-expert-rc-V4.0`
- 最多 64 个字符

## YAML Frontmatter

### 格式规范

```yaml
---
name: skill-name-lowercase
description: |
  简短描述 - 一句话说明这个 Skill 做什么。
  详细说明何时使用此 Skill，包括具体场景、文件类型或触发任务。
  触发关键词: keyword1, keyword2, keyword3
---
```

### 必填字段

| 字段 | 说明 | 限制 |
|------|------|------|
| `name` | 唯一标识符 | 小写字母+连字符，最多 64 字符 |
| `description` | 描述和触发场景 | 最多 1024 字符，不含尖括号 |

### description 编写规范（重要）

`description` 是 AI 判断何时使用 Skill 的**唯一依据**！必须包含：

1. **做什么**: 一句话说明 Skill 的功能
2. **何时使用**: 详细的触发场景和条件
3. **触发关键词**: 帮助精准匹配的关键词列表

**示例**:
```yaml
description: |
  需求返讲助手 - 帮助研发人员进行需求评审和返讲文档撰写。
  当需要分析 PBI 内容、生成返讲文档、检查需求完整性时使用。
  触发关键词: 需求返讲, 评审需求, 返讲文档, 检查需求, PBI分析
```

## Skill 目录结构

```
skill-name/
├── SKILL.md (必需)
│   ├── YAML frontmatter 元数据 (必需)
│   └── Markdown 指令 (必需)
└── 捆绑资源 (可选)
    ├── scripts/          - 可执行脚本 (Python/Bash等)
    ├── references/       - 按需加载的参考文档
    └── assets/           - 用于输出的文件 (模板、图标等)
```

### scripts/ - 脚本目录

用于需要确定性可靠性或重复编写的任务的可执行代码。

- **何时使用**: 相同代码被重复编写，或需要确定性可靠性
- **优势**: Token 高效、确定性、可执行而无需加载到上下文

### references/ - 参考文档目录

用于在工作时按需加载到上下文的文档和参考资料。

- **何时使用**: AI 在工作时应参考的详细文档
- **最佳实践**: 如果文件较大 (>10k 词)，在 SKILL.md 中包含搜索模式
- **避免重复**: 信息应只存在于 SKILL.md 或 references 中，而非两者都有

### assets/ - 资产目录

不打算加载到上下文，而是用于 AI 产出的文件。

- **何时使用**: Skill 需要在最终输出中使用的文件
- **示例**: 模板、图片、字体、样板代码

## 最佳实践

### 内容原则

1. **简洁是关键**: 只添加 AI 不知道的上下文
2. **触发词要精准**: 帮助 Copilot 正确匹配
3. **代码示例要可运行**: 避免伪代码
4. **搜索建议要准确**: 减少搜索噪音

### 渐进式加载

保持 SKILL.md 正文简洁，控制在 500 行以内。接近此限制时拆分内容到 `references/` 目录。

### 必须包含的章节

1. **执行声明规范**: 开始/完成时的状态输出
2. **参考来源声明**: 使用的数据来源声明模板

详见 `shared-operational-rules/references/` 下的相关文档

## 不应包含的内容

Skill 应只包含直接支持其功能的必要文件。**不要**创建：

- ❌ README.md
- ❌ INSTALLATION_GUIDE.md
- ❌ CHANGELOG.md
- ❌ QUICK_REFERENCE.md

## 参考资源

- **Skill 批量生成**: `app-skill-wizard/SKILL.md` — 交互式创建模块专家
- **项目接入 Agent**: `templates/ProjectSetup.agent.md` — 新项目完整接入流程
- **模块专家模板**: `_templates/module-expert-skill.md` — v4 平台无关模板
