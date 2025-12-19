# 构建说明

## 构建命令

```bash
python build_novelkit.py cursor linux   # Linux 版本
python build_novelkit.py cursor win     # Windows 版本
```

构建产物位于 `dist/cursor-{platform}/` 目录。

## 构建过程

1. **复制元空间文件**
   - `memory/config.json` → `.novelkit/memory/config.json`
   - `templates/` → `.novelkit/templates/`
   - `scripts/bash/` 或 `scripts/powershell/` → `.novelkit/scripts/`

2. **复制命令文件**
   - `commands/*.md` → `.cursor/commands/novel.*.md`
   - 文件名转换：`writer-new.md` → `novel.writer.new.md`

3. **生成目录结构**
   ```
   dist/cursor-linux/
   ├── .novelkit/
   │   ├── memory/
   │   ├── templates/
   │   └── scripts/
   └── .cursor/
       └── commands/
   ```

## 文件转换规则

命令文件名转换：
- 去掉 `.md` 扩展名
- 如果以 `novel-` 开头，去掉前缀
- 按 `-` 分割，用 `.` 连接
- 添加 `novel.` 前缀

示例：
- `writer-new.md` → `novel.writer.new.md`
- `chapter-plan.md` → `novel.chapter.plan.md`
- `novel-setup.md` → `novel.setup.md`

## 平台特定处理

- **Linux**：只复制 `scripts/bash/` 目录
- **Windows**：只复制 `scripts/powershell/` 目录

## 配置文件

支持的 AI 环境和平台在 `build-config.json` 中配置：

```json
{
  "supported_ais": ["cursor"],
  "supported_platforms": ["linux", "win"]
}
```

**注意**：此配置文件仅用于构建脚本（`build_novelkit.py`）和 CI/CD（GitHub Actions）。CLI 工具面向用户，不依赖此配置文件。

## GitHub Actions 自动构建

推送 tag 时自动构建：

```bash
git tag v0.0.2
git push origin v0.0.2
```

GitHub Actions 会：
1. 读取 `build-config.json` 获取支持的 AI 环境列表
2. 自动构建所有 AI 环境和平台的组合
3. 打包成 ZIP 文件
4. 上传到 GitHub Release

构建产物命名：`novel-kit-{ai-env}-{platform}-{version}.zip`

例如，如果配置了 `cursor` 和 `claude`，会自动构建：
- `novel-kit-cursor-linux-v0.0.2.zip`
- `novel-kit-cursor-win-v0.0.2.zip`
- `novel-kit-claude-linux-v0.0.2.zip`
- `novel-kit-claude-win-v0.0.2.zip`
