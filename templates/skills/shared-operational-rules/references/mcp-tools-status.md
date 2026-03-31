```markdown
# 🔧 MCP 工具状态

> 📌 根据你配置的 MCP 服务调整此文件。PaceNote 框架支持任意 MCP 工具集成。

## 已配置的 MCP 工具

<!-- 🤖 AI 填充指南
将以下提示词发送给你的 AI 助手：

---
我配置了以下 MCP 服务：
[列出你的 MCP 服务，如 Azure DevOps MCP、GitHub MCP、Jira MCP、飞书 MCP 等]

请帮我生成每个 MCP 工具的状态表，格式如下：

### [MCP 服务名]
工具名称格式: `mcp_xxx_<action>`

| 工具 | 用途 | 返回内容 | 注意事项 |
---
-->

### Issue Tracker MCP（如 Azure DevOps / GitHub / Jira）

| 工具 | 用途 | 返回内容 |
|------|------|----------|
| `get_work_item` / `get_issue` | 获取单个需求详情 | ✅ 完整字段 |
| `search_work_items` / `search_issues` | 搜索需求列表 | ⚠️ 可能仅返回摘要 |
| `search_code` | 搜索远程仓库代码 | 代码片段 |
| `get_file_content` | 读取远程仓库完整文件 | ✅ 完整文件内容 |

### 文档平台 MCP（如 飞书 / Notion / Confluence）

| 工具 | 用途 |
|------|------|
| `import_document` | 导入/创建文档 |
| `search_document` | 搜索文档 |
| `get_document_content` | 获取文档内容 |

## MCP 不可用时的处理

当 MCP 工具调用失败或不存在时：

1. **明确告知用户** MCP 状态
2. **认证失败（401/403）时 — 禁止静默降级**:
   - 检测到认证错误时，**必须通过 ask_questions 询问用户**
   - 向用户说明认证可能已过期，提供两个选项：
     - **选项 A**: 提供新的认证信息（Token/PAT）
     - **选项 B**: 使用降级方案（读本地缓存/手动粘贴内容）
   - **严禁**在用户不知情的情况下自动降级
3. **其他 MCP 错误的备选方案**:
   - **Issue MCP**: 读取本地 CSV/缓存文件、请用户手动粘贴内容
   - **文档 MCP**: 保存为本地 Markdown 文档
4. **建议用户检查**:
   - VS Code 输出面板 → MCP 日志
   - 确认 Node.js/npx 环境正常
   - 重启 VS Code

```
