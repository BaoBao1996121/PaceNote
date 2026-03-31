# 设计评审文档模板（Phase C 组装参考）

> 本文件是设计评审文档（`06-design-review.md`）的组装模板。
> Phase C 主Agent根据此模板结构，从 01-05.md 的 DESIGN_REVIEW 标记区段提取内容，填充到对应章节。
>
> 📚 来源: `docs/需求返讲与设计评审文档模板.md` 第二部分

---

## 文档信息

| 属性 | 内容 |
|------|------|
| PBI 编号 | `{从需求提取}` |
| PBI 标题 | `{从需求提取}` |
| 编写日期 | `{当前日期}` |
| 版本 | v1.0 |

---

## 1. 概要设计

### 1.1 架构图

<!-- AI_INTERNAL: DESIGN_REVIEW:1.1 来自 01-architecture.md — 本行仅供 AI 组装参考，禁止保留到最终文档 -->

使用 Mermaid 或图片展示分层架构（应用FE → 应用BE → 平台BE）。

### 1.2 模块职责

<!-- AI_INTERNAL: DESIGN_REVIEW:1.2 来自 01-architecture.md — 本行仅供 AI 组装参考，禁止保留到最终文档 -->

| 模块 | 层级 | 职责 |
|------|------|------|
| `<类名/模块名>` | 应用FE/应用BE/平台BE | `<职责描述>` |

### 1.3 文件结构

<!-- AI_INTERNAL: DESIGN_REVIEW:1.3 来自 02-efficiency.md — 本行仅供 AI 组装参考，禁止保留到最终文档 -->

标注新增/修改的文件，使用目录树格式：

```
src/{{PLATFORM_NAMESPACE}}.XXX/
├── ViewModels/
│   ├── XxxViewModel.cs          # 修改：描述改动
│   └── YyyViewModel.cs          # 新增：描述功能
```

---

## 2. 详细设计

### 2.1 时序图（关键流程）

<!-- AI_INTERNAL: DESIGN_REVIEW:2.1 来自 05-implementation.md — 本行仅供 AI 组装参考，禁止保留到最终文档 -->

🔴 必须使用 Mermaid `sequenceDiagram` 代码块展示核心交互流程。纯文字描述不合格。

### 2.2 核心类设计

<!-- AI_INTERNAL: DESIGN_REVIEW:2.2 来自 01-architecture.md — 本行仅供 AI 组装参考，禁止保留到最终文档 -->

🔴 必须使用 Mermaid `classDiagram` 代码块展示关键类及其关系。纯文字描述不合格。

### 2.3 接口设计

<!-- AI_INTERNAL: DESIGN_REVIEW:2.3a 来自 01-architecture.md, DESIGN_REVIEW:2.3b 来自 05-implementation.md — 本行仅供 AI 组装参考，禁止保留到最终文档 -->

🔴 C# 接口定义每个公开方法必须含 `/// <summary>` XML 注释，缺失视为不合格。

**前端接口 (C#):**

```csharp
/// <summary>接口描述</summary>
public interface IXxxService
{
    Task<Result> MethodAsync(string paramName);
}
```

**后端接口 (C++):**

```cpp
/// @brief 方法描述
int MethodName(const std::string& paramName);
```

### 2.4 数据结构

<!-- AI_INTERNAL: DESIGN_REVIEW:2.4 来自 05-implementation.md — 本行仅供 AI 组装参考，禁止保留到最终文档 -->

C# 数据类 + Proto 协议变更（如有）。

### 2.5 关键流程

<!-- AI_INTERNAL: DESIGN_REVIEW:2.5 来自 05-implementation.md — 本行仅供 AI 组装参考，禁止保留到最终文档 -->

使用 Mermaid flowchart 展示关键算法/校验/转换流程。

---

## 3. 可能存在的问题

### 3.1 技术风险

<!-- AI_INTERNAL: DESIGN_REVIEW:3.1 来自 04-cost.md — 本行仅供 AI 组装参考，禁止保留到最终文档 -->

| 风险 | 描述 | 缓解措施 |
|------|------|----------|

### 3.2 UX 风险

<!-- AI_INTERNAL: DESIGN_REVIEW:3.2 来自 03-quality.md — 本行仅供 AI 组装参考，禁止保留到最终文档 -->

| UX 风险 | 描述 | 缓解措施 |
|---------|------|----------|

### 3.3 兼容性

<!-- AI_INTERNAL: DESIGN_REVIEW:3.3 来自 03-quality.md — 本行仅供 AI 组装参考，禁止保留到最终文档 -->

| 兼容性项 | 影响 | 处理方案 |
|----------|------|----------|
| 历史数据兼容 | 是/否 | `<方案>` |
| 书签兼容 | 是/否 | `<方案>` |
| 其他应用兼容 | 是/否 | `<方案>` |

---

## 4. 自测与测试范围

### 4.1 自测范围

<!-- AI_INTERNAL: DESIGN_REVIEW:4.1 来自 03-quality.md — 本行仅供 AI 组装参考，禁止保留到最终文档 -->

| 测试项 | 测试内容 | 预期结果 |
|--------|----------|----------|

### 4.2 三方软件/系统兼容测试（如适用）

<!-- AI_INTERNAL: DESIGN_REVIEW:4.2 来自 03-quality.md — 本行仅供 AI 组装参考，禁止保留到最终文档 -->

| 软件/系统 | 测试内容 | 预期结果 |
|-----------|----------|----------|

### 4.3 测试提醒

<!-- AI_INTERNAL: DESIGN_REVIEW:4.3 来自 03-quality.md — 本行仅供 AI 组装参考，禁止保留到最终文档 -->

1. **重点测试场景**: ...
2. **边界测试**: ...
3. **性能测试**: ...

---

## 5. 评审结论

> ⚠️ 以下部分留空，由人工在评审会议后填写。

### 5.1 评审记录

| 评审日期 | 评审意见 | 状态 |
|----------|----------|------|
| `<日期>` | `<意见>` | 🟢 通过 / 🟡 待补充 / 🔴 不通过 |

### 5.2 遗留问题

| 问题 | 负责人 | 计划完成时间 |
|------|--------|------------|
| `<遗留问题>` | `<负责人>` | `<时间>` |

---

## DESIGN_REVIEW 标记 → 章节映射速查

| 标记 | 章节 | 来源角色 | 来源文件 |
|------|------|----------|----------|
| `1.1` | §1.1 架构图 | 🧠架构派 | `01-architecture.md` |
| `1.2` | §1.2 模块职责 | 🧠架构派 | `01-architecture.md` |
| `1.3` | §1.3 文件结构 | ⚡效率派 | `02-efficiency.md` |
| `2.1` | §2.1 时序图 | 👨‍💻实施派 | `05-implementation.md` |
| `2.2` | §2.2 核心类设计 | 🧠架构派 | `01-architecture.md` |
| `2.3a` | §2.3 接口设计(C#) | 🧠架构派 | `01-architecture.md` |
| `2.3b` | §2.3 接口设计(C++) | 👨‍💻实施派 | `05-implementation.md` |
| `2.4` | §2.4 数据结构 | 👨‍💻实施派 | `05-implementation.md` |
| `2.5` | §2.5 关键流程 | 👨‍💻实施派 | `05-implementation.md` |
| `3.1` | §3.1 技术风险 | 💰成本派 | `04-cost.md` |
| `3.2` | §3.2 UX风险 | 🛡️质量派 | `03-quality.md` |
| `3.3` | §3.3 兼容性 | 🛡️质量派 | `03-quality.md` |
| `4.1` | §4.1 自测范围 | 🛡️质量派 | `03-quality.md` |
| `4.2` | §4.2 三方兼容测试 | 🛡️质量派 | `03-quality.md` |
| `4.3` | §4.3 测试提醒 | 🛡️质量派 | `03-quality.md` |
