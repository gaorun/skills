---
name: obsidian-memo
description: >
  在 Obsidian 中创建和查询个人记忆，帮助 AI 避免重复犯错。
  当用户说"记一下"、"记着"、"记住这个"时创建记忆；
  当用户说"查一下"、"之前xxx"、"以往xxx"、"上次xxx"或者执行任务时缺乏相关背景资料时查询记忆；
  当用户说"整理记忆"时合并相似记忆并清理已合并内容。
  当检测到用户在同一会话中反复纠正同一问题（2次及以上），自动创建记忆。
  创建记忆前会检查是否存在相似记忆，存在则追加而非重复创建。
  依赖 obsidian-cli，如果该工具不可用则技能不触发。
---

# Obsidian Memo

在 Obsidian 中创建和查询个人记忆，帮助 AI 在长期协作中避免重复犯错。

## 依赖检查

本技能依赖 `obsidian-cli`。在执行任何操作前，先运行 `obsidian help` 确认 CLI 可用。如果命令失败，告知用户需要安装 obsidian-cli 并停止执行。

## 自动检测重复纠正

在对话过程中，如果用户纠正了你的错误做法，注意判断：

- 这次纠正的问题是否与之前已纠正的问题属于**同类**（相同技术、相同模式、相同领域）
- 如果是第 2 次及以上纠正同类问题，**自动创建记忆**，无需用户说"记一下"

自动创建时，向用户说明："我注意到你已经多次纠正这类问题，我已经记下来了，下次不会再犯。"

## 创建记忆

当用户说"记一下"或触发自动检测时，执行以下步骤：

### 1. 检查是否存在相似记忆

在创建新记忆前，先查询现有记忆（见"查询记忆"章节的步骤 1-2），对比 description 属性判断是否存在相似或相近的记忆：

- **如果存在相似记忆**：不创建新文件，而是用 `obsidian append` 将新内容追加到已有的记忆文件中。如果新内容导致该记忆的适用范围扩大，更新 description 属性。如果核心主题发生变化，用 `obsidian rename` 重命名文件。
- **如果不存在相似记忆**：继续执行下面的步骤创建新文件。

### 2. 确保目录存在

```bash
obsidian create path="obsidian-memo/.gitkeep" content="" silent
```

如果目录已存在，这一步不会创建新文件，只是确保路径可用。

### 3. 生成文件名

用当前时间戳作为文件名：

```bash
date +%Y-%m-%d-%H-%M-%S
```

假设输出为 `2025-01-15-14-30-45`，则文件路径为 `obsidian-memo/2025-01-15-14-30-45.md`。

### 4. 创建记忆文件

```bash
obsidian create path="obsidian-memo/2025-01-15-14-30-45.md" content="## 正确做法\n（正确的做法）\n\n## 错误做法\n（之前犯的错误）\n\n## 背景\n（补充上下文）" silent
```

### 5. 设置 frontmatter 属性

```bash
obsidian property:set name="tags" value='["obsidian-memo"]' file="obsidian-memo/2025-01-15-14-30-45"
```

```bash
obsidian property:set name="description" value="一句话摘要。适用场景：xxx。关键词：xxx, xxx" file="obsidian-memo/2025-01-15-14-30-45"
```

```bash
obsidian property:set name="read_counter" value="0" file="obsidian-memo/2025-01-15-14-30-45"
```

### description 写法指南

description 的作用是在查询时匹配相关记忆。写得好才能查得到。

**格式：** `一句话摘要。适用场景：xxx。关键词：xxx, xxx, xxx`

- **摘要**：用一句话概括这条记忆的核心内容
- **适用场景**：描述什么时候应该参考这条记忆（"当用户要求xxx时"、"当处理xxx问题时"）
- **关键词**：列出 3-5 个便于匹配的关键词

**示例：**

| 场景     | description                                                                                                        |
| -------- | ------------------------------------------------------------------------------------------------------------------ |
| API 前缀 | "API 请求必须使用 /api/v2 前缀。适用场景：当发起 API 请求时。关键词：API, 前缀, v2, 接口"                          |
| 调试方式 | "使用 debugger 而非 console.log 调试。适用场景：当需要调试代码时。关键词：调试, debugger, 日志"                    |
| 组件库   | "该项目使用 Ant Design Vue 而非 Element UI。适用场景：当引入或使用 UI 组件时。关键词：组件库, Ant Design, Element" |

## 查询记忆

当用户说"查一下"、"之前xxx"、"以往xxx"时，执行以下步骤：

### 1. 确保 Base 文件存在

检查 `obsidian-memo.base` 是否存在。如果不存在，先创建（见"初始化 Base"章节）。

### 2. 查询所有记忆

```bash
obsidian base:query path="obsidian-memo.base" format=md
```

这会返回所有记忆文件的列表，包含文件名和 description 属性。

### 3. 匹配记忆

根据用户的查询意图，在返回的结果中匹配 description 最相关的记忆。可能匹配一条或多条。

### 4. 读取记忆内容

对每条匹配的记忆，用 `obsidian read` 读取完整内容：

```bash
obsidian read path="obsidian-memo/2025-01-15-14-30-45"
```

读取成功后，将该记忆文件的 `read_counter` 属性自增 1：

```bash
obsidian property:read name="read_counter" file="obsidian-memo/2025-01-15-14-30-45"
```

获取当前值后，设置为当前值 + 1：

```bash
obsidian property:set name="read_counter" value=<当前值+1> file="obsidian-memo/2025-01-15-14-30-45"
```

然后将内容呈现给用户。

## 整理记忆

当用户说"整理记忆"时，执行以下步骤：

### 1. 查询所有记忆

按照"查询记忆"章节的步骤获取所有记忆文件列表。

### 2. 识别相似记忆

对比所有记忆的 description 属性，找出内容相似或相近的记忆组。

### 3. 合并记忆

对于每组相似记忆：

1. 创建新的记忆文件（使用当前时间戳命名），将相似记忆的内容合并整理到新文件中
2. 新文件的 description 应覆盖合并前所有记忆的适用场景
3. 设置新文件的 `tags` 为 `["obsidian-memo"]`
4. 设置新文件的 `read_counter` 为合并前各记忆 read_counter 的总和
5. 对被合并的旧记忆文件，用 `obsidian property:set` 在其 tags 中增加 `"merged"` 标记

### 4. 更新 Base

确保 Base 文件的 filters 中排除 tags 包含 "merged" 的记忆（见"初始化 Base"章节）。

## 初始化 Base

如果 `obsidian-memo.base` 不存在，用以下命令创建：

```bash
obsidian create path="obsidian-memo.base" content='filters:\n  and:\n    - file.hasTag("obsidian-memo")\n    - file.inFolder("obsidian-memo")\n    - not:\n        - file.hasTag("merged")\n\nproperties:\n  description:\n    displayName: "Description"\n  read_counter:\n    displayName: "Read Count"\n\nviews:\n  - type: table\n    name: "All Memos"\n    order:\n      - file.name\n      - description\n      - read_counter\n      - file.mtime' silent
```

Base 文件的作用是将所有记忆文件以表格形式展示，便于查询和浏览。

## 记忆文件模板

```markdown
---
description: "一句话摘要。适用场景：xxx。关键词：xxx, xxx, xxx"
tags:
  - obsidian-memo
read_counter: 0
---

## 正确做法

（记录正确的做法）

## 错误做法

（记录之前犯的错误，作为对比）

## 背景

（可选：补充上下文信息）
```
