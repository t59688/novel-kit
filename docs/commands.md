# 命令列表

## Writer 管理

| 命令 | 文件 | 功能 |
|------|------|------|
| `/novel.writer.new` | `writer-new.md` | 创建新 writer（交互式或快速生成） |
| `/novel.writer.list` | `writer-list.md` | 列出所有 writers |
| `/novel.writer.show` | `writer-show.md` | 查看 writer 详情 |
| `/novel.writer.switch` | `writer-switch.md` | 切换活动 writer |
| `/novel.writer.update` | `writer-update.md` | 更新 writer 配置 |

## 章节管理

| 命令 | 文件 | 功能 |
|------|------|------|
| `/novel.chapter.new` | `chapter-write.md` | 创建新章节 |
| `/novel.chapter.plan` | `chapter-plan.md` | 规划章节内容 |
| `/novel.chapter.write` | `chapter-write.md` | 撰写章节 |
| `/novel.chapter.review` | `chapter-review.md` | 审查章节 |
| `/novel.chapter.polish` | `chapter-polish.md` | 润色章节 |
| `/novel.chapter.confirm` | `chapter-confirm.md` | 确认章节完成 |

## 角色管理

| 命令 | 文件 | 功能 |
|------|------|------|
| `/novel.character.new` | `character-new.md` | 创建角色 |
| `/novel.character.list` | `character-list.md` | 列出所有角色 |
| `/novel.character.show` | `character-show.md` | 查看角色详情 |
| `/novel.character.update` | `character-update.md` | 更新角色信息 |

## 地点管理

| 命令 | 文件 | 功能 |
|------|------|------|
| `/novel.location.new` | `location-new.md` | 创建地点 |
| `/novel.location.list` | `location-list.md` | 列出所有地点 |
| `/novel.location.show` | `location-show.md` | 查看地点详情 |
| `/novel.location.update` | `location-update.md` | 更新地点信息 |
| `/novel.location.map` | `location-map.md` | 查看地点地图 |

## 势力管理

| 命令 | 文件 | 功能 |
|------|------|------|
| `/novel.faction.new` | `faction-new.md` | 创建势力 |
| `/novel.faction.list` | `faction-list.md` | 列出所有势力 |
| `/novel.faction.show` | `faction-show.md` | 查看势力详情 |
| `/novel.faction.update` | `faction-update.md` | 更新势力信息 |
| `/novel.faction.members` | `faction-members.md` | 查看势力成员 |
| `/novel.faction.relationships` | `faction-relationships.md` | 查看势力关系 |

## 剧情管理

### 主线剧情

| 命令 | 文件 | 功能 |
|------|------|------|
| `/novel.plot.main.new` | `plot-main-new.md` | 创建主线剧情 |
| `/novel.plot.main.list` | `plot-main-list.md` | 列出主线剧情 |
| `/novel.plot.main.show` | `plot-main-show.md` | 查看主线剧情详情 |
| `/novel.plot.main.update` | `plot-main-update.md` | 更新主线剧情 |

### 支线剧情

| 命令 | 文件 | 功能 |
|------|------|------|
| `/novel.plot.side.new` | `plot-side-new.md` | 创建支线剧情 |
| `/novel.plot.side.list` | `plot-side-list.md` | 列出支线剧情 |
| `/novel.plot.side.show` | `plot-side-show.md` | 查看支线剧情详情 |
| `/novel.plot.side.update` | `plot-side-update.md` | 更新支线剧情 |

### 伏笔管理

| 命令 | 文件 | 功能 |
|------|------|------|
| `/novel.plot.foreshadow.new` | `plot-foreshadow-new.md` | 创建伏笔 |
| `/novel.plot.foreshadow.list` | `plot-foreshadow-list.md` | 列出所有伏笔 |
| `/novel.plot.foreshadow.track` | `plot-foreshadow-track.md` | 追踪伏笔状态 |

## 项目设置

| 命令 | 文件 | 功能 |
|------|------|------|
| `/novel.setup` | `novel-setup.md` | 初始化项目目录结构 |
| `/novel.constitution.create` | `constitution-create.md` | 创建小说宪法 |
| `/novel.constitution.show` | `constitution-show.md` | 查看小说宪法 |
| `/novel.constitution.update` | `constitution-update.md` | 更新小说宪法 |
| `/novel.constitution.check` | `constitution-check.md` | 检查是否符合宪法 |

## 命令文件结构

每个命令文件包含：

1. **YAML Front Matter**
   ```yaml
   ---
   description: 命令描述
   scripts:
     sh: .novelkit/scripts/bash/manager.sh action "$ARGUMENTS"
     ps: .novelkit/scripts/powershell/manager.ps1 -Action Action -Json "$ARGUMENTS"
   ---
   ```

2. **用户输入处理**
   ```markdown
   ## User Input
   ```text
   $ARGUMENTS
   ```
   ```

3. **交互流程定义**
   - AI 的行为规范
   - 交互步骤
   - 输出格式

## 添加新命令

1. 在 `commands/` 创建 `.md` 文件
2. 定义 YAML front matter 和脚本调用
3. 编写交互流程
4. 如需新脚本操作，添加对应脚本
5. 构建测试：`python build_novelkit.py cursor linux`
6. 测试命令：`novel-kit init test-project`
