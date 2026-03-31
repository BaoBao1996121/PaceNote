#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Skill 验证脚本

检查所有 Skill 的格式和完整性：
- frontmatter 必填字段
- 引用的依赖 Skill 是否存在
- 参考文件是否存在
- 触发词是否定义

使用方法:
    python lint_skills.py                    # 验证所有 Skill
    python lint_skills.py --skill pbi-reviewer  # 验证指定 Skill
    python lint_skills.py --fix              # 尝试自动修复简单问题

遵循 AI 友好编码规范：
- 类型注解
- 详细文档注释
- 单一职责原则
"""

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set
import yaml

# 兼容 GBK 终端（中文 Windows PowerShell 5.1）
try:
    sys.stdout.reconfigure(errors="replace")
    sys.stderr.reconfigure(errors="replace")
except AttributeError:
    pass  # Python < 3.7


@dataclass
class LintError:
    """验证错误
    
    Attributes:
        skill_name: Skill 名称
        severity: 严重程度 (error/warning/info)
        message: 错误信息
        fix_hint: 修复建议
    """
    skill_name: str
    severity: str
    message: str
    fix_hint: str = ""
    
    def __str__(self) -> str:
        icon = {'error': '❌', 'warning': '⚠️', 'info': 'ℹ️'}.get(self.severity, '?')
        result = f"{icon} [{self.skill_name}] {self.message}"
        if self.fix_hint:
            result += f"\n   💡 {self.fix_hint}"
        return result


@dataclass
class LintResult:
    """验证结果
    
    Attributes:
        errors: 错误列表
        warnings: 警告列表
        info: 信息列表
        passed: 是否通过（无错误）
    """
    errors: List[LintError] = field(default_factory=list)
    warnings: List[LintError] = field(default_factory=list)
    info: List[LintError] = field(default_factory=list)
    
    @property
    def passed(self) -> bool:
        return len(self.errors) == 0
    
    def add(self, error: LintError) -> None:
        if error.severity == 'error':
            self.errors.append(error)
        elif error.severity == 'warning':
            self.warnings.append(error)
        else:
            self.info.append(error)
    
    def print_summary(self) -> None:
        total = len(self.errors) + len(self.warnings) + len(self.info)
        print(f"\n=== 验证结果 ===")
        print(f"总计: {total} 条问题")
        print(f"  ❌ 错误: {len(self.errors)}")
        print(f"  ⚠️ 警告: {len(self.warnings)}")
        print(f"  ℹ️ 信息: {len(self.info)}")
        
        if self.passed:
            print("\n✅ 验证通过！")
        else:
            print("\n❌ 验证失败，请修复错误")


def parse_frontmatter(content: str) -> Optional[Dict]:
    """解析 YAML frontmatter"""
    match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return None
    
    try:
        return yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None


def extract_triggers(frontmatter: Dict) -> List[str]:
    """从 frontmatter 提取触发词列表
    
    优先使用 triggers 字段，否则从 description 中解析 "触发词: ..." 行。
    
    Args:
        frontmatter: 解析后的 YAML frontmatter
    
    Returns:
        去重后的触发词列表（保持原始大小写）
    """
    triggers = frontmatter.get('triggers', [])
    if triggers:
        return [t.strip() for t in triggers if t.strip()]
    
    description = frontmatter.get('description', '')
    if description:
        match = re.search(r'触发(?:关键)?词[:：]\s*(.+?)(?:\n|$)', description)
        if match:
            return [t.strip() for t in re.split(r'[,，、\s]+', match.group(1)) if t.strip()]
    
    return []


def get_all_skill_names(skills_dir: Path) -> Set[str]:
    """获取所有 Skill 名称
    
    Args:
        skills_dir: Skills 目录
    
    Returns:
        Skill 名称集合
    """
    names = set()
    for skill_path in skills_dir.iterdir():
        if skill_path.is_dir() and not skill_path.name.startswith('_'):
            names.add(skill_path.name)
    return names


def lint_skill(skill_path: Path, all_skill_names: Set[str]) -> List[LintError]:
    """验证单个 Skill
    
    Args:
        skill_path: Skill 目录路径
        all_skill_names: 所有 Skill 名称集合
    
    Returns:
        错误列表
    """
    errors = []
    skill_name = skill_path.name
    
    # 1. 检查 SKILL.md 存在
    skill_file = skill_path / "SKILL.md"
    if not skill_file.exists():
        errors.append(LintError(
            skill_name=skill_name,
            severity='error',
            message='缺少 SKILL.md 文件',
            fix_hint='创建 SKILL.md 并添加 frontmatter'
        ))
        return errors
    
    # 2. 解析 frontmatter
    try:
        content = skill_file.read_text(encoding='utf-8')
    except Exception as e:
        errors.append(LintError(
            skill_name=skill_name,
            severity='error',
            message=f'无法读取文件: {e}'
        ))
        return errors
    
    frontmatter = parse_frontmatter(content)
    if frontmatter is None:
        errors.append(LintError(
            skill_name=skill_name,
            severity='error',
            message='缺少 YAML frontmatter 或格式错误',
            fix_hint='在文件开头添加 --- ... --- 格式的 YAML'
        ))
        return errors
    
    # 3. 检查必填字段
    required_fields = ['name', 'description']
    for field_name in required_fields:
        if not frontmatter.get(field_name):
            errors.append(LintError(
                skill_name=skill_name,
                severity='error',
                message=f'缺少必填字段: {field_name}',
                fix_hint=f'在 frontmatter 中添加 {field_name} 字段'
            ))
    
    # 4. 检查推荐字段
    recommended_fields = ['triggers', 'version', 'last_updated']
    for field_name in recommended_fields:
        if not frontmatter.get(field_name):
            errors.append(LintError(
                skill_name=skill_name,
                severity='warning',
                message=f'缺少推荐字段: {field_name}',
                fix_hint=f'在 frontmatter 中添加 {field_name} 字段以支持自动发现'
            ))
    
    # 5. 检查触发词
    triggers = frontmatter.get('triggers', [])
    description = frontmatter.get('description', '')
    
    # 尝试从 description 提取触发词
    if not triggers and description:
        match = re.search(r'触发(?:关键)?词[:：]\s*(.+?)(?:\n|$)', description)
        if match:
            triggers = [t.strip() for t in re.split(r'[,，\s]+', match.group(1)) if t.strip()]
    
    if not triggers:
        errors.append(LintError(
            skill_name=skill_name,
            severity='warning',
            message='未定义触发词',
            fix_hint='添加 triggers 字段或在 description 中添加 "触发词: ..."'
        ))
    
    # 6. 检查依赖的 Skill 是否存在
    requires = frontmatter.get('requires', [])
    if requires:
        for req in requires:
            if req not in all_skill_names:
                errors.append(LintError(
                    skill_name=skill_name,
                    severity='error',
                    message=f'依赖的 Skill 不存在: {req}',
                    fix_hint=f'检查 requires 中的 "{req}" 是否拼写正确'
                ))
    
    # 7. 检查 references 目录中的文件引用
    references_dir = skill_path / "references"
    if references_dir.exists():
        # 检查 SKILL.md 中引用的文件是否存在
        ref_pattern = re.compile(r'references/([^\s\)]+)')
        for match in ref_pattern.finditer(content):
            ref_file = references_dir / match.group(1).rstrip(')')
            if not ref_file.exists():
                errors.append(LintError(
                    skill_name=skill_name,
                    severity='warning',
                    message=f'引用的文件不存在: references/{match.group(1)}',
                    fix_hint='创建该文件或更正引用路径'
                ))
    
    # 8. 检查名称一致性
    frontmatter_name = frontmatter.get('name', '')
    if frontmatter_name and frontmatter_name != skill_name:
        # 允许不完全匹配，但提示
        if skill_name not in frontmatter_name and frontmatter_name not in skill_name:
            errors.append(LintError(
                skill_name=skill_name,
                severity='info',
                message=f'frontmatter.name ({frontmatter_name}) 与目录名 ({skill_name}) 不一致',
                fix_hint='建议保持一致以避免混淆'
            ))
    
    # 9. 检查版本号格式
    version = frontmatter.get('version', '')
    if version and not re.match(r'^(\d+\.)*\d+|rc-V\d+\.\d+', version):
        errors.append(LintError(
            skill_name=skill_name,
            severity='info',
            message=f'版本号格式不标准: {version}',
            fix_hint='建议使用 x.y.z 格式（如 1.0.0）或 rc-Vx.y 格式'
        ))
    
    return errors


def check_trigger_overlap(skills_dir: Path) -> List[LintError]:
    """检查跨 Skill 触发词重叠
    
    扫描所有 Skill 的触发词，检测:
    - 精确匹配冲突（同一触发词出现在多个 Skill）→ warning
    - 子串包含冲突（一个触发词是另一个的子串）→ info
    
    Args:
        skills_dir: Skills 目录
    
    Returns:
        冲突错误列表
    """
    errors: List[LintError] = []
    
    # 1. 收集所有 Skill 的触发词
    skill_triggers: Dict[str, List[str]] = {}  # skill_name -> [triggers]
    
    for skill_path in skills_dir.iterdir():
        if not skill_path.is_dir() or skill_path.name.startswith('_'):
            continue
        
        skill_file = skill_path / "SKILL.md"
        if not skill_file.exists():
            continue
        
        try:
            content = skill_file.read_text(encoding='utf-8')
        except Exception:
            continue
        
        frontmatter = parse_frontmatter(content)
        if not frontmatter:
            continue
        
        triggers = extract_triggers(frontmatter)
        if triggers:
            skill_triggers[skill_path.name] = triggers
    
    # 2. 精确匹配检测：同一触发词出现在多个 Skill
    trigger_to_skills: Dict[str, List[str]] = {}  # trigger_lower -> [skill_names]
    trigger_original: Dict[str, str] = {}  # trigger_lower -> original_case
    
    for skill_name, triggers in skill_triggers.items():
        for trigger in triggers:
            key = trigger.lower()
            if key not in trigger_to_skills:
                trigger_to_skills[key] = []
                trigger_original[key] = trigger
            trigger_to_skills[key].append(skill_name)
    
    for trigger_lower, skills in trigger_to_skills.items():
        if len(skills) > 1:
            original = trigger_original[trigger_lower]
            skills_str = ' ↔ '.join(sorted(skills))
            errors.append(LintError(
                skill_name=skills_str,
                severity='warning',
                message=f'触发词冲突: "{original}" 同时出现在 {len(skills)} 个 Skill 中',
                fix_hint='从其中一个 Skill 移除该触发词，或用限定词区分语义（如 "TissueControl数据定义" vs "TissueControl操作"）'
            ))
    
    # 3. 子串包含检测（仅检查长度>=3 的短词被长词包含的情况）
    all_triggers_lower = sorted(trigger_to_skills.keys())
    checked_pairs: Set[tuple] = set()
    
    for i, t1 in enumerate(all_triggers_lower):
        if len(t1) < 3:
            continue
        for j, t2 in enumerate(all_triggers_lower):
            if i == j or t1 == t2:
                continue
            # t1 是 t2 的子串（且 t1 != t2）
            if t1 in t2 and len(t1) < len(t2):
                # 检查是否在不同 Skill 中
                skills_t1 = set(trigger_to_skills[t1])
                skills_t2 = set(trigger_to_skills[t2])
                overlapping = skills_t1 & skills_t2
                cross_skills = (skills_t1 - overlapping) & (skills_t2 - overlapping)
                if skills_t1 != skills_t2 and not skills_t1.issubset(skills_t2) and not skills_t2.issubset(skills_t1):
                    pair_key = (min(t1, t2), max(t1, t2))
                    if pair_key not in checked_pairs:
                        checked_pairs.add(pair_key)
                        orig1 = trigger_original[t1]
                        orig2 = trigger_original[t2]
                        s1 = ', '.join(sorted(skills_t1))
                        s2 = ', '.join(sorted(skills_t2))
                        errors.append(LintError(
                            skill_name='(cross-skill)',
                            severity='info',
                            message=f'触发词子串重叠: "{orig1}"({s1}) ⊂ "{orig2}"({s2})',
                            fix_hint='用户输入短词时可能匹配到非预期 Skill，建议使用更具体的触发词'
                        ))
    
    return errors


def lint_all_skills(skills_dir: Path, target_skill: Optional[str] = None) -> LintResult:
    """验证所有 Skill
    
    Args:
        skills_dir: Skills 目录
        target_skill: 指定验证的 Skill（可选）
    
    Returns:
        验证结果
    """
    result = LintResult()
    
    if not skills_dir.exists():
        result.add(LintError(
            skill_name='(global)',
            severity='error',
            message=f'Skills 目录不存在: {skills_dir}'
        ))
        return result
    
    all_skill_names = get_all_skill_names(skills_dir)
    
    for skill_path in skills_dir.iterdir():
        if not skill_path.is_dir():
            continue
        if skill_path.name.startswith('_'):
            continue
        
        # 如果指定了目标 Skill，只验证它
        if target_skill and skill_path.name != target_skill:
            continue
        
        errors = lint_skill(skill_path, all_skill_names)
        for error in errors:
            result.add(error)
    
    # 10. 跨 Skill 触发词重叠检测（全局检查，非单 Skill 维度）
    if not target_skill:  # 仅在全量验证时执行
        overlap_errors = check_trigger_overlap(skills_dir)
        for error in overlap_errors:
            result.add(error)
    
    return result


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='验证 Skill 格式和完整性',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument('--skill', type=str,
                        help='验证指定的 Skill')
    parser.add_argument('--skills-dir', type=str,
                        help='Skills 目录路径（默认自动查找）')
    parser.add_argument('--fix', action='store_true',
                        help='尝试自动修复（暂未实现）')
    parser.add_argument('--quiet', action='store_true',
                        help='仅显示错误，不显示警告和信息')
    
    args = parser.parse_args()
    
    # 确定路径
    script_dir = Path(__file__).parent.parent
    
    if args.skills_dir:
        skills_dir = Path(args.skills_dir)
    else:
        skills_dir = script_dir / "templates" / "skills"
    
    print(f"验证目录: {skills_dir}")
    
    if args.skill:
        print(f"目标 Skill: {args.skill}")
    
    # 执行验证
    result = lint_all_skills(skills_dir, target_skill=args.skill)
    
    # 输出结果
    if result.errors:
        print("\n=== 错误 ===")
        for error in result.errors:
            print(error)
    
    if result.warnings and not args.quiet:
        print("\n=== 警告 ===")
        for warning in result.warnings:
            print(warning)
    
    if result.info and not args.quiet:
        print("\n=== 信息 ===")
        for info in result.info:
            print(info)
    
    result.print_summary()
    
    # 返回码
    sys.exit(0 if result.passed else 1)


if __name__ == '__main__':
    main()
