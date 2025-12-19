# 贡献指南

NovelKit 是元项目，主要开发内容是编写命令文件、模板文件和脚本文件。

## 项目结构

```
novel-kit/
├── commands/          # AI 命令定义（38个）
├── templates/         # 模板文件（7个）
├── scripts/           # 自动化脚本
│   ├── bash/         # Linux/Mac 脚本（8个）
│   └── powershell/   # Windows 脚本（8个）
├── memory/            # 项目配置
├── src/novel_kit_cli/ # CLI 工具
└── build_novelkit.py  # 构建脚本
```

## 开发流程

### 1. 添加新命令

在 `commands/` 目录创建 `.md` 文件：

```markdown
---
description: 命令描述
scripts:
  sh: .novelkit/scripts/bash/manager.sh action "$ARGUMENTS"
  ps: .novelkit/scripts/powershell/manager.ps1 -Action Action -Json "$ARGUMENTS"
---

## User Input

```text
$ARGUMENTS
```

[命令的交互流程和 AI 行为定义...]
```

参考现有命令：
- `commands/writer-new.md` - 复杂的交互式命令
- `commands/writer-list.md` - 简单的列表命令
- `commands/novel-setup.md` - 初始化命令

### 2. 添加新模板

在 `templates/` 目录创建 `.md` 文件：

```markdown
# [Title] Template

**Created**: [DATE]
**Writer ID**: [writer-id]

---

## Section 1

[内容结构...]
```

参考现有模板：
- `templates/writer.md` - Writer 模板
- `templates/chapter.md` - 章节模板
- `templates/character.md` - 角色模板

### 3. 添加脚本支持

如果命令需要新的脚本操作，在 `scripts/bash/` 和 `scripts/powershell/` 添加对应脚本。

参考现有脚本：
- `scripts/bash/writer-manager.sh` - Writer 管理脚本
- `scripts/bash/chapter-manager.sh` - 章节管理脚本

脚本需要：
- 查找项目根目录（通过 `.novelkit/` 或 `.git/`）
- 读取/更新 `memory/config.json`
- 使用模板生成文件

### 4. 测试

```bash
# 构建测试
python build_novelkit.py cursor linux

# 初始化测试项目
novel-kit init test-project --ai cursor

# 在 Cursor 中测试新命令
/novel.your.command
```

## 命令文件命名规则

命令文件使用 kebab-case，构建后自动转换为点分隔格式：

- `writer-new.md` → `novel.writer.new.md`
- `chapter-plan.md` → `novel.chapter.plan.md`
- `novel-setup.md` → `novel.setup.md`

## 脚本规范

### Bash 脚本

```bash
#!/usr/bin/env bash
set -e

# 查找项目根目录
find_repo_root() {
    local dir="$1"
    while [ "$dir" != "/" ]; do
        if [ -d "$dir/.git" ] || [ -d "$dir/.novelkit" ]; then
            echo "$dir"
            return 0
        fi
        dir="$(dirname "$dir")"
    done
    return 1
}

REPO_ROOT="$(find_repo_root "$(pwd)")"
```

### PowerShell 脚本

```powershell
#Requires -Version 5.1

function Find-RepoRoot {
    param([string]$Path)
    $current = $Path
    while ($current -ne $null) {
        if ((Test-Path (Join-Path $current ".git")) -or 
            (Test-Path (Join-Path $current ".novelkit"))) {
            return $current
        }
        $current = Split-Path $current -Parent
    }
    return $null
}

$REPO_ROOT = Find-RepoRoot (Get-Location)
```

## 构建和发布

### 配置文件

支持的 AI 环境在 `build-config.json` 中配置（仅用于构建和 CI/CD）：

```json
{
  "supported_ais": ["cursor"],
  "supported_platforms": ["linux", "win"]
}
```

**注意**：CLI 工具不依赖此配置文件（用户没有源码），CLI 中的 AI 环境配置在代码中硬编码。

### 本地构建

```bash
# 构建单个 AI 环境
python build_novelkit.py cursor linux
python build_novelkit.py cursor win

# 构建所有支持的 AI 环境
python build_novelkit.py all
```

### 发布流程

1. 更新 `pyproject.toml` 中的版本号
2. 提交更改
3. 创建并推送 tag：`git tag v0.0.2 && git push origin v0.0.2`
4. GitHub Actions 自动读取 `build-config.json`，构建所有 AI 环境并发布

## 提交规范

使用约定式提交：

```
feat(command): 添加新命令
fix(script): 修复脚本错误
docs: 更新文档
```

## 获取帮助

- 查看现有命令文件作为参考
- 创建 [Issue](https://github.com/t59688/novel-kit/issues)
