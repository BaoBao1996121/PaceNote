# 电商项目示例

此目录展示了一个**已配置完成的项目**应该长什么样，供参考。

## 说明

这是运行 `setup_project.py` + `@ProjectSetup` 后的目标状态：

- `copilot-instructions.md` — 已替换所有占位符
- `copilot-resources/docs/` — 三个文档均已填充（检查清单、模块清单、依赖关系）

> 📌 实际使用中，你的项目还会有 `.github/skills/` 目录（由 `setup_project.py` 自动复制），
> 这里为节省空间没有重复包含。

## 结构

```
e-commerce/
├── copilot-instructions.md        ← 已填充的 Copilot 指令（占位符已替换）
├── copilot-resources/docs/
│   ├── checklist.md               ← 需求检查清单（已填充，28 项）
│   ├── modules.md                 ← 功能模块清单（6 个模块）
│   └── dependencies.md            ← 依赖关系（含矩阵 + 高风险链路）
└── README.md                      ← 本文件
```

## 如何使用

1. 参考此目录了解"填充完成后应该长什么样"
2. 运行 `python scripts/setup_project.py --target /path/to/your-project` 生成骨架
3. 使用 `@ProjectSetup 帮我完成项目接入` 填充内容
