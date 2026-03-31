```markdown
# 🛠️ 代码规范

<!-- 🤖 AI 填充指南
将以下提示词发送给你的 AI 助手：

---
我的项目使用以下技术栈：
[列出你的技术栈，如 Java/Spring、Python/Django、C#/.NET、TypeScript/React 等]

请帮我生成代码命名约定表：
| 代码层 | 语言 | 命名约定 | 示例 |

以及常见的代码规范要点（目录结构约定、注释要求、测试要求等）。
---
-->

| 层 | 语言 | 命名约定 |
|---|------|---------|
| 后端 | [你的后端语言] | [命名规范] |
| 前端 | [你的前端语言] | [命名规范] |
| API | [API 规范] | [命名规范] |

## 🔴 PowerShell 文件编码安全（强制）

> **PowerShell 5.1 在中文 Windows（CP936）上，`Get-Content`/`Set-Content` 默认使用 GBK 编码，
> 会静默损坏 UTF-8 文件中的 CJK 字节（部分字节被替换为 `?` 即 0x3F）。**

| 场景 | ❌ 禁止 | ✅ 正确做法 |
|------|--------|------------|
| 读写文本文件 | `Get-Content` / `Set-Content`（不带 `-Encoding`） | `[System.IO.File]::ReadAllText($path, [System.Text.Encoding]::UTF8)` |
| 批量替换文件内容 | PowerShell `-replace` + `Set-Content -NoNewline` | Python `open(f, encoding='utf-8')` 读写 |
| 需要用 PowerShell | — | 始终加 `-Encoding UTF8`（注意：会添加 BOM） |
| 需要无 BOM 的 UTF-8 | `Set-Content -Encoding UTF8`（有 BOM） | `[IO.File]::WriteAllText($path, $content, [Text.UTF8Encoding]::new($false))` |

**经验来源**: 批量操作含中文的文件时，PowerShell 默认编码导致文件损坏。

```
