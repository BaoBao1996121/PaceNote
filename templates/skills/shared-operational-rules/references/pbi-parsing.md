# 🎫 PBI 智能解析

**支持多种方式传入 PBI，AI 会自动识别并获取详情：**

| 输入方式 | 示例 |
|----------|------|
| DevOps 链接 | `https://your-devops-server.example.com/YourProject/_queries/edit/1073716/...` |
| 标准格式 | `Product Backlog Item 1073716: PBI_Func_...` |
| 纯 ID | `1073716` |
| PBI 标题 | `PBI_Func_{{APP_NAME}}_Feature_XXX_功能优化

## 强制规则

1. 检测到 PBI ID → **必须尝试调用** `mcp_azuredevops_get_work_item`
2. MCP 不可用 → 查询历史 PBI CSV + 请用户粘贴内容
3. **禁止**: 不尝试就说"无法访问"

> 📚 详细解析规则参见: `#pbi-reviewer`
