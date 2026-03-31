#!/usr/bin/env python3
"""
PaceNote 项目配置工具

交互式 CLI，一站式将 PaceNote 部署到你的项目。
自动完成：收集项目信息 → 复制 Skills/Agents → 替换占位符 → 创建文档结构 → 验证。

用法:
    python scripts/setup_project.py --target /path/to/your-project
    python scripts/setup_project.py --target /path/to/your-project --non-interactive
"""

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

# 兼容 GBK 终端（中文 Windows PowerShell 5.1）
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, OSError):
    pass


# ─── 工具函数 ───────────────────────────────────────────────

def get_pacenote_root() -> Path:
    """获取 PaceNote 根目录"""
    return Path(__file__).resolve().parent.parent


def prompt_input(question: str, default: str = "") -> str:
    """带默认值的交互式输入"""
    suffix = f" [{default}]" if default else ""
    answer = input(f"  {question}{suffix}: ").strip()
    return answer if answer else default


def prompt_yes_no(question: str, default: bool = True) -> bool:
    """是/否交互"""
    suffix = " [Y/n]" if default else " [y/N]"
    answer = input(f"  {question}{suffix}: ").strip().lower()
    if not answer:
        return default
    return answer in ("y", "yes", "是")


def print_header(step: int, total: int, title: str):
    """打印步骤标题"""
    print(f"\n{'─' * 50}")
    print(f"  📌 步骤 {step}/{total}: {title}")
    print(f"{'─' * 50}")


def print_box(lines: list, title: str = ""):
    """打印框线内容"""
    width = max(len(line) for line in lines) + 4
    width = max(width, len(title) + 6, 40)
    print()
    if title:
        print(f"  ┌─ {title} {'─' * max(0, width - len(title) - 4)}┐")
    else:
        print(f"  ┌{'─' * width}┐")
    for line in lines:
        print(f"  │  {line:<{width - 4}}  │")
    print(f"  └{'─' * width}┘")


# ─── 核心逻辑 ───────────────────────────────────────────────

# Skills 复制时排除的文件名模式
EXCLUDE_PATTERNS = {"_cleanup-report.md", "*.pyc", "__pycache__"}
# 受保护文件（备份后恢复）
PROTECTED_FILES = {"experience-notes.md", "bug-patterns.md"}


def collect_project_info(non_interactive: bool = False) -> dict:
    """交互式收集项目信息

    Returns:
        dict: {project_name, platform_prefix, platform_repo, has_platform}
    """
    if non_interactive:
        return {
            "project_name": "my-project",
            "platform_prefix": "",
            "platform_repo": "",
            "has_platform": False,
            "pacenote_path": str(get_pacenote_root()),
        }

    print()
    print("  PaceNote 需要了解一些你的项目信息来完成配置。")
    print("  如果不确定，直接按回车跳过，后续可以用 @ProjectSetup 补充。")
    print()

    project_name = prompt_input("项目名称（英文，如 my-app）", "my-project")

    print()
    print('  💡 如果你的项目有 平台/框架层（多个应用共用的底层代码），')
    print('     PaceNote 可以帮 AI 区分"平台代码"和"应用代码"。')
    print('     如果只是单一项目，直接跳过即可。')
    print()

    has_platform = prompt_yes_no("你的项目是否有独立的平台/框架层？", default=False)

    platform_prefix = ""
    platform_repo = ""
    if has_platform:
        platform_prefix = prompt_input(
            "平台前缀（用于命名域专家，如 myplatform）", ""
        )
        platform_repo = prompt_input(
            "平台代码仓库名（如 my-platform-components）", ""
        )

    return {
        "project_name": project_name,
        "platform_prefix": platform_prefix,
        "platform_repo": platform_repo,
        "has_platform": has_platform,
        "pacenote_path": str(get_pacenote_root()),
    }


def copy_skills(
    pacenote_root: Path,
    target: Path,
    include_examples: bool = True,
) -> int:
    """复制核心 Skills 到目标项目（自包含，无外部依赖）"""
    skills_src = pacenote_root / "templates" / "skills"
    skills_dst = target / ".github" / "skills"
    skills_dst.mkdir(parents=True, exist_ok=True)

    # 备份用户自定义文件
    backups = {}
    if skills_dst.exists():
        for pf in PROTECTED_FILES:
            for found in skills_dst.rglob(pf):
                try:
                    content = found.read_text(encoding="utf-8")
                    if content.strip() and len(content.strip()) > 100:
                        rel = str(found.relative_to(skills_dst))
                        backups[rel] = content
                except Exception:
                    pass
        if backups:
            print(f"    🔒 已备份 {len(backups)} 个用户自定义文件")

    count = 0
    for item in sorted(skills_src.iterdir()):
        if not item.is_dir():
            continue
        if not include_examples and item.name == "examples":
            continue

        dst = skills_dst / item.name
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(
            item, dst,
            ignore=shutil.ignore_patterns(*EXCLUDE_PATTERNS),
        )
        count += 1

    # 恢复备份
    for rel_path, content in backups.items():
        target_file = skills_dst / rel_path
        if target_file.exists():
            target_file.write_text(content, encoding="utf-8")

    return count


def copy_agents(pacenote_root: Path, target: Path, agents: list) -> int:
    """复制 Agent 定义到目标项目"""
    github_dir = target / ".github"
    github_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for agent in agents:
        src = pacenote_root / "templates" / agent
        if src.exists():
            shutil.copy2(src, github_dir / agent)
            count += 1
            print(f"    ✅ {agent}")
        else:
            print(f"    ⚠️ 未找到: {agent}")
    return count


def copy_and_configure_instructions(
    pacenote_root: Path,
    target: Path,
    project_info: dict,
) -> None:
    """复制 copilot-instructions.md 并替换所有占位符"""
    src = pacenote_root / "templates" / "copilot-instructions.md"
    dst = target / ".github" / "copilot-instructions.md"
    dst.parent.mkdir(parents=True, exist_ok=True)

    content = src.read_text(encoding="utf-8")

    # ── 替换占位符 ──
    platform_prefix = project_info.get("platform_prefix", "")
    platform_repo = project_info.get("platform_repo", "")

    content = content.replace(
        "{{PLATFORM_PREFIX}}",
        platform_prefix if platform_prefix else "{your-platform}",
    )
    content = content.replace(
        "{{PLATFORM_REPO}}",
        platform_repo if platform_repo else "{your-platform-repo}",
    )

    # ── 处理文档配置段 ──
    docs_section = _build_docs_config_section()
    content = content.replace("{{DOCS_CONFIG_SECTION}}", docs_section)

    # ── 如果没有平台层，软化平台相关措辞 ──
    if not project_info.get("has_platform"):
        content = content.replace(
            "必须参考 `#platform-architecture` 搜索策略，主动搜索",
            "如有平台仓库，参考 `#platform-architecture` 搜索策略，搜索",
        )

    dst.write_text(content, encoding="utf-8")
    print("    ✅ copilot-instructions.md（占位符已替换）")


def replace_tool_repo_path(target: Path, pacenote_path: str) -> int:
    """替换所有已部署 Skill 文件中的 {{TOOL_REPO_PATH}}"""
    skills_dir = target / ".github" / "skills"
    if not skills_dir.exists():
        return 0
    count = 0
    for md_file in skills_dir.rglob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8")
            if "{{TOOL_REPO_PATH}}" in content:
                content = content.replace("{{TOOL_REPO_PATH}}", pacenote_path)
                md_file.write_text(content, encoding="utf-8")
                count += 1
        except Exception:
            pass
    return count


def _build_docs_config_section() -> str:
    """生成文档配置段落"""
    docs_base = ".github/copilot-resources/docs"
    return "\n".join([
        f"| 文档 | 路径 | 状态 |",
        f"|------|------|------|",
        f"| 检查清单 | `{docs_base}/checklist.md` | 待填充 |",
        f"| 功能模块 | `{docs_base}/modules.md` | 待填充 |",
        f"| 功能依赖 | `{docs_base}/dependencies.md` | 待填充 |",
        f"",
        f"> 💡 使用 `@ProjectSetup` 或 `#app-skill-wizard` 自动生成以上文档。",
        f"> 每个占位文件内都有 AI 提示词，复制给 Copilot 即可填充。",
    ])


def setup_project_docs(target: Path) -> None:
    """创建项目文档目录和占位文件（每个文件内置 AI 填充提示词）"""
    docs_dir = target / ".github" / "copilot-resources" / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    placeholders = {
        "checklist.md": (
            "# 需求检查清单\n\n"
            "> 📋 **此文件待填充**。复制下方提示词发给 Copilot 即可自动生成：\n>\n"
            "> ```\n"
            "> 请帮我生成项目的需求检查清单。\n"
            "> 格式参考 .github/skills/_templates/project-requirement-checklist.md 模板。\n"
            "> 请先扫描当前工作区目录结构识别功能模块，然后为每个模块生成特有检查项。\n"
            "> ```\n"
        ),
        "modules.md": (
            "# 功能模块清单\n\n"
            "> 📋 **此文件待填充**。复制下方提示词发给 Copilot 即可自动生成：\n>\n"
            "> ```\n"
            "> 请帮我生成项目的功能模块清单。\n"
            "> 格式参考 .github/skills/_templates/project-module-list.md 模板。\n"
            "> 请扫描当前工作区代码，识别所有功能模块，填写中文名、英文标识、触发关键词。\n"
            "> ```\n"
        ),
        "dependencies.md": (
            "# 功能依赖关系\n\n"
            "> 📋 **此文件待填充**。复制下方提示词发给 Copilot 即可自动生成：\n>\n"
            "> ```\n"
            "> 请帮我生成项目的功能依赖关系文档。\n"
            "> 格式参考 .github/skills/_templates/project-dependency-matrix.md 模板。\n"
            "> 请分析代码中的 import/引用关系，生成依赖矩阵和高风险依赖链。\n"
            "> ```\n"
        ),
    }

    for filename, content in placeholders.items():
        filepath = docs_dir / filename
        if not filepath.exists():
            filepath.write_text(content, encoding="utf-8")
            print(f"    ✅ {filepath.relative_to(target)}")
        else:
            print(f"    ⏭️ 已存在: {filepath.relative_to(target)}")


def count_remaining_placeholders(target: Path) -> list:
    """检查部署产物中是否还有未替换的占位符"""
    issues = []
    instructions = target / ".github" / "copilot-instructions.md"
    if instructions.exists():
        content = instructions.read_text(encoding="utf-8")
        matches = re.findall(r'\{\{[A-Z_]+\}\}', content)
        for m in set(matches):
            issues.append(f"copilot-instructions.md 中残留占位符: {m}")

    # 检查 Skills 中的 TOOL_REPO_PATH
    skills_dir = target / ".github" / "skills"
    if skills_dir.exists():
        for md_file in skills_dir.rglob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8")
                if "{{TOOL_REPO_PATH}}" in content:
                    rel = md_file.relative_to(target)
                    issues.append(f"{rel} 中残留占位符: {{{{TOOL_REPO_PATH}}}}")
            except Exception:
                pass
    return issues


# ─── 主流程 ─────────────────────────────────────────────────

TOTAL_STEPS = 6


def main():
    parser = argparse.ArgumentParser(
        description="PaceNote 项目配置工具 — 一站式部署到你的项目",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例:\n"
            "  python setup_project.py --target /path/to/project\n"
            "  python setup_project.py --target /path/to/project --non-interactive\n"
        ),
    )
    parser.add_argument("--target", "-t", type=str, help="目标项目根目录路径")
    parser.add_argument("--non-interactive", action="store_true", help="非交互模式")
    args = parser.parse_args()

    pacenote_root = get_pacenote_root()

    # ─── 欢迎 ───
    print()
    print("  ╔══════════════════════════════════════════════╗")
    print("  ║  🎯 PaceNote — 项目配置向导                  ║")
    print("  ║  从需求到代码，全链路 AI 辅助研发管线          ║")
    print("  ╚══════════════════════════════════════════════╝")
    print()

    # ─── Step 0: 确定目标 ───
    target_str = args.target
    if not target_str:
        target_str = prompt_input("目标项目路径（你自己的项目根目录）")

    if not target_str:
        print("  ❌ 请指定目标项目路径")
        sys.exit(1)

    target = Path(target_str).resolve()
    if not target.exists():
        print(f"  ❌ 目录不存在: {target}")
        sys.exit(1)

    print(f"\n  📂 目标项目: {target}")

    # ─── Step 1: 收集项目信息 ───
    print_header(1, TOTAL_STEPS, "收集项目信息")
    project_info = collect_project_info(args.non_interactive)

    print_box([
        f"项目名称:   {project_info['project_name']}",
        f"有平台层:   {'是' if project_info['has_platform'] else '否'}",
        f"平台前缀:   {project_info['platform_prefix'] or '(无)'}",
        f"平台仓库:   {project_info['platform_repo'] or '(无)'}",
    ], title="项目信息确认")

    if not args.non_interactive:
        if not prompt_yes_no("信息正确吗？", default=True):
            print("  请重新运行脚本")
            sys.exit(0)

    # ─── Step 2: 部署 Skills ───
    print_header(2, TOTAL_STEPS, "部署 Skills")
    include_examples = True
    if not args.non_interactive:
        include_examples = prompt_yes_no("包含示例域专家（shopping-cart-expert）？")

    skill_count = copy_skills(pacenote_root, target, include_examples)
    print(f"    ✅ 已部署 {skill_count} 个 Skills")

    # ─── Step 3: 部署 Agent 定义 ───
    print_header(3, TOTAL_STEPS, "部署 Agent 定义")
    available_agents = [
        ("GuidedDev.agent.md", "引导式三阶段管线（需求→设计→编码）"),
        ("PlanPlus.agent.md", "规划+执行通用 Agent"),
        ("ProjectSetup.agent.md", "新项目接入，填充领域知识"),
    ]
    agents_to_copy = [a[0] for a in available_agents]

    if not args.non_interactive:
        print("  可用 Agent:")
        for i, (name, desc) in enumerate(available_agents, 1):
            print(f"    {i}. {name} — {desc}")
        selection = prompt_input("选择（逗号分隔，如 1,2,3）", "1,2,3")
        indices = [int(x.strip()) - 1 for x in selection.split(",") if x.strip().isdigit()]
        agents_to_copy = [available_agents[i][0] for i in indices if 0 <= i < len(available_agents)]

    copy_agents(pacenote_root, target, agents_to_copy)

    # ─── Step 4: 部署并配置 Copilot 指令 ───
    print_header(4, TOTAL_STEPS, "部署 Copilot 指令（自动替换占位符）")
    copy_and_configure_instructions(pacenote_root, target, project_info)

    # 同时复制需求评审文档模板
    review_src = pacenote_root / "templates" / "pbi-review-document.md"
    if review_src.exists():
        review_dst = target / ".github" / "pbi-review-document.md"
        shutil.copy2(review_src, review_dst)
        print("    ✅ pbi-review-document.md")

    # ─── Step 4b: 替换 Skills 中的工具仓库路径 ───
    pacenote_path = project_info.get("pacenote_path", str(pacenote_root))
    replaced = replace_tool_repo_path(target, pacenote_path)
    if replaced:
        print(f"    ✅ 已替换 {replaced} 个文件中的工具仓库路径")

    # ─── Step 5: 创建项目文档结构 ───
    print_header(5, TOTAL_STEPS, "创建项目文档结构（含 AI 填充提示）")
    setup_project_docs(target)

    # ─── Step 6: 验证 ───
    print_header(6, TOTAL_STEPS, "验证部署")

    checks = [
        (target / ".github" / "skills", "Skills 目录"),
        (target / ".github" / "copilot-instructions.md", "Copilot 指令"),
        (target / ".github" / "GuidedDev.agent.md", "GuidedDev Agent"),
    ]
    for path, name in checks:
        exists = path.exists()
        status = "✅" if exists else "❌"
        print(f"    {status} {name}")

    issues = count_remaining_placeholders(target)
    if issues:
        for issue in issues:
            print(f"    ⚠️ {issue}")
    else:
        print("    ✅ 占位符已全部替换")

    # ─── 完成 ───
    print()
    print("  ╔══════════════════════════════════════════════╗")
    print("  ║  ✅ 部署完成！                               ║")
    print("  ╚══════════════════════════════════════════════╝")
    print()
    print("  ┌─ 🚀 接下来做什么（3 步即可开始使用）──────────┐")
    print("  │                                                │")
    print("  │  Step A: 用 VS Code 打开你的项目               │")
    print(f"  │    code \"{target}\"")
    print("  │                                                │")
    print("  │  Step B: 在 Copilot Chat 中填充领域知识        │")
    print("  │    输入: @ProjectSetup 帮我完成项目接入         │")
    print("  │    （AI 会引导你完成: 平台架构→域专家→文档）    │")
    print("  │                                                │")
    print("  │  Step C: 开始使用三阶段管线                    │")
    print("  │    输入: @GuidedDev 帮我分析这个需求: [需求]    │")
    print("  │                                                │")
    print("  │  💡 不确定从哪开始？输入: #workflow-router      │")
    print("  │                                                │")
    print("  └────────────────────────────────────────────────┘")
    print()


if __name__ == "__main__":
    main()
