"""CLI 自动部署 Skills 到目标项目

功能：替代 GUI 手动操作，将 Skills 按类别过滤后复制到目标项目
用途：由 app-skill-wizard Step 2 调用，或开发者命令行使用

用法：
    python scripts/deploy_skills.py --target-path "D:\\project" --categories platform,cardiacct
    python scripts/deploy_skills.py --target-path "D:\\project" --categories platform,{{APP_NAME}} --dry-run
    python scripts/deploy_skills.py --list-categories
"""

import argparse
import json
import sys
from pathlib import Path

# 兼容 GBK 终端（中文 Windows PowerShell 5.1）
try:
    sys.stdout.reconfigure(errors="replace")
    sys.stderr.reconfigure(errors="replace")
except AttributeError:
    pass  # Python < 3.7

# 项目根目录
SCRIPT_DIR = Path(__file__).resolve().parent.parent

# ─── 自包含的 Skill 过滤逻辑（不依赖外部模块）───

SKILLS_PROTECTED_FILES = {"experience-notes.md", "bug-patterns.md"}
SKILLS_EXCLUDE_PATTERNS = {"_cleanup-report.md", "*.pyc", "__pycache__"}


def _load_skill_categories(root: Path) -> dict:
    """加载 Skill 分类配置（自包含版本）"""
    # 优先从 data/ 目录读取
    for candidate in [
        root / "data" / "skill_categories.json",
        root / "data" / "skill_categories.example.json",
    ]:
        if candidate.exists():
            with open(candidate, encoding="utf-8") as f:
                return json.load(f)
    return {"categories": {}, "presets": {}}


def _get_prefixes_for_categories(root: Path, categories: list) -> list:
    """获取指定类别的前缀列表"""
    config = _load_skill_categories(root)
    prefixes = []
    # 展开 preset
    expanded = []
    presets = config.get("presets", {})
    for cat in categories:
        if cat in presets:
            preset_cats = presets[cat].get("categories", presets[cat]) if isinstance(presets[cat], dict) else presets[cat]
            expanded.extend(preset_cats if isinstance(preset_cats, list) else [])
        else:
            expanded.append(cat)
    # 收集前缀
    cats_config = config.get("categories", {})
    for cat in expanded:
        if cat in cats_config:
            prefixes.extend(cats_config[cat].get("prefixes", []))
    return prefixes


def _filter_skills(skills_dir: Path, prefixes: list, include_common: bool = True) -> list:
    """按前缀过滤 Skills（自包含版本）"""
    if not skills_dir.exists():
        return []
    result = []
    for item in sorted(skills_dir.iterdir()):
        if not item.is_dir():
            continue
        name = item.name
        # 跳过 _ 开头的目录（模板等）
        if name.startswith("_"):
            if include_common:
                result.append(name)
            continue
        # 匹配前缀
        matched_prefix = any(name.startswith(p) for p in prefixes) if prefixes else False
        # 无前缀匹配 = 通用 Skill
        is_common = not any(
            name.startswith(p)
            for cat_info in _load_skill_categories(skills_dir.parent.parent).get("categories", {}).values()
            for p in cat_info.get("prefixes", [])
            if cat_info.get("prefixes")
        )
        if matched_prefix or (include_common and is_common):
            result.append(name)
    return result


# 向后兼容别名
load_skill_categories = _load_skill_categories
get_skill_prefixes_for_categories = lambda root, cats: _get_prefixes_for_categories(root, cats)
filter_skills_by_categories = lambda skills_dir, prefixes, include_common=True: _filter_skills(skills_dir, prefixes, include_common)


def list_categories() -> None:
    """列出所有可用的 Skill 类别"""
    config = load_skill_categories(SCRIPT_DIR)
    categories = config.get("categories", {})
    presets = config.get("presets", {})

    print("\n📂 可用类别:")
    print(f"  {'ID':<20} {'显示名':<15} {'前缀':<30} {'默认选中'}")
    print(f"  {'─'*20} {'─'*15} {'─'*30} {'─'*8}")
    for cat_id, info in categories.items():
        prefixes = ", ".join(info.get("prefixes", []))
        default = "✅" if info.get("default_selected") else ""
        print(f"  {cat_id:<20} {info.get('display_name', ''):<15} {prefixes:<30} {default}")

    print(f"\n📦 预设组合:")
    for name, cats in presets.items():
        print(f"  {name}: {', '.join(cats)}")

    print(f"\n💡 通用 Skills（无前缀）始终包含，不受 --categories 影响")


def count_skills(skills_dir: Path, included: list[str]) -> dict:
    """统计 Skill 信息"""
    stats = {"total": len(included), "by_prefix": {}}
    for name in included:
        matched = False
        config = load_skill_categories(SCRIPT_DIR)
        for cat_id, info in config.get("categories", {}).items():
            for prefix in info.get("prefixes", []):
                if name.startswith(prefix):
                    stats["by_prefix"].setdefault(cat_id, 0)
                    stats["by_prefix"][cat_id] += 1
                    matched = True
                    break
            if matched:
                break
        if not matched:
            stats["by_prefix"].setdefault("common", 0)
            stats["by_prefix"]["common"] += 1
    return stats


def deploy_skills(target_path: Path, categories: list[str],
                  dry_run: bool = False, force: bool = False) -> bool:
    """部署 Skills 到目标项目

    Args:
        target_path: 目标项目根路径
        categories: 选中的类别 ID 列表
        dry_run: 仅预览不执行
        force: 跳过确认直接覆盖

    Returns:
        是否成功
    """
    skills_source = SCRIPT_DIR / "templates" / "skills"
    skills_target = target_path / ".github" / "skills"

    if not skills_source.exists():
        print(f"❌ 源目录不存在: {skills_source}")
        return False

    if not target_path.exists():
        print(f"❌ 目标项目不存在: {target_path}")
        return False

    # 获取选中类别的前缀
    prefixes = get_skill_prefixes_for_categories(SCRIPT_DIR, categories)
    print(f"\n🔧 部署配置:")
    print(f"  源目录: {skills_source}")
    print(f"  目标:   {skills_target}")
    print(f"  类别:   {', '.join(categories)}")
    print(f"  前缀:   {', '.join(prefixes) if prefixes else '(无，仅通用 Skills)'}")

    # 过滤 Skills
    included = filter_skills_by_categories(skills_source, prefixes, include_common=True)
    if not included:
        print("⚠️ 未找到匹配的 Skills")
        return False

    stats = count_skills(skills_source, included)
    print(f"\n📋 将部署 {stats['total']} 个 Skills:")
    for cat, count in stats["by_prefix"].items():
        print(f"  {cat}: {count}")

    if dry_run:
        print("\n🔍 [DRY RUN] 将复制以下 Skills:")
        for name in sorted(included):
            print(f"  📁 {name}")
        print("\n🔍 [DRY RUN] 实际未执行任何操作")
        return True

    # 确认覆盖
    if skills_target.exists() and not force:
        print(f"\n⚠️ 目标目录已存在: {skills_target}")
        response = input("是否覆盖？(y/N): ").strip().lower()
        if response != "y":
            print("已取消")
            return False

    # 备份受保护文件
    import shutil
    import fnmatch
    backups = {}
    if skills_target.exists():
        for protected_name in SKILLS_PROTECTED_FILES:
            for found_file in skills_target.rglob(protected_name):
                try:
                    content = found_file.read_text(encoding="utf-8")
                    if content.strip() and len(content.strip()) > 100:
                        rel_path = str(found_file.relative_to(skills_target))
                        backups[rel_path] = content
                except Exception:
                    pass
        if backups:
            print(f"  🔒 已备份 {len(backups)} 个受保护文件")
        # 清理目标目录
        shutil.rmtree(skills_target)

    # 创建目标目录并复制
    skills_target.mkdir(parents=True, exist_ok=True)
    copied = 0
    for skill_name in included:
        src = skills_source / skill_name
        dst = skills_target / skill_name
        if src.is_dir():
            shutil.copytree(src, dst)
            copied += 1

    # 恢复受保护文件
    restored = 0
    for rel_path, content in backups.items():
        target_file = skills_target / rel_path
        target_file.parent.mkdir(parents=True, exist_ok=True)
        should_restore = False
        if not target_file.exists():
            should_restore = True
        else:
            try:
                new_content = target_file.read_text(encoding="utf-8")
                if len(new_content.strip()) < 100 and len(content.strip()) >= 100:
                    should_restore = True
                elif len(content.strip()) >= 100:
                    should_restore = True
            except Exception:
                should_restore = True
        if should_restore:
            target_file.write_text(content, encoding="utf-8")
            restored += 1
    if restored:
        print(f"  🔒 已恢复 {restored} 个受保护文件")

    # 复制 _templates/module-expert-skill.md
    template_src = skills_source / "_templates" / "module-expert-skill.md"
    if template_src.exists():
        template_dir = skills_target / "_templates"
        template_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(template_src, template_dir / "module-expert-skill.md")

    # 复制 README.md
    readme_src = skills_source / "README.md"
    if readme_src.exists():
        shutil.copy2(readme_src, skills_target / "README.md")

    print(f"\n✅ 部署完成: {copied} 个 Skills 已复制到 {skills_target}")
    print(f"💡 请在目标项目 VS Code 中执行 Ctrl+Shift+P → Reload Window 使 Skills 生效")
    return True


def main() -> None:
    """CLI 入口"""
    parser = argparse.ArgumentParser(
        description="将 Skills 按类别部署到目标项目",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="示例:\n"
               "  python deploy_skills.py --target-path D:\\project --categories platform,cardiacct\n"
               "  python deploy_skills.py --list-categories\n"
               "  python deploy_skills.py --target-path D:\\project --categories platform --dry-run",
    )
    parser.add_argument(
        "--target-path", type=str,
        help="目标项目根路径",
    )
    parser.add_argument(
        "--categories", type=str,
        help="逗号分隔的类别 ID（如 platform,{{APP_NAME}}）",
    )
    parser.add_argument(
        "--list-categories", action="store_true",
        help="列出所有可用类别并退出",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="仅预览将复制哪些 Skills，不执行",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="跳过确认直接覆盖",
    )

    args = parser.parse_args()

    if args.list_categories:
        list_categories()
        return

    if not args.target_path:
        parser.error("--target-path 是必需参数（除非使用 --list-categories）")
    if not args.categories:
        parser.error("--categories 是必需参数（除非使用 --list-categories）")

    target = Path(args.target_path).resolve()
    cats = [c.strip() for c in args.categories.split(",") if c.strip()]

    success = deploy_skills(target, cats, dry_run=args.dry_run, force=args.force)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
