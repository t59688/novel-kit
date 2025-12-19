# NovelKit

<div align="center">

![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**AI 辅助小说写作工具包，帮助作者使用 AI 助手创作长篇小说**

[特性](#特性) • [快速开始](#快速开始) • [文档](#文档) • [贡献](#贡献)

</div>

---

NovelKit 是一个专为 AI 辅助小说创作设计的 **Slash 命令集合**（不是图形界面应用），提供了完整的命令系统和项目结构，让作者能够高效地使用 AI（如 Cursor）创作长篇小说。通过 `/novel.xxx` 格式的命令，在 AI 环境中直接调用，支持角色管理、世界构建、剧情规划、章节写作等全方位的创作功能。

## ✨ 特性

- ⚡ **Slash 命令集合** - 提供 40+ 个 `/novel.xxx` 格式的命令，在 AI 环境中直接调用（非图形界面）
- 🔌 **AI 环境原生集成** - 专为 Cursor 等 AI 开发环境设计，命令即用即生效
- 🎭 **多 Writer 管理** - 支持多个写作风格配置，灵活切换不同的叙述视角、语言风格和节奏
- 📚 **完整的章节生命周期** - 从规划、写作、审查、润色到确认的完整工作流
- 👥 **角色管理系统** - 创建、更新和管理角色信息，维护角色档案
- 🌍 **世界构建工具** - 管理地点、势力、关系网络等世界设定元素
- 📖 **剧情管理** - 支持主线、支线和伏笔的创建与追踪
- 📋 **小说宪法** - 定义和维护小说的核心规则和设定，确保创作一致性
- 🔄 **交互式命令** - 所有命令支持交互式操作，AI 助手引导完成创作
- 🎯 **状态管理** - 自动追踪当前章节、角色、地点等创作状态
- 📊 **结构化存储** - 清晰的项目结构，便于版本控制和协作
- 🛠️ **跨平台支持** - 支持 Linux、macOS 和 Windows

## 📦 安装

### 方式一：使用 uv（推荐）

`uv` 是一个Python 包管理器，可以快速安装 CLI 工具，无需系统权限：

```bash
# 安装 uv（如果还没有）

# 安装 NovelKit CLI
uv tool install novel-kit-cli
```

**验证安装：**
```bash
novel-kit version
```

### 方式二：使用 pip

```bash
# 尝试用户安装
pip install novel-kit-cli

```

### 方式三：从源码安装

```bash
git clone https://github.com/t59688/novel-kit.git
cd novel-kit
pip install --break-system-packages -e .
```

## 🚀 快速开始

> **注意**：NovelKit 是 Slash 命令集合，需要在支持命令的 AI 环境（如 Cursor）中使用，不是独立的图形界面应用。

### 1. 初始化项目

首先使用 CLI 工具初始化项目：

```bash
novel-kit init my-novel
```

会交互式选择 AI 环境（当前支持 cursor），然后自动下载构建产物并初始化项目。

### 2. 项目设置

初始化完成后，在 Cursor（或其他 AI 环境）中使用 **slash 命令**：

```
/novel.setup
```

这会创建必要的目录结构（`chapters/`, `world/`, `plots/` 等）。

### 3. 创建小说宪法

小说宪法定义了小说的核心规则和设定，确保创作一致性。建议在开始创作前先创建：

```
/novel.constitution.create
```

按提示交互式创建，定义小说的核心规则、世界观、风格要求等。

### 4. 创建 Writer

Writer 定义了写作风格。使用 slash 命令创建第一个 writer：

```
/novel.writer.new
```

按提示交互式创建，或直接提供描述：

```
/novel.writer.new mystery thriller writer, fast-paced, third person limited
```

### 5. 开始写作

使用 slash 命令开始创作：

```
/novel.chapter.new    # 创建新章节
/novel.chapter.plan   # 规划章节
/novel.chapter.write  # 撰写章节
```

## 💡 核心概念

### 小说宪法

小说宪法是 NovelKit 的核心概念，定义了小说的核心规则和设定，确保创作一致性：

- **世界观规则** - 魔法体系、科技水平、社会结构等基础设定
- **创作规范** - 语言风格、叙事视角、节奏控制等写作要求
- **角色设定原则** - 角色创建和更新的指导原则
- **剧情发展规则** - 主线、支线和伏笔的管理原则

建议在开始创作前先创建宪法，后续的创作都会参考宪法来保持一致性。可以通过 `/novel.constitution.check` 检查内容是否符合宪法规则。

### Writer（写作风格配置）

Writer 定义了小说的写作风格和规则：

- **叙述视角和时态** - 第一人称、第三人称等，以及过去时、现在时等
- **语言风格和节奏** - 文风特点、叙事节奏控制
- **角色发展和对话风格** - 角色塑造方式和对话特色
- **世界构建方式** - 世界观呈现方式

每个项目可以创建多个 Writer，通过 `/novel.writer.switch` 在不同风格间切换，适合多人协作或不同章节采用不同风格。

### 章节生命周期

NovelKit 定义了完整的章节创作流程：

1. **规划** (`/novel.chapter.plan`) - 规划章节内容和大纲
2. **撰写** (`/novel.chapter.write`) - AI 辅助撰写章节正文
3. **审查** (`/novel.chapter.review`) - 审查章节质量和一致性
4. **润色** (`/novel.chapter.polish`) - 优化语言表达
5. **确认** (`/novel.chapter.confirm`) - 确认章节完成，更新状态

### 世界构建体系

NovelKit 提供了完整的世界构建工具：

- **角色管理** - 创建和管理角色档案，包括基本信息、性格、关系等
- **地点管理** - 管理地点信息，支持地点地图可视化
- **势力管理** - 创建和管理各种势力，追踪成员和关系
- **剧情管理** - 主线、支线和伏笔的创建与追踪

### 项目结构

```
my-novel/
├── .novelkit/          # 系统文件（自动管理）
│   ├── memory/         # 状态和配置
│   ├── templates/      # 模板文件
│   ├── scripts/        # 自动化脚本
│   ├── writers/        # Writer 配置
│   └── chapters/       # 章节元数据
├── .cursor/            # Cursor 命令（或其他 AI 环境）
├── chapters/           # 章节正文
├── world/              # 世界构建（角色、地点、势力等）
└── plots/              # 剧情数据
```

## 📋 主要命令

NovelKit 提供了 40+ 个 **Slash 命令**来管理小说创作的各个环节。所有命令都以 `/novel.xxx` 的格式在 AI 环境中使用（如 `/novel.chapter.new`）。这些命令不是图形界面按钮，而是通过文本命令调用，AI 助手会读取命令定义并引导你完成交互式操作。

> 📖 **完整命令列表和使用说明请查看 [命令文档](docs/commands.md)**

> 💡 **使用顺序建议**：按照实际创作流程，建议先完成项目设置和宪法创建，再开始创建 Writer 和进行章节创作。

### ⚙️ 项目设置（1 个命令）

项目初始化，创建必要的目录结构。**这是使用 NovelKit 的第一步**。

- `/novel.setup` - 初始化项目目录结构（创建 `chapters/`, `world/`, `plots/` 等目录）

### 📜 小说宪法（4 个命令）

定义和维护小说的核心规则和设定，确保创作一致性。**建议在开始创作前先创建宪法**。

- `/novel.constitution.create` - 创建小说宪法（核心规则和设定）
- `/novel.constitution.show` - 查看小说宪法
- `/novel.constitution.update` - 更新小说宪法
- `/novel.constitution.check` - 检查内容是否符合宪法规则

### 🎭 Writer 管理（5 个命令）

管理写作风格配置，支持多 Writer 切换。**创建宪法后，建议创建第一个 Writer 来定义写作风格**。

- `/novel.writer.new` - 创建新的 Writer（支持交互式或快速生成）
- `/novel.writer.list` - 列出所有 Writers
- `/novel.writer.show` - 查看 Writer 详细信息
- `/novel.writer.switch` - 切换活动 Writer
- `/novel.writer.update` - 更新 Writer 配置

### 📚 章节管理（6 个命令）

完整的章节创作生命周期管理。**这是核心创作流程**。

- `/novel.chapter.new` - 创建新章节
- `/novel.chapter.plan` - 规划章节内容和结构
- `/novel.chapter.write` - AI 辅助撰写章节正文
- `/novel.chapter.review` - 审查章节质量和一致性
- `/novel.chapter.polish` - 润色和优化章节
- `/novel.chapter.confirm` - 确认章节完成

### 👥 角色管理（4 个命令）

创建和管理角色档案。**可以在创作过程中随时创建和管理角色**。

- `/novel.character.new` - 创建新角色
- `/novel.character.list` - 列出所有角色
- `/novel.character.show` - 查看角色详情
- `/novel.character.update` - 更新角色信息

### 🌍 地点管理（5 个命令）

管理小说中的地点设定。

- `/novel.location.new` - 创建新地点
- `/novel.location.list` - 列出所有地点
- `/novel.location.show` - 查看地点详情
- `/novel.location.update` - 更新地点信息
- `/novel.location.map` - 查看地点地图（可视化）

### 🏛️ 势力管理（6 个命令）

管理各种势力和组织。

- `/novel.faction.new` - 创建新势力
- `/novel.faction.list` - 列出所有势力
- `/novel.faction.show` - 查看势力详情
- `/novel.faction.update` - 更新势力信息
- `/novel.faction.members` - 查看势力成员
- `/novel.faction.relationships` - 查看势力关系网络

### 📖 剧情管理（10 个命令）

管理主线、支线和伏笔。

**主线剧情**（4 个命令）：
- `/novel.plot.main.new` - 创建主线剧情
- `/novel.plot.main.list` - 列出所有主线剧情
- `/novel.plot.main.show` - 查看主线剧情详情
- `/novel.plot.main.update` - 更新主线剧情

**支线剧情**（4 个命令）：
- `/novel.plot.side.new` - 创建支线剧情
- `/novel.plot.side.list` - 列出所有支线剧情
- `/novel.plot.side.show` - 查看支线剧情详情
- `/novel.plot.side.update` - 更新支线剧情

**伏笔管理**（3 个命令）：
- `/novel.plot.foreshadow.new` - 创建伏笔
- `/novel.plot.foreshadow.list` - 列出所有伏笔
- `/novel.plot.foreshadow.track` - 追踪伏笔状态

## 🏗️ 架构设计

NovelKit 采用模块化设计，包含以下核心组件：

### 命令系统

- **命令文件**（`commands/*.md`）- 定义 AI 命令的行为和交互流程，使用 Markdown + YAML Front Matter 格式
- **脚本文件**（`scripts/bash/*.sh` 和 `scripts/powershell/*.ps1`）- 执行实际的文件操作和状态管理
- **模板文件**（`templates/*.md`）- 定义生成内容的结构和格式

### 工作流程

1. **初始化阶段** - CLI 工具下载构建产物并初始化项目结构
2. **命令执行** - 在 AI 环境中使用命令，AI 读取命令文件并执行相应脚本
3. **数据管理** - 所有数据以 JSON 格式存储在 `.novelkit/` 目录中
4. **构建发布** - 构建脚本（`build_novelkit.py`）将源文件打包成发布包

### 数据存储

- 状态数据存储在 `.novelkit/memory/` 目录
- 章节、角色、地点等数据使用结构化 JSON 格式
- 支持版本控制和协作编辑

## 📖 文档

- [📋 命令文档](docs/commands.md) - 完整的命令列表和使用说明
- [🔧 构建文档](docs/build.md) - 如何构建和发布 NovelKit
- [🤝 贡献指南](CONTRIBUTING.md) - 如何参与项目开发
- [🐛 问题反馈](https://github.com/t59688/novel-kit/issues) - 报告 Bug 或提出建议

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！请查看 [贡献指南](CONTRIBUTING.md) 了解详情。

## 📄 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。

## 🔗 相关链接

- [GitHub 仓库](https://github.com/t59688/novel-kit)
- [问题追踪](https://github.com/t59688/novel-kit/issues)

---

<div align="center">

**如果这个项目对你有帮助，请给它一个 ⭐ Star！**

Made with ❤️ for novel writers

</div>
