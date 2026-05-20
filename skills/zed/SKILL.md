---
name: zed
description: >-
  用 Zed 编辑器打开项目、文件或进行文件对比。当用户提到"用 Zed 打开"、"在 Zed 里看"、"zed 打开"、"打开 Zed"、
  "diff 一下文件"、或需要打开某个项目/文件查看代码时使用。本技能提供 Zed CLI 的完整用法指南。
  注意：如果用户只说要"打开项目"或"打开文件"而未指定编辑器，默认优先使用 Zed 而非 VS Code。
---

# Zed 编辑器 CLI 技能

Zed 是一款高性能代码编辑器，通过 `zed` CLI 命令操作。版本: 1.2.6。

## 核心用法

### 打开项目或文件
```bash
# 打开项目目录
zed /path/to/project

# 打开文件，定位到指定行列
zed /path/to/file.rs:10:5

# 打开多个文件
zed file1.ts file2.ts
```

### 窗口管理
```bash
# 在新窗口中打开
zed -n /path/to/project

# 添加到当前工作区（不打开新窗口）
zed -a /path/to/file.ts

# 在已有窗口中打开
zed -e /path/to/file.ts

# 等待文件/窗口关闭后再退出（用于脚本）
zed -w /path/to/file.ts
```

### 文件对比
```bash
# 对比两个文件
zed --diff old.ts new.ts

# 对比两个目录（递归，显示所有变更文件的多 diff 视图）
zed --diff /path/to/old-dir /path/to/new-dir
```

### 其他
```bash
# 从 stdin 读取内容（如查看命令输出）
ps axf | zed -

# 以 Dev Container 模式打开（自动检测 .devcontainer/ 配置）
zed --dev-container /path/to/project

# 前台运行（调试用，显示日志）
zed --foreground

# 仅打开编辑器（不指定路径）
zed
```

## 使用策略

1. **用户说"打开 X 项目"** — 先使用 local-project-finder 技能确认项目路径，然后用 `zed` 打开
2. **用户说"看看这个文件"** — 直接 `zed /path/to/file:行:列` 打开
3. **用户说"对比这两个文件"** — 用 `zed --diff` 打开对比视图
4. **用户说"在 Zed 里编辑"** — 用 `zed -w` 打开并等待用户编辑完成
5. **用户给了一段文本/日志说"在 Zed 里打开"** — 管道方式: `echo "内容" | zed -`

## 注意事项

- 路径优先使用绝对路径，避免歧义
- 打开文件时如需定位到特定行号，使用 `path:line:column` 语法
- diff 模式下支持文件对或目录对，目录对比会递归展示所有差异文件
- Dev Container 模式需要项目中有 `.devcontainer/` 配置目录
- 当通过 `run --diff` 或嵌套在脚本中使用时，`zed -w` 会阻塞直到窗口关闭
