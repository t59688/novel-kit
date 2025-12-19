#!/usr/bin/env python3
"""
NovelKit CLI - 项目初始化工具

用法:
    novel-kit init <project-name>     # 创建新项目目录
    novel-kit init .                  # 在当前目录初始化
    novel-kit init --here             # 在当前目录初始化（替代语法）
"""

import os
import sys
import shutil
import platform
import zipfile
import tempfile
from pathlib import Path
from typing import Optional, Dict

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.tree import Tree
from rich.align import Align
from rich.text import Text
from rich.table import Table
from rich.live import Live

# 尝试导入 readchar（用于交互式选择）
try:
    import readchar
    HAS_READCHAR = True
except ImportError:
    HAS_READCHAR = False
    # 如果没有 readchar，将使用简单的 typer.confirm

# 尝试导入 httpx（用于远程下载）
try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

# 检测平台
IS_WINDOWS = platform.system() == "Windows"
PLATFORM = "win" if IS_WINDOWS else "linux"

console = Console()

BANNER = """
███╗   ██╗ ██████╗ ██╗   ██╗███████╗██╗     ██╗  ██╗██╗████████╗
████╗  ██║██╔═══██╗██║   ██║██╔════╝██║     ██║ ██╔╝██║╚══██╔══╝
██╔██╗ ██║██║   ██║██║   ██║█████╗  ██║     █████╔╝ ██║   ██║   
██║╚██╗██║██║   ██║╚██╗ ██╔╝██╔══╝  ██║     ██╔═██╗ ██║   ██║   
██║ ╚████║╚██████╔╝ ╚████╔╝ ███████╗███████╗██║  ██╗██║   ██║   
╚═╝  ╚═══╝ ╚═════╝   ╚═══╝  ╚══════╝╚══════╝╚═╝  ╚═╝╚═╝   ╚═╝   
"""

TAGLINE = "AI-Assisted Novel Writing Toolkit"

# 远程仓库配置
REPO_OWNER = "t59688"
REPO_NAME = "novel-kit"
REPO_URL = f"https://github.com/{REPO_OWNER}/{REPO_NAME}"

# AI 环境配置（可扩展）
# 注意：CLI 面向用户，用户没有源码，所以这里硬编码支持的 AI 环境
# build-config.json 只用于构建脚本和 CI/CD，不用于 CLI
AI_ENV_CONFIG: Dict[str, Dict[str, str]] = {
    "cursor": {
        "name": "Cursor",
        "description": "Cursor IDE 集成",
        "folder": ".cursor",
        "build_function": "build_for_cursor",
    },
    # TODO: 添加更多 AI 环境支持时：
    # 1. 更新 build-config.json（用于构建）
    # 2. 在这里添加配置（用于 CLI）
    # 3. 在 build_novelkit.py 中添加构建函数
    # "claude": {
    #     "name": "Claude Code",
    #     "description": "Claude Code 集成",
    #     "folder": ".claude",
    #     "build_function": "build_for_claude",
    # },
}


def show_banner():
    """显示 ASCII 艺术横幅"""
    banner_lines = BANNER.strip().split('\n')
    colors = ["bright_blue", "blue", "cyan", "bright_cyan", "white", "bright_white"]
    
    styled_banner = Text()
    for i, line in enumerate(banner_lines):
        color = colors[i % len(colors)]
        styled_banner.append(line + "\n", style=color)
    
    console.print(Align.center(styled_banner))
    console.print(Align.center(Text(TAGLINE, style="italic bright_yellow")))
    console.print()


def get_key() -> str:
    """获取单个按键（跨平台）"""
    if not HAS_READCHAR:
        return ""
    
    try:
        key = readchar.readkey()
        
        # 处理方向键
        if key == readchar.key.UP:
            return 'up'
        if key == readchar.key.DOWN:
            return 'down'
        if key == readchar.key.ENTER or key == '\r' or key == '\n':
            return 'enter'
        if key == readchar.key.ESC:
            return 'escape'
        if key == '\x03':  # Ctrl+C
            raise KeyboardInterrupt
        
        # Windows 上的特殊处理
        if IS_WINDOWS:
            # Windows 上可能需要特殊处理
            if key == '\xe0':  # 扩展键前缀
                next_key = readchar.readkey()
                if next_key == 'H':  # 上箭头
                    return 'up'
                if next_key == 'P':  # 下箭头
                    return 'down'
        
        return key
    except Exception:
        return ""


def select_with_arrows(
    options: Dict[str, str],
    prompt_text: str = "选择选项",
    default_key: Optional[str] = None
) -> str:
    """
    使用箭头键进行交互式选择（使用 Rich Live 显示）
    
    Args:
        options: 字典，键为选项键，值为描述
        prompt_text: 提示文本
        default_key: 默认选中的键
        
    Returns:
        选中的选项键
    """
    if not HAS_READCHAR or not sys.stdin.isatty():
        # 回退到简单的 typer 选择
        console.print(f"\n[cyan]{prompt_text}[/cyan]")
        option_keys = list(options.keys())
        for i, (key, desc) in enumerate(options.items(), 1):
            console.print(f"  {i}. {key} - {desc}")
        
        if default_key and default_key in option_keys:
            default_index = option_keys.index(default_key) + 1
            choice = typer.prompt("请选择", default=str(default_index), type=int)
        else:
            choice = typer.prompt("请选择", type=int)
        
        if 1 <= choice <= len(option_keys):
            return option_keys[choice - 1]
        return option_keys[0]
    
    option_keys = list(options.keys())
    if default_key and default_key in option_keys:
        selected_index = option_keys.index(default_key)
    else:
        selected_index = 0
    
    selected_key = None
    
    def create_selection_panel():
        """创建选择面板"""
        table = Table.grid(padding=(0, 2))
        table.add_column(style="cyan", justify="left", width=3)
        table.add_column(style="white", justify="left")
        
        for i, key in enumerate(option_keys):
            if i == selected_index:
                table.add_row("▶", f"[cyan]{key}[/cyan] [dim]({options[key]})[/dim]")
            else:
                table.add_row(" ", f"[cyan]{key}[/cyan] [dim]({options[key]})[/dim]")
        
        table.add_row("", "")
        table.add_row("", "[dim]使用 ↑/↓ 导航，Enter 选择，Esc 取消[/dim]")
        
        return Panel(
            table,
            title=f"[bold]{prompt_text}[/bold]",
            border_style="cyan",
            padding=(1, 2)
        )
    
    console.print()
    
    def run_selection_loop():
        nonlocal selected_key, selected_index
        with Live(create_selection_panel(), console=console, transient=True, auto_refresh=False) as live:
            while True:
                try:
                    key = get_key()
                    if key == 'up':
                        selected_index = (selected_index - 1) % len(option_keys)
                    elif key == 'down':
                        selected_index = (selected_index + 1) % len(option_keys)
                    elif key == 'enter':
                        selected_key = option_keys[selected_index]
                        break
                    elif key == 'escape':
                        console.print("\n[yellow]选择已取消[/yellow]")
                        raise typer.Exit(1)
                    
                    live.update(create_selection_panel(), refresh=True)
                except KeyboardInterrupt:
                    console.print("\n[yellow]选择已取消[/yellow]")
                    raise typer.Exit(1)
    
    run_selection_loop()
    
    if selected_key is None:
        console.print("\n[red]选择失败[/red]")
        raise typer.Exit(1)
    
    return selected_key


def find_package_dist_dir(ai_env: str = "cursor") -> Optional[Path]:
    """
    查找构建产物目录。
    
    Args:
        ai_env: AI 环境名称（如 "cursor", "claude" 等）
    
    查找策略：
    1. 从源码目录查找（开发模式）- 相对于当前文件
    2. 从当前工作目录查找（用于测试）
    3. 从环境变量指定的路径查找
    4. TODO: 从远程仓库下载（如果本地不存在）
    5. TODO: 从已安装的包中查找（需要打包时包含 dist 目录）
    """
    dist_name = f"{ai_env}-{PLATFORM}"
    
    # 方法1: 从源码目录查找（开发模式）
    # 假设 CLI 在 src/novel_kit_cli/__init__.py
    current_file = Path(__file__).resolve()
    repo_root = current_file.parent.parent.parent
    dist_dir = repo_root / "dist" / dist_name
    
    if dist_dir.exists():
        return dist_dir
    
    # 方法2: 从当前工作目录查找（用于测试）
    cwd_dist = Path.cwd() / "dist" / dist_name
    if cwd_dist.exists():
        return cwd_dist
    
    # 方法3: 从环境变量指定的路径查找
    env_dist = os.getenv("NOVELKIT_DIST_DIR")
    if env_dist:
        env_path = Path(env_dist) / dist_name
        if env_path.exists():
            return env_path
    
    # 方法4: 从远程仓库下载（在调用处处理，不在这里）
    
    # 方法5: 尝试从用户主目录查找（如果包已安装）
    # TODO: 实现从已安装包中查找的逻辑
    
    return None


def download_from_remote(ai_env: str, platform: str, github_token: Optional[str] = None) -> Optional[Path]:
    """
    从远程仓库下载构建产物
    
    Args:
        ai_env: AI 环境名称
        platform: 平台名称（linux/win）
        github_token: GitHub token（可选，用于提高速率限制）
    
    Returns:
        下载后的目录路径，如果失败返回 None
    """
    if not HAS_HTTPX:
        console.print("[red]错误:[/red] 需要安装 httpx 库才能使用远程下载功能")
        console.print("[yellow]提示:[/yellow] 运行: pip install httpx")
        console.print("[yellow]或重新安装:[/yellow] pip install -e .")
        return None
    
    # 构建产物文件名模式
    asset_pattern = f"novel-kit-{ai_env}-{platform}"
    
    # GitHub API URL
    api_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/latest"
    
    # 准备请求头
    headers = {}
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"
    elif os.getenv("GH_TOKEN"):
        headers["Authorization"] = f"Bearer {os.getenv('GH_TOKEN')}"
    elif os.getenv("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {os.getenv('GITHUB_TOKEN')}"
    
    try:
        # 获取最新 release 信息
        console.print("[cyan]正在获取最新版本信息...[/cyan]")
        with httpx.Client(timeout=30.0, follow_redirects=True) as client:
            response = client.get(api_url, headers=headers)
            
            if response.status_code == 404:
                console.print(f"[red]错误:[/red] 仓库 {REPO_OWNER}/{REPO_NAME} 不存在或没有 releases")
                return None
            
            if response.status_code == 403:
                rate_limit_info = response.headers.get("X-RateLimit-Remaining", "unknown")
                console.print(f"[red]错误:[/red] GitHub API 访问受限（剩余请求: {rate_limit_info}）")
                console.print("[yellow]提示:[/yellow] 可以设置 GH_TOKEN 或 GITHUB_TOKEN 环境变量提高速率限制")
                return None
            
            if response.status_code != 200:
                console.print(f"[red]错误:[/red] GitHub API 返回状态码 {response.status_code}")
                return None
            
            release_data = response.json()
            assets = release_data.get("assets", [])
            
            # 查找匹配的构建产物
            matching_assets = [
                asset for asset in assets
                if asset_pattern in asset["name"] and asset["name"].endswith(".zip")
            ]
            
            if not matching_assets:
                console.print(f"[red]错误:[/red] 未找到匹配的构建产物（模式: {asset_pattern}*.zip）")
                console.print(f"[yellow]可用资源:[/yellow]")
                for asset in assets[:5]:  # 只显示前5个
                    console.print(f"  - {asset['name']}")
                if len(assets) > 5:
                    console.print(f"  ... 还有 {len(assets) - 5} 个资源")
                return None
            
            asset = matching_assets[0]
            download_url = asset["browser_download_url"]
            filename = asset["name"]
            file_size = asset["size"]
            
            console.print(f"[cyan]找到构建产物:[/cyan] {filename}")
            console.print(f"[cyan]版本:[/cyan] {release_data.get('tag_name', 'unknown')}")
            console.print(f"[cyan]大小:[/cyan] {file_size:,} 字节")
            
            # 创建缓存目录
            cache_dir = Path.home() / ".cache" / "novel-kit" / "dist"
            cache_dir.mkdir(parents=True, exist_ok=True)
            
            # 检查缓存
            cached_file = cache_dir / filename
            cached_dir = cache_dir / f"{ai_env}-{platform}"
            
            # 如果缓存存在且完整，直接使用
            if cached_dir.exists() and cached_file.exists():
                console.print(f"[green]使用缓存:[/green] {cached_dir}")
                return cached_dir
            
            # 下载文件
            console.print("[cyan]正在下载构建产物...[/cyan]")
            zip_path = cache_dir / filename
            
            with httpx.stream("GET", download_url, headers=headers, timeout=60.0, follow_redirects=True) as stream:
                if stream.status_code != 200:
                    console.print(f"[red]错误:[/red] 下载失败，状态码 {stream.status_code}")
                    return None
                
                total_size = int(stream.headers.get("content-length", 0))
                
                with open(zip_path, "wb") as f:
                    if total_size > 0:
                        with Progress(
                            SpinnerColumn(),
                            TextColumn("[progress.description]{task.description}"),
                            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                            console=console,
                        ) as progress:
                            task = progress.add_task("下载中...", total=total_size)
                            downloaded = 0
                            for chunk in stream.iter_bytes(chunk_size=8192):
                                f.write(chunk)
                                downloaded += len(chunk)
                                progress.update(task, completed=downloaded)
                    else:
                        for chunk in stream.iter_bytes(chunk_size=8192):
                            f.write(chunk)
            
            console.print(f"[green]下载完成:[/green] {filename}")
            
            # 解压文件
            console.print("[cyan]正在解压...[/cyan]")
            extract_dir = cache_dir / f"{ai_env}-{platform}"
            
            # 如果目录已存在，先删除
            if extract_dir.exists():
                shutil.rmtree(extract_dir)
            
            extract_dir.mkdir(parents=True, exist_ok=True)
            
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # 检查解压后的结构
            # 如果只有一个顶层目录，可能需要调整
            extracted_items = list(extract_dir.iterdir())
            if len(extracted_items) == 1 and extracted_items[0].is_dir():
                # 如果解压后只有一个目录，将其内容提升到 extract_dir
                nested_dir = extracted_items[0]
                temp_dir = extract_dir.parent / f"{extract_dir.name}_temp"
                nested_dir.rename(temp_dir)
                extract_dir.rmdir()
                temp_dir.rename(extract_dir)
            
            console.print(f"[green]解压完成:[/green] {extract_dir}")
            
            # 清理 ZIP 文件（可选，保留以便下次使用）
            # zip_path.unlink()
            
            return extract_dir
            
    except httpx.HTTPError as e:
        console.print(f"[red]网络错误:[/red] {e}")
        return None
    except zipfile.BadZipFile as e:
        console.print(f"[red]ZIP 文件损坏:[/red] {e}")
        if 'zip_path' in locals() and zip_path.exists():
            zip_path.unlink()
        return None
    except Exception as e:
        console.print(f"[red]下载失败:[/red] {e}")
        if 'zip_path' in locals() and zip_path.exists():
            zip_path.unlink()
        return None


def copy_tree(src: Path, dst: Path, verbose: bool = False) -> None:
    """递归复制目录树"""
    if not src.exists():
        return
    
    dst.mkdir(parents=True, exist_ok=True)
    
    for item in src.iterdir():
        target = dst / item.name
        if item.is_dir():
            copy_tree(item, target, verbose)
        else:
            if target.exists() and verbose:
                console.print(f"[yellow]覆盖文件:[/yellow] {target.relative_to(dst.parent)}")
            shutil.copy2(item, target)


def init_project(
    project_path: Path,
    dist_dir: Path,
    is_current_dir: bool = False,
    force: bool = False,
    verbose: bool = False,
) -> bool:
    """
    初始化 NovelKit 项目
    
    Args:
        project_path: 项目路径
        dist_dir: 构建产物目录
        is_current_dir: 是否在当前目录初始化
        force: 是否强制覆盖（跳过确认）
        verbose: 是否显示详细信息
    
    Returns:
        是否成功
    """
    if not dist_dir.exists():
        console.print(f"[red]错误:[/red] 找不到构建产物目录: {dist_dir}")
        console.print("[yellow]提示:[/yellow] 请先运行构建脚本: python build_novelkit.py cursor {platform}")
        return False
    
    # 检查目标目录
    if is_current_dir:
        existing_items = list(project_path.iterdir())
        if existing_items:
            console.print(f"[yellow]警告:[/yellow] 当前目录不为空 ({len(existing_items)} 个项目)")
            console.print("[yellow]NovelKit 文件将与现有内容合并，可能会覆盖现有文件[/yellow]")
            if not force:
                response = typer.confirm("是否继续？")
                if not response:
                    console.print("[yellow]操作已取消[/yellow]")
                    return False
    else:
        if project_path.exists():
            console.print(f"[red]错误:[/red] 目录 '{project_path}' 已存在")
            return False
        project_path.mkdir(parents=True, exist_ok=True)
    
    # 复制文件
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("正在初始化项目...", total=None)
        
        # 复制 .novelkit 目录
        novelkit_src = dist_dir / ".novelkit"
        novelkit_dst = project_path / ".novelkit"
        if novelkit_src.exists():
            copy_tree(novelkit_src, novelkit_dst, verbose)
            if verbose:
                progress.update(task, description="已复制 .novelkit 目录")
        
        # 复制 AI 环境特定的目录（如 .cursor, .claude 等）
        # 查找所有以 . 开头的目录（AI 环境目录）
        for item in dist_dir.iterdir():
            if item.is_dir() and item.name.startswith(".") and item.name != ".novelkit":
                ai_folder_dst = project_path / item.name
                copy_tree(item, ai_folder_dst, verbose)
                if verbose:
                    progress.update(task, description=f"已复制 {item.name} 目录")
        
        progress.update(task, completed=True)
    
    # 设置脚本执行权限（仅 Linux/Mac）
    if not IS_WINDOWS:
        scripts_dir = project_path / ".novelkit" / "scripts" / "bash"
        if scripts_dir.exists():
            for script in scripts_dir.rglob("*.sh"):
                if script.is_file():
                    os.chmod(script, 0o755)
    
    return True


app = typer.Typer(
    name="novel-kit",
    help="NovelKit - AI 辅助小说写作工具包",
    add_completion=False,
)


@app.command()
def init(
    project_name: str = typer.Argument(
        None,
        help="项目名称（新目录名），或使用 '.' 表示当前目录"
    ),
    ai_env: Optional[str] = typer.Option(
        None,
        "--ai",
        help=f"AI 环境 ({', '.join(AI_ENV_CONFIG.keys())})"
    ),
    here: bool = typer.Option(
        False,
        "--here",
        help="在当前目录初始化（替代使用 '.'）"
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="强制初始化，跳过确认（当目录不为空时）"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="显示详细信息"
    ),
):
    """
    初始化新的 NovelKit 项目
    
    示例:
        novel-kit init my-novel          # 创建新目录 my-novel（交互式选择 AI）
        novel-kit init my-novel --ai cursor  # 指定 AI 环境
        novel-kit init .                 # 在当前目录初始化
        novel-kit init --here            # 在当前目录初始化（替代语法）
        novel-kit init . --force         # 强制初始化，跳过确认
    """
    show_banner()
    
    # 处理参数
    if project_name == ".":
        here = True
        project_name = None
    
    if here and project_name:
        console.print("[red]错误:[/red] 不能同时指定项目名称和 --here 选项")
        raise typer.Exit(1)
    
    if not here and not project_name:
        console.print("[red]错误:[/red] 必须指定项目名称、使用 '.' 或使用 --here 选项")
        raise typer.Exit(1)
    
    # 确定项目路径
    if here:
        project_path = Path.cwd()
        project_name = project_path.name
    else:
        project_path = Path(project_name).resolve()
    
    # 选择 AI 环境
    if ai_env:
        if ai_env not in AI_ENV_CONFIG:
            console.print(f"[red]错误:[/red] 不支持的 AI 环境 '{ai_env}'")
            console.print(f"[yellow]支持的 AI 环境:[/yellow] {', '.join(sorted(AI_ENV_CONFIG.keys()))}")
            raise typer.Exit(1)
        selected_ai = ai_env
    else:
        # 交互式选择 AI 环境
        ai_choices = {
            key: config["description"] 
            for key, config in AI_ENV_CONFIG.items()
        }
        selected_ai = select_with_arrows(
            ai_choices,
            "选择 AI 环境:",
            default_key="cursor"  # 默认选择 cursor
        )
    
    ai_config = AI_ENV_CONFIG[selected_ai]
    
    # 查找构建产物
    dist_dir = find_package_dist_dir(selected_ai)
    
    # 如果本地找不到，尝试从远程下载
    if not dist_dir:
        console.print(f"[yellow]警告:[/yellow] 本地未找到 {selected_ai} 环境的构建产物")
        console.print("[cyan]尝试从远程下载...[/cyan]")
        
        # 检查是否有 GitHub token（从环境变量或参数获取）
        github_token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
        
        dist_dir = download_from_remote(selected_ai, PLATFORM, github_token=github_token)
    
    if not dist_dir:
        console.print("[red]错误:[/red] 找不到 NovelKit 构建产物")
        console.print(f"[yellow]提示:[/yellow] 请先运行: [cyan]python build_novelkit.py {selected_ai} {PLATFORM}[/cyan]")
        console.print("[dim]或等待远程下载功能实现[/dim]")
        raise typer.Exit(1)
    
    if verbose:
        console.print(f"[cyan]构建产物目录:[/cyan] {dist_dir}")
        console.print(f"[cyan]项目路径:[/cyan] {project_path}")
    
    # 显示项目信息
    setup_lines = [
        "[cyan]NovelKit 项目初始化[/cyan]",
        "",
        f"{'项目名称':<15} [green]{project_name}[/green]",
        f"{'项目路径':<15} [dim]{project_path}[/dim]",
        f"{'AI 环境':<15} [cyan]{ai_config['name']}[/cyan] [dim]({selected_ai})[/dim]",
        f"{'平台':<15} [dim]{PLATFORM}[/dim]",
    ]
    
    console.print(Panel("\n".join(setup_lines), border_style="cyan", padding=(1, 2)))
    
    # 初始化项目
    success = init_project(
        project_path=project_path,
        dist_dir=dist_dir,
        is_current_dir=here,
        force=force,
        verbose=verbose,
    )
    
    if not success:
        raise typer.Exit(1)
    
    # 显示成功信息
    console.print()
    console.print("[bold green]✓ 项目初始化成功！[/bold green]")
    console.print()
    
    # 显示下一步操作
    steps_lines = []
    if not here:
        steps_lines.append(f"1. 进入项目目录: [cyan]cd {project_name}[/cyan]")
        step_num = 2
    else:
        steps_lines.append("1. 您已在项目目录中！")
        step_num = 2
    
    steps_lines.append(f"{step_num}. 开始使用 NovelKit 命令:")
    steps_lines.append("   • [cyan]/novel.writer.new[/] - 创建新的 writer")
    steps_lines.append("   • [cyan]/novel.writer.list[/] - 列出所有 writers")
    steps_lines.append("   • [cyan]/novel.writer.switch[/] - 切换活动 writer")
    steps_lines.append("   • [cyan]/novel.setup[/] - 项目设置")
    
    steps_panel = Panel("\n".join(steps_lines), title="下一步", border_style="cyan", padding=(1, 2))
    console.print(steps_panel)
    


@app.command()
def version():
    """显示版本信息"""
    show_banner()
    
    import importlib.metadata
    
    cli_version = "unknown"
    try:
        cli_version = importlib.metadata.version("novel-kit-cli")
    except Exception:
        # 开发模式：尝试从 pyproject.toml 读取
        try:
            import tomllib
            pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
            if pyproject_path.exists():
                with open(pyproject_path, "rb") as f:
                    data = tomllib.load(f)
                    cli_version = data.get("project", {}).get("version", "unknown")
        except Exception:
            pass
    
    # 使用 Rich 的 Table 来显示版本信息（已导入 Table）
    info_table = Table(show_header=False, box=None, padding=(0, 2))
    info_table.add_column(style="cyan", justify="right")
    info_table.add_column(style="white", justify="left")
    
    info_table.add_row("[cyan]NovelKit CLI[/cyan]", cli_version)
    info_table.add_row("平台", PLATFORM)
    info_table.add_row("Python", sys.version.split()[0])
    
    console.print()
    console.print(info_table)
    console.print()


def main():
    """CLI 入口点"""
    app()


if __name__ == "__main__":
    main()

