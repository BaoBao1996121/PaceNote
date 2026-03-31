# PBI 智能解析规则

> 此文件包含 PBI 输入解析的详细规则，由 SKILL.md 通过 @reference 引用

---

## 支持的输入格式

| 格式 | 示例 | 解析方式 |
|------|------|----------|
| DevOps 链接 | `https://your-devops-server.example.com/YourProject/_queries/edit/1073716/...` | 从 URL 提取数字 ID |
| 工作项格式 | `Product Backlog Item 1073716: PBI_Func_...` | 提取 "Item" 后的数字 |
| 纯数字 ID | `1073716` | 直接使用 |
| PBI 标题 | `PBI_Func_{{APP_NAME}}_Feature_XXX_功能优化
| 自然语言 | `帮我评价下PBI PBI_Func_{{APP_NAME}}_Feature_XXX_功能优化

---

## 解析正则表达式

```javascript
// 1. 从 URL 提取 ID
url.match(/\/_(?:queries|workitems)\/(?:edit\/)?([0-9]+)/)

// 2. 从标准格式提取
text.match(/(?:Product Backlog Item|PBI|Work Item|Bug)\s*#?([0-9]+)/i)

// 3. 纯数字 (5-8位，符合 DevOps ID 范围)
text.match(/\b([0-9]{5,8})\b/)

// 4. PBI 标题 (用于搜索)
text.match(/PBI_[A-Za-z0-9_]+/)
```

---

## MCP 调用规则

### 🔴 强制执行：当检测到 PBI ID 时

```
工具名称: mcp_azuredevops_get_work_item
参数: 
  - id: <提取到的PBI数字ID>
  
示例调用:
  mcp_azuredevops_get_work_item(id=1073716)
```

### 只有标题没有 ID 时

```
工具名称: mcp_azuredevops_search_work_items  
参数:
  - query: <PBI标题>
```

### 提取的关键字段

| 字段 | 说明 |
|------|------|
| `System.Title` | 标题 |
| `System.Description` | 需求描述 (HTML格式，需解析) |
| `Microsoft.VSTS.Common.AcceptanceCriteria` | 验收标准 |
| `System.State` | 状态 |
| `System.IterationPath` | 迭代路径 |

---

## MCP 不可用时的备选方案

### 执行流程

```markdown
⚠️ **MCP 状态**: Azure DevOps 工具不可用
   原因: [工具未加载 / 连接失败 / 认证错误]

🔄 **启用备选方案**:
   1. 查询历史 PBI 知识库
   2. 请用户手动提供 PBI 内容
```

### 查询历史 PBI 知识库

> 配置文件: `data/user_preferences.json`（相对于工作区根目录）
> 字段: `pbi_csv_path`

**CSV 列结构**:
| 列名 | 说明 |
|------|------|
| `Work Item ID` | PBI 编号 |
| `Title` | 标题 |
| `State` | 状态 |
| `Description` | 描述 |

**搜索方式**:
1. 按 ID 精确匹配
2. 按标题关键词模糊匹配
3. 返回最相关的 3-5 条记录作为参考

---

## 输入示例

**方式1: DevOps 链接**
```
帮我做需求返讲: https://your-devops-server.example.com/YourProject/_queries/edit/1073716/?triage=true
```

**方式2: 标准格式**
```
请分析这个 PBI:
Product Backlog Item 1073716: PBI_Func_{{APP_NAME}}_Feature_XXX_功能优化
```

**方式3: 纯 ID**
```
需求返讲 1073716
```

**方式4: PBI 标题**
```
帮我评价下PBI PBI_Func_{{APP_NAME}}_Feature_XXX_功能优化
```

**方式5: 直接粘贴内容**
```
帮我做一下这个PBI的需求返讲:
PBI-123456: VOI分割支持多阈值配置
需求描述: 用户希望在进行PET病灶分割时，能够配置多个阈值策略...
```
