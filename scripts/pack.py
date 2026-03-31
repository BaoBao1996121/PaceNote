#!/usr/bin/env python3
"""
PaceNote 飞书传输打包工具 v3

终极方案：接收端只需创建 2 个文件（restore.py + data.txt），运行 1 条命令。
- tar.xz 跨文件压缩（比 ZIP 小 40%）
- 每块 ≤19K 字符（飞书安全上限）
- 接收端无需创建 chunks 目录，所有数据合并到一个 data.txt

用法:
    python scripts/pack.py

产出:
    _transfer/
    ├── restore.py          # 第 1 条消息（自包含还原脚本）
    ├── part_01.txt ~ NN    # 第 2 条消息起（依次粘贴到 data.txt 中）
    └── manifest.txt        # 传输清单
"""

import argparse
import base64
import hashlib
import io
import sys
import tarfile
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, OSError):
    pass

CHUNK_SIZE = 19000
SKIP_DIRS = {"__pycache__", ".git", "_transfer", "_restore_test", "node_modules"}
SKIP_EXTS = {".pyc", ".pyo", ".exe", ".dll", ".so"}


def get_pacenote_root() -> Path:
    return Path(__file__).resolve().parent.parent


def build_tar_xz(root: Path) -> tuple[bytes, int]:
    """tar.xz 跨文件压缩"""
    buf = io.BytesIO()
    count = 0
    with tarfile.open(fileobj=buf, mode="w:xz", preset=9) as tf:
        for f in sorted(root.rglob("*")):
            if not f.is_file():
                continue
            parts = f.relative_to(root).parts
            if any(d in SKIP_DIRS for d in parts):
                continue
            if f.suffix in SKIP_EXTS:
                continue
            tf.add(f, f.relative_to(root))
            count += 1
    return buf.getvalue(), count


# ── restore.py 内容 ──
# 接收端只需：
#   1. 保存 restore.py
#   2. 按顺序把所有 base64 文本粘贴到同一个 data.txt
#   3. python restore.py
RESTORE_SCRIPT = r'''#!/usr/bin/env python3
"""
PaceNote 还原脚本

操作步骤:
  1. 将此脚本保存为 restore.py
  2. 在同目录下创建 data.txt
  3. 把飞书收到的所有 base64 文本块按顺序粘贴到 data.txt 中
     （直接一段接一段粘贴，不需要分隔符，中间有空行也没关系）
  4. 运行: python restore.py
"""

import base64, hashlib, io, sys, tarfile
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, OSError):
    pass

def main():
    here = Path(__file__).resolve().parent
    data_file = here / "data.txt"
    output = here / "PaceNote"

    if not data_file.exists():
        print("  [X] data.txt not found!")
        print("      Create data.txt in the same folder as this script,")
        print("      paste ALL base64 text blocks into it (in order), then re-run.")
        sys.exit(1)

    raw_text = data_file.read_text(encoding="utf-8-sig")  # handle BOM
    b64_clean = "".join(raw_text.split())  # strip ALL whitespace
    print(f"  [*] data.txt: {len(b64_clean)} chars (cleaned)")

    try:
        archive = base64.b64decode(b64_clean)
    except Exception as e:
        print(f"  [X] Base64 decode failed: {e}")
        print("      Check that data.txt is complete and in correct order.")
        sys.exit(1)

    md5 = hashlib.md5(archive).hexdigest()
    print(f"  [*] MD5: {md5}")

    output.mkdir(parents=True, exist_ok=True)
    try:
        with tarfile.open(fileobj=io.BytesIO(archive), mode="r:xz") as tf:
            members = [m for m in tf.getmembers() if m.isfile()]
            tf.extractall(output, filter="data")
    except Exception as e:
        print(f"  [X] Extract failed: {e}")
        sys.exit(1)

    print(f"\n  [OK] Restored {len(members)} files -> {output}/")
    print(f"  [OK] MD5: {md5}")
    print(f"\n  Next steps:")
    print(f"    python PaceNote/scripts/setup_project.py --target YOUR_PROJECT")
    print(f"    Then in VS Code: @ProjectSetup")

if __name__ == "__main__":
    main()
'''


def main():
    root = get_pacenote_root()
    transfer_dir = root / "_transfer"
    transfer_dir.mkdir(exist_ok=True)

    print("\n  === PaceNote Pack (tar.xz) ===\n")

    archive, file_count = build_tar_xz(root)
    md5 = hashlib.md5(archive).hexdigest()
    b64 = base64.b64encode(archive).decode("ascii")
    parts = [b64[i:i + CHUNK_SIZE] for i in range(0, len(b64), CHUNK_SIZE)]

    print(f"  {file_count} files -> {len(archive)/1024:.1f} KB (tar.xz)")
    print(f"  Base64: {len(b64)/1024:.1f} KB -> {len(parts)} parts @ {CHUNK_SIZE} chars")
    print(f"  MD5: {md5}")

    # 写入 restore.py
    (transfer_dir / "restore.py").write_text(RESTORE_SCRIPT, encoding="utf-8")

    # 写入分块文件（方便逐条复制发送）
    for i, part in enumerate(parts, 1):
        (transfer_dir / f"part_{i:02d}.txt").write_text(part, encoding="utf-8")

    # 清理旧文件
    for old in transfer_dir.glob("part_*.txt"):
        num = int(old.stem.split("_")[1])
        if num > len(parts):
            old.unlink()
    for old in transfer_dir.glob("chunk_*.txt"):
        old.unlink()

    # 传输清单
    lines = [
        f"# PaceNote Transfer Manifest",
        f"# {__import__('datetime').datetime.now().isoformat()}",
        f"# Files: {file_count} | tar.xz: {len(archive)/1024:.1f}KB | MD5: {md5}",
        "",
        "## How to Send (Lark Messages)",
        "",
        f"  Msg 1: restore.py ({len(RESTORE_SCRIPT)} chars)",
    ]
    for i, part in enumerate(parts, 1):
        lines.append(f"  Msg {i+1}: part_{i:02d}.txt ({len(part)} chars)")
    lines.extend([
        "",
        "## How to Receive",
        "",
        "  1. Save restore.py",
        "  2. Create data.txt, paste ALL part texts into it (in order)",
        "  3. Run: python restore.py",
        f"  4. Verify MD5: {md5}",
    ])
    (transfer_dir / "manifest.txt").write_text("\n".join(lines), encoding="utf-8")

    # 输出操作指引
    print(f"\n  === Output: {transfer_dir} ===\n")
    print(f"  SEND ORDER ({len(parts) + 1} Lark messages):")
    print(f"    Msg 1: restore.py  ({len(RESTORE_SCRIPT)} chars)")
    for i, part in enumerate(parts, 1):
        print(f"    Msg {i+1}: part_{i:02d}.txt  ({len(part)} chars)")
    print()
    print("  RECEIVE (only 2 files + 1 command):")
    print("    1. Save Msg 1 as -> restore.py")
    print(f"    2. Paste Msg 2~{len(parts)+1} ALL into -> data.txt")
    print("    3. Run: python restore.py")
    print()


if __name__ == "__main__":
    main()
