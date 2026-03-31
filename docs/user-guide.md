# PaceNote 使用手册

## 安装与部署

### 前置条件

| 工具 | 最低版本 | 用途 |
|------|---------|------|
| VS Code | 1.100+ | 编辑器 |
| GitHub Copilot | Agent 模式 | AI 引擎 |
| Python | 3.10+ | 脚本工具 |

### 部署方式

#### 方式 A：脚本部署（推荐）

```bash
# 部署通用 Skills 到目标项目
python scripts/deploy_skills.py --target /path/to/your-project --categories common

# 部署含自定义类别的 Skills
python scripts/deploy_skills.py --target /path/to/your-project --categories common,platform
```

#### 方式 B：手动部署

1. 将 `templates/skills/` 下的文件夹复制到目标项目的 `.github/skills/`
2. 将 Agent `.md` 文件复制到目标项目的 `.github/`
3. 将 `templates/copilot-instructions.md` 复制到 `.github/copilot-instructions.md`

---

## 使用三阶段管线

### 方式 1：GuidedDev 全自动管线

```
@GuidedDev 帮我分析这个需求：

标题：用户登录支持短信验证码
描述：在现有密码登录基础上，增加短信验证码登录方式...
```

GuidedDev 会自动依次执行：需求返讲 → 设计评审 → 编码实现，每个阶段结束后等待你确认。

### 方式 2：单阶段手动调用

```
# 仅做需求返讲
#pbi-reviewer 帮我分析这个需求：[需求描述]

# 仅做设计评审（需要先有返讲文档）
#roundtable-debate 帮我做设计评审

# 仅做编码（需要先有设计文档）
#coding-agent 帮我根据设计编码
```

---

## 域专家系统

### 什么是域专家

域专家是封装了**特定业务模块知识**的 Skill。当 AI 在需求分析或设计评审时遇到相关模块，会自动调用域专家获取上下文。

### 创建域专家

在 Copilot Chat 中：

```
#app-skill-wizard 帮我为购物车模块(shopping-cart)生成一个域专家
```

向导会交互式引导你提供：
1. 模块名称和职责
2. 代码仓库路径
3. 关键入口文件
4. 已知陷阱和经验

### 域专家如何被使用

1. `#pbi-reviewer` 分析需求时 → 调用 `#expert-index` 扫描匹配的域专家
2. `#roundtable-debate` 设计时 → 每个角色的 subAgent 携带域专家知识
3. `#coding-agent` 编码时 → 参考域专家中的陷阱表和依赖关系

---

## 经验固化

### 自动触发

每次任务完成后，`#experience-codifier` 自动评估：
- 是否遇到了预期外的问题？
- 是否找到了更好的做法？
- 是否踩坑后发现了隐含规则？

如果有，会经过**双层质量门**后请你确认是否写入知识库。

### 手动触发

```
#experience-codifier 我发现了一个重要经验：[描述经验]
```

---

## Skill 验证

```bash
# 验证所有 Skills 格式
python scripts/lint_skills.py

# 验证单个 Skill
python scripts/lint_skills.py --skill my-expert
```

验证内容包括：
- YAML frontmatter 格式
- 必填字段（name, description）
- 触发关键词冲突检测
- 行数限制检查

---

## 常见问题

### Q: Skill 不被触发怎么办？

检查 `SKILL.md` 的 YAML frontmatter 中 `description` 字段是否包含正确的触发关键词。

### Q: 需要从哪个阶段开始？

不需要全部走完三阶段。可以：
- 只做需求返讲（快速理解需求）
- 只做设计评审（已有需求文档时）
- 只做编码（已有设计文档时）

### Q: 支持哪些编程语言？

PaceNote 是**语言无关**的工作流框架。域专家模板支持任意技术栈。
