````markdown
# 核查清单定义（参考材料）

> ⚠️ **本文件为参考材料**，定义了5个角色各自需关注的质量维度。
> v2.0 中不再有独立的核查验证循环，但这些维度仍是各角色分析时的质量参考。
> 实施派在 Phase B 综合前4个角色产出时，天然形成质量校准。

> 🎯 **核心理念**：从"打分"改为"核查"，从"主观评分"改为"事实陈述"

---

## 核查输出格式（强制JSON）

> ⚠️ **每个subagent必须输出以下JSON格式，禁止自由文本评分！**

```json
{
  "reviewer": "架构派|效率派|质量派|成本派|实施派",
  "checklist": [
    {
      "item": "检查项名称",
      "required": true,
      "question": "具体检查问题",
      "pass": true,
      "evidence": "【必填】引用设计文档原文或说明'经检查无此问题'",
      "location": "【必填】章节名或'全文检查'"
    }
  ],
  "verdict": "PASS|FAIL|CONDITIONAL",
  "failReasons": ["【FAIL时必填】列出所有pass=false且required=true的item"],
  "conditionalReasons": ["【CONDITIONAL时必填】列出pass=false但required=false的item"]
}
```

---

## 通过规则（替代评分阈值）

| verdict | 条件 | 后续动作 |
|---------|------|----------|
| **PASS** | 所有required项pass=true | ✅ 此角色通过 |
| **CONDITIONAL** | 所有required项通过，但有非required项未通过 | ⚠️ 主Agent决定是否可接受 |
| **FAIL** | 任一required项pass=false | ❌ 必须修复后重新核查 |

### 整体通过标准

```
5个角色verdict均为PASS → 设计通过 → 输出最终文档
任一角色verdict为FAIL → 触发修复流程 → 交叉验证 → 重新核查
```

---

## 架构派核查清单 🧠

| # | 检查项 | required | 核查问题 | 反向验证 |
|---|--------|----------|----------|----------|
| A1 | 分层定义 | ✅ | 文档是否明确定义了各层（L2/L3/L4）？ | 列出文档中提到的各层名称 |
| A2 | 无跨层调用 | ✅ | 详细设计中是否存在L4直接调用L2的代码？ | 如有，列出具体代码位置 |
| A3 | 职责单一 | ✅ | 是否有预计超过200行的类未说明拆分策略？ | 列出所有类及其预计行数 |
| A4 | 依赖方向 | ✅ | 是否存在下层依赖上层的情况？ | 列出所有依赖关系 |
| A5 | 扩展点 | ⬜ | 是否为未来变化预留了扩展点？ | 列出扩展点设计 |
| A6 | 类图存在 | ✅ | 文档是否包含Mermaid classDiagram？ | 粘贴类图的class列表 |

---

## 效率派核查清单 ⚡

| # | 检查项 | required | 核查问题 | 反向验证 |
|---|--------|----------|----------|----------|
| E1 | 复用分析 | ✅ | 是否分析了可复用的现有组件？ | 列出复用机会表格 |
| E2 | 代码骨架 | ✅ | 核心类是否有方法骨架（非空接口）？ | 粘贴一个类的骨架代码 |
| E3 | 文件组织 | ✅ | 是否有树形文件目录结构？ | 粘贴目录结构 |
| E4 | 命名规范 | ⬜ | 命名是否遵循项目规范？ | 列出主要类/方法命名 |
| E5 | 平台能力 | ✅ | 是否正确使用了平台通用能力？ | 列出使用的平台接口 |

---

## 质量派核查清单 🛡️

| # | 检查项 | required | 核查问题 | 反向验证 |
|---|--------|----------|----------|----------|
| Q1 | 异常处理 | ✅ | 是否列出了异常处理清单？ | 粘贴异常处理表格 |
| Q2 | 边界条件 | ✅ | 是否覆盖空值、极值、并发、超时？ | 列出边界条件检查项 |
| Q3 | 测试用例 | ✅ | 是否有测试用例表格？ | 粘贴测试用例ID列表 |
| Q4 | 日志规范 | ⬜ | 是否定义了关键日志点？ | 列出日志点 |
| Q5 | 可测试性 | ✅ | 核心逻辑是否可独立单元测试？ | 说明测试策略 |

---

## 成本派核查清单 💰

| # | 检查项 | required | 核查问题 | 反向验证 |
|---|--------|----------|----------|----------|
| C1 | 任务粒度 | ✅ | 任务拆解是否都在2-8h范围内？ | 列出所有任务及工时 |
| C2 | 任务ID | ✅ | 每个任务是否有唯一ID（如BE-1, FE-2）？ | 列出所有任务ID |
| C3 | 依赖关系 | ✅ | 任务间依赖是否明确？ | 列出依赖链 |
| C4 | 总工时 | ✅ | 是否有总工时估算？ | 显示总工时 |
| C5 | 风险识别 | ⬜ | 是否识别了主要风险？ | 列出风险项 |

---

## 实施派核查清单 👨‍💻

| # | 检查项 | required | 核查问题 | 反向验证 |
|---|--------|----------|----------|----------|
| I1 | 时序图 | ✅ | 文档是否包含Mermaid sequenceDiagram？ | 粘贴时序图的participant列表 |
| I2 | 数据结构 | ✅ | 所有Context/Result类是否有完整字段定义？ | 列出所有类及其字段 |
| I3 | 接口签名 | ✅ | 接口方法是否有完整签名和注释？ | 粘贴一个接口定义 |
| I4 | 调用链 | ✅ | 从UI到数据落地的路径是否完整？ | 描述完整调用链 |
| I5 | BE函数 | ⬜ | C++后端函数签名是否完整？ | 粘贴头文件声明 |
| I6 | 实现骨架 | ✅ | 核心类是否有方法体骨架（含步骤注释）？ | 粘贴一个方法骨架 |

---

## 交叉验证矩阵

> 🎯 **修复者 ≠ 验证者**，避免"自己改自己评"

| 角色修复 | 由谁验证 | 原因 |
|----------|----------|------|
| 架构派修复 | 效率派验证 | 效率派关注可实现性 |
| 效率派修复 | 实施派验证 | 实施派关注能否编码 |
| 质量派修复 | 架构派验证 | 架构派关注整体一致性 |
| 成本派修复 | 质量派验证 | 质量派关注工时是否合理 |
| 实施派修复 | 效率派验证 | 效率派关注代码骨架可行性 |

---

## 核查Prompt模板

```markdown
你是{角色}，请对以下设计文档进行**核查**（不是评分！）。

## 设计文档
{设计文档内容}

## 核查清单
{角色对应的核查清单}

## 输出要求

**必须输出JSON格式**，禁止输出自由文本评分！

```json
{
  "reviewer": "{角色}",
  "checklist": [
    {
      "item": "时序图",
      "required": true,
      "question": "文档是否包含Mermaid sequenceDiagram？",
      "pass": true/false,
      "evidence": "【必填】粘贴时序图participant列表 或 '未找到sequenceDiagram代码块'",
      "location": "章节名 或 '全文检查'"
    }
    // ... 所有检查项
  ],
  "verdict": "PASS|FAIL|CONDITIONAL",
  "failReasons": ["列出所有pass=false且required=true的item"],
  "conditionalReasons": ["列出pass=false但required=false的item"]
}
```

⚠️ **关键要求**：
1. 每个检查项必须提供evidence（证据）
2. evidence必须引用文档原文或明确说明"未找到"
3. 禁止输出分数（如"9.5分"），只输出PASS/FAIL/CONDITIONAL
```

---

## 核查结果示例

### PASS示例
```json
{
  "reviewer": "实施派",
  "checklist": [
    {
      "item": "时序图",
      "required": true,
      "question": "文档是否包含Mermaid sequenceDiagram？",
      "pass": true,
      "evidence": "participant: UI, ViewModel, Service, Repository",
      "location": "二、架构设计"
    },
    {
      "item": "数据结构",
      "required": true,
      "question": "所有Context/Result类是否有完整字段定义？",
      "pass": true,
      "evidence": "ExportContext: OutputPath, VOIs, Format; ExportResult: Success, FilePath, Error",
      "location": "三、详细设计"
    }
  ],
  "verdict": "PASS",
  "failReasons": [],
  "conditionalReasons": []
}
```

### FAIL示例
```json
{
  "reviewer": "实施派",
  "checklist": [
    {
      "item": "时序图",
      "required": true,
      "question": "文档是否包含Mermaid sequenceDiagram？",
      "pass": false,
      "evidence": "全文搜索未找到sequenceDiagram代码块",
      "location": "全文检查"
    },
    {
      "item": "数据结构",
      "required": true,
      "question": "所有Context/Result类是否有完整字段定义？",
      "pass": false,
      "evidence": "ExportContext只有名字，无字段定义",
      "location": "三、详细设计"
    }
  ],
  "verdict": "FAIL",
  "failReasons": ["缺少时序图", "数据结构定义不完整"],
  "conditionalReasons": []
}
```

````
