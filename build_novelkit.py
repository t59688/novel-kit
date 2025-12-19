#!/usr/bin/env python3
"""
NovelKit build script

作用：
- 将 NovelKit 元项目（`novelkit/` 目录）构建为可发布的包
- 目前只支持目标 AI = cursor，其它 AI 先标记为 TODO
- 目标平台参数目前只体现在输出目录结构上（如 dist/cursor-linux 或 dist/cursor-win）

输出目录结构（相对于仓库根目录 `./`）：

dist/
  cursor-linux/                 # 或 cursor-win / 未来可能是 claude-linux 等
    .novelkit/                  # 元空间模板（发布包内的初始结构）
      memory/
        config.json             # 初始状态机（从 ./memory/config.json 复制）
      templates/                # 从 ./templates/ 复制
      scripts/                  # 从 ./scripts/ 复制
      writers/                  # 空目录（运行时由命令生成）
      chapters/                 # 空目录（运行时由命令生成）
    .cursor/
      commands/
        novel.writer.new.md
        novel.writer.list.md
        ...

使用示例：
    python -m novelkit.build cursor linux
    python ./build.py cursor win
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path


def load_build_config() -> tuple[set[str], set[str]]:
    """从 build-config.json 加载构建配置"""
    config_path = Path(__file__).parent / "build-config.json"
    if not config_path.exists():
        # 默认配置（向后兼容）
        return {"cursor"}, {"linux", "win"}
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    supported_ais = set(config.get("supported_ais", ["cursor"]))
    supported_platforms = set(config.get("supported_platforms", ["linux", "win"]))
    
    return supported_ais, supported_platforms


SUPPORTED_AIS, SUPPORTED_PLATFORMS = load_build_config()


def find_repo_root() -> Path:
    """
    仓库根目录 = build.py 所在的目录
    """
    here = Path(__file__).resolve()
    repo_root = here.parent
    # Check for a key directory to validate root
    if not (repo_root / "commands").is_dir():
        print(f"Error: could not find 'commands' directory in {repo_root}", file=sys.stderr)
        sys.exit(1)
    return repo_root


def copy_tree(src: Path, dst: Path) -> None:
    """递归复制目录（允许目标已存在）。"""
    if not src.exists():
        return
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        target = dst / item.name
        if item.is_dir():
            copy_tree(item, target)
        else:
            shutil.copy2(item, target)


def build_for_cursor(repo_root: Path, platform: str) -> Path:
    """
    构建 cursor 目标的发布包。

    :param repo_root: 仓库根目录（与 ./ 同级）
    :param platform:  平台标识（linux / win）
    :return:          构建输出目录路径
    """
    # 目录命名规则：dist/cursor-linux、dist/cursor-win
    dist_root = repo_root / "dist" / f"cursor-{platform}"

    # 1. 准备目标目录
    meta_target = dist_root / ".novelkit"
    commands_target = dist_root / ".cursor" / "commands"

    # 清理旧产物（如果存在）
    if dist_root.exists():
        shutil.rmtree(dist_root)

    meta_target.mkdir(parents=True, exist_ok=True)
    commands_target.mkdir(parents=True, exist_ok=True)

    # 2. 复制 .novelkit 内容
    # 2.1 memory/config.json（初始状态机模板）
    src_config = repo_root / "memory" / "config.json"
    memory_target = meta_target / "memory"
    memory_target.mkdir(parents=True, exist_ok=True)
    if src_config.is_file():
        shutil.copy2(src_config, memory_target / "config.json")
    else:
        print(
            "Warning: ./memory/config.json not found, "
            "memory/config.json will be missing in package.",
            file=sys.stderr,
        )

    # 2.2 templates/
    src_templates = repo_root / "templates"
    copy_tree(src_templates, meta_target / "templates")

    # 2.3 scripts/（只复制指定平台的脚本）
    scripts_target = meta_target / "scripts"
    scripts_target.mkdir(parents=True, exist_ok=True)
    
    if platform == "linux":
        # Linux 平台：只复制 bash 脚本
        src_bash = repo_root / "scripts" / "bash"
        if src_bash.is_dir():
            copy_tree(src_bash, scripts_target / "bash")
        else:
            print(
                f"Warning: ./scripts/bash not found for platform '{platform}'.",
                file=sys.stderr,
            )
    elif platform == "win":
        # Windows 平台：只复制 PowerShell 脚本
        src_powershell = repo_root / "scripts" / "powershell"
        if src_powershell.is_dir():
            copy_tree(src_powershell, scripts_target / "powershell")
        else:
            print(
                f"Warning: ./scripts/powershell not found for platform '{platform}'.",
                file=sys.stderr,
            )
    else:
        print(
            f"Warning: Unknown platform '{platform}', skipping scripts copy.",
            file=sys.stderr,
        )

    # 注意：writers/ 和 chapters/ 目录不需要在构建时创建
    # 它们会在运行时由脚本自动创建：
    # - writers/ 由 writer-manager.sh 创建（第35行：mkdir -p "$WRITERS_DIR"）
    # - chapters/ 由 chapter-manager.sh 创建（第37行：mkdir -p "$CHAPTERS_META_DIR"）

    # 3. 复制命令到 .cursor/commands 并重命名
    src_commands = repo_root / "commands"
    if not src_commands.is_dir():
        print(
            "Warning: ./commands not found, no commands will be packaged.",
            file=sys.stderr,
        )
    else:
        for cmd_file in src_commands.glob("*.md"):
            new_name = to_cursor_command_name(cmd_file.name)
            shutil.copy2(cmd_file, commands_target / new_name)

    return dist_root


def to_cursor_command_name(src_name: str) -> str:
    """
    将 ./commands 下的文件名转换为 Cursor 所需的命令名。

    规则：
    - 去掉扩展名，按 `-` 分割
    - 如果前缀是 `novel-`，先去掉 `novel-`
    - 最终格式：novel.<part1>.<part2>... + .md

    例：
    - writer-new.md           -> novel.writer.new.md
    - writer-list.md          -> novel.writer.list.md
    - constitution-create.md  -> novel.constitution.create.md
    - chapter-plan.md         -> novel.chapter.plan.md
    - novel-setup.md          -> novel.setup.md
    """
    base = src_name
    if base.lower().endswith(".md"):
        base = base[:-3]

    # 去掉前缀 novel-
    lower = base.lower()
    if lower.startswith("novel-"):
        base = base[len("novel-") :]

    parts = base.split("-")
    parts = [p for p in parts if p]  # 去掉空

    if not parts:
        # 极端情况：fallback 原名
        return src_name

    new_base = "novel." + ".".join(parts)
    return new_base + ".md"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build NovelKit distribution packages.")
    parser.add_argument(
        "ai",
        help=f"目标 AI（支持: {', '.join(sorted(SUPPORTED_AIS))}, 或 'all' 构建所有）",
        nargs="?",
        default="cursor",
    )
    parser.add_argument(
        "platform",
        help=f"目标平台（{', '.join(sorted(SUPPORTED_PLATFORMS))}），使用 'all' 时忽略此参数",
        nargs="?",
        default="linux",
    )
    return parser.parse_args(argv)


def build_all(repo_root: Path) -> list[Path]:
    """
    构建所有支持的 AI 环境和平台组合。
    
    Returns:
        构建输出目录列表
    """
    output_dirs = []
    for ai in SUPPORTED_AIS:
        for platform in SUPPORTED_PLATFORMS:
            if ai == "cursor":
                out_dir = build_for_cursor(repo_root, platform)
            else:
                # 未来添加其他 AI 环境时，在这里添加对应的构建函数调用
                print(f"Warning: AI '{ai}' build function not implemented yet.", file=sys.stderr)
                continue
            output_dirs.append(out_dir)
            print(f"Built NovelKit package for ai='{ai}', platform='{platform}' at: {out_dir}")
    return output_dirs


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    args = parse_args(argv)
    ai = args.ai.lower()
    platform = args.platform.lower()

    # 特殊处理：如果 ai 为 "all"，构建所有支持的 AI 环境
    if ai == "all":
        repo_root = find_repo_root()
        output_dirs = build_all(repo_root)
        if not output_dirs:
            print("Error: No packages were built.", file=sys.stderr)
            return 1
        return 0

    if ai not in SUPPORTED_AIS:
        print(f"TODO: AI '{ai}' not supported yet. Supported: {sorted(SUPPORTED_AIS)}", file=sys.stderr)
        print(f"Use 'all' to build all supported AI environments.", file=sys.stderr)
        return 1

    if platform not in SUPPORTED_PLATFORMS:
        print(
            f"Warning: platform '{platform}' is not in {sorted(SUPPORTED_PLATFORMS)}. "
            f"Using it as directory name anyway.",
            file=sys.stderr,
        )

    repo_root = find_repo_root()

    if ai == "cursor":
        out_dir = build_for_cursor(repo_root, platform)
        print(f"Built NovelKit package for ai='{ai}', platform='{platform}' at: {out_dir}")
        print(f"  meta-space   : {out_dir / '.novelkit'}")
        print(f"  commands     : {out_dir / '.cursor' / 'commands'}")
        return 0

    # 理论上不会走到这里
    print(f"Internal error: unsupported AI '{ai}' reached build logic.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
