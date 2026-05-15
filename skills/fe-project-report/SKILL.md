---
name: fe-project-report
description: 前端项目探索与报告生成技能。当用户要求分析一个前端项目的结构、生成项目架构报告、探索不熟悉的代码库、进行项目交接或架构摸底时触发。该技能会自动探索项目的路由结构、分析每个页面的功能与接口依赖、统计微服务使用情况、分析页面间跳转关系，最终输出一份完整的项目报告。支持用户选择输出格式：markdown（可读性高，适合 Wiki/文档）、html（含可视化图表和交互，适合浏览器查看）、JSON（结构化数据，适合程序处理或后续集成）。适用于：接到外包项目需要快速了解、项目文档缺失需要逆向梳理、新成员 onboarding、架构评审等场景。
---

# 前端项目分析报告 (FE Project Report)

探索前端项目并生成项目分析报告，支持 **HTML**、**Markdown**、**JSON** 三种输出格式。

## 工作流程

### 阶段零：确认输出格式

开始分析前，先询问用户想要什么格式的报告：

| 格式 | 参数值 | 输出文件 | 适用场景 |
|------|--------|---------|---------|
| **HTML**（默认） | `html` | `project_report.html` | 富文本页面，含样式和 Mermaid 跳转图，适合浏览器查看/分享 |
| **Markdown** | `markdown` | `project_report.md` | 纯文本表格报告，适合嵌入 Wiki、GitHub、飞书文档 |
| **JSON** | `json` | `project_report.json` | 原始结构化数据，适合程序处理或二次加工 |

- 如果用户未指定，默认使用 **HTML** 格式
- 告知用户每种格式的特点，让用户选择
- 如果用户要求"所有格式"或"都要"，按 HTML → Markdown → JSON 依次生成

执行时依次完成以下 6 个阶段，每个阶段完成后输出当前进度。

### 阶段一：检测项目基本信息

1. **读取 `package.json`** — 获取项目名称、`description`、`dependencies` / `devDependencies`
2. **判断前端框架** — 根据依赖确定主要框架：
   - Vue 系列：vue + vue-router / nuxt
   - React 系列：react + react-router / next
   - Angular：@angular/core + @angular/router
   - 其他：umi、svelte、solid 等
3. **记录框架版本和关键依赖**（UI 组件库、HTTP 库、状态管理等）
4. **检查 TypeScript 配置**（`tsconfig.json`）

### 阶段二：发现路由规则

这是最关键的一步。目标是找到项目中的所有页面路由。

**搜索顺序（按优先级）：**

1. 查找静态路由表配置文件：
   - `src/router/index.ts` / `.js`
   - `src/router/routes.ts` / `.js`
   - `src/app-routing.module.ts`（Angular）
   - `config/routes.ts`（UmiJS）
   - `.umirc.ts` 中的 `routes` 字段
   - `app.tsx` 或 `App.tsx` 中的 `<Route>` 定义
2. 如果存在主动路由表，**直接提取所有路径**，记录每个 `path` 关联的 `component`
3. 文件系统路由（没有主动路由表时）：
   - Next.js：`pages/` 或 `app/` 目录结构
   - Nuxt.js：`pages/` 目录结构
   - VitePress：`docs/` 目录 + config 中的 nav/sidebar
   - 其他：扫描 `src/pages/` 或 `src/views/` 下所有文件
4. 检测 **动态路由**：查找 `router.addRoute()` 或动态添加路由的逻辑，记录添加条件和路由路径
5. 记录 `routing_type`（`static` / `file-based` / `hybrid`）

### 阶段三：分析每个页面

对阶段二发现的每个路由，逐个分析其关联的组件文件：

**提取信息：**

1. **页面路径**（route path，如 `/dashboard`）
2. **页面标题** — 按以下优先级查找：
   - 路由配置的 `meta.title`
   - 组件中 `document.title = '...'`
   - 组件模板中的 `<title>`
   - 组件中使用 `useTitle()` 或类似 hook
   - 最后回退：根据路由路径和组件文件名推断中文标题
3. **业务功能描述** — 阅读组件代码，理解该页面做什么（增删改查？展示什么数据？有什么交互？）。用自己的话简洁概括 2-4 句。
4. **依赖的接口** — 扫描页面组件及其导入的 service/api 文件：
   - 搜索 `axios.get`、`axios.post`、`axios.put`、`axios.delete`
   - `fetch(url`、`fetch('`、`fetch("`
   - `request.get/post`
   - `http.get/post`
   - `api.xxx` 调用模式
   - `$http`、`$api` 等自定义封装
   - 读取 service/api 文件中对应函数的实际请求地址
   - 记录完整的请求方法 + 路径
5. **业务域** — 根据路由路径前缀和功能内容划分：
   - `/order/*` → "订单管理"
   - `/user/*`、`/member/*` → "用户管理"
   - `/dashboard` → "数据看板"
   - `/setting*` → "系统设置"
   - 如果路由前缀不明显，根据页面功能内容命名
6. **子页面/子路由**（如果有嵌套路由）

### 阶段四：收集微服务依赖

从阶段三收集到的所有接口路径中提取微服务信息：

1. **解析接口路径结构**，识别微服务名称：
   - 模式：`/microservice-name/rest/of/path` 或 `microservice-name/app/module/action`
   - 第一个路径段通常是微服务/应用名称
2. **按微服务分组**统计：
   - 服务名称
   - 该服务在当前项目中出现的接口数量
   - 列出所有端点路径
   - 被哪些页面使用
3. 记录项目总接口数和涉及的微服务总数

### 阶段五：分析页面跳转关系

扫描所有页面组件（以及相关代码）中的导航逻辑：

**搜索模式：**
- `router.push(...)`、`router.replace(...)`
- `this.$router.push(...)`（Vue Options API）
- `navigate(...)`、`useNavigate()(...)`
- `history.push(...)`、`history.replace(...)`
- `<Link to="...">`（React）、`<router-link to="...">`（Vue）
- `<a href="...">` 指向项目内页面（排除外部链接）
- `window.location.href = '...'`
- `useRouter().push()`

**记录格式：**
```
来源页面 → 目标页面 (触发方式/按钮文案)
```

如果代码中的跳转路径是相对路径，解析为完整的路由路径。

### 阶段六：生成报告

1. 将全部分析结果整理为统一的 JSON 数据结构
2. 写入 `report_data.json`
3. 根据用户选择的格式运行对应的报告生成命令

**数据 JSON 结构：**

```json
{
  "project_name": "项目名称",
  "project_description": "package.json 中的描述",
  "framework": "Vue 3 / React 18 / Next.js 14 / ...",
  "routing_type": "static / file-based / hybrid",
  "total_pages": 12,
  "total_api_calls": 45,
  "total_microservices": 3,
  "pages": [
    {
      "path": "/dashboard",
      "title": "数据看板",
      "component": "src/views/dashboard/index.vue",
      "description": "展示核心业务指标，包含销售额趋势图、订单量统计柱状图、最近交易列表。支持按时间范围筛选数据。",
      "business_domain": "运营管理",
      "sub_routes": ["/dashboard/analysis", "/dashboard/monitor"],
      "api_calls": [
        { "method": "GET", "path": "/trade-enterprise-app/api/dashboard/stats" },
        { "method": "GET", "path": "/trade-enterprise-app/api/dashboard/trend" }
      ],
      "navigates_to": [
        { "target": "/orders", "label": "查看订单详情" },
        { "target": "/users", "label": "点击用户头像" }
      ]
    }
  ],
  "microservices": [
    {
      "name": "trade-enterprise-app",
      "api_count": 23,
      "endpoints": ["/api/dashboard/stats", "/api/orders/list", "/api/orders/detail"],
      "used_by_pages": ["/dashboard", "/orders", "/orders/detail"]
    }
  ],
  "navigations": [
    { "from": "/dashboard", "to": "/orders", "label": "查看订单详情" }
  ]
}
```

**报告生成命令（根据选择的格式）：**

```bash
# HTML（默认，含可视化图表和完整样式）
python <skill_dir>/scripts/generate_report.py report_data.json --format html
# 或简写
python <skill_dir>/scripts/generate_report.py report_data.json

# Markdown（可读性高，适合 Wiki/文档）
python <skill_dir>/scripts/generate_report.py report_data.json --format markdown

# JSON（纯结构化数据，适合程序处理）
python <skill_dir>/scripts/generate_report.py report_data.json --format json
```

**常用选项：**
- `--format html|markdown|json` — 选择输出格式（默认 HTML）
- `-o <文件路径>` — 自定义输出路径
- `--no-open` — 不自动打开浏览器（HTML 格式）

## 注意事项

- **不要分析 `node_modules`、`.git`、`dist`、`build`、`.next` 等目录** — 只在源码目录（`src/`、`app/`、`pages/` 等）中搜索
- 如果代码中有多个 route 配置源（如既有静态路由表又有文件系统路由），以**静态路由表**为主，文件系统路由作为补充
- 对大型项目，优先分析**主要业务页面**，忽略错误页面（404）、登录页、layout 组件等非业务页面
- 接口路径可能包含动态参数（如 `/api/order/:id`），保留参数占位符
- 跳转路径也可能是动态的（如 `router.push({ name: 'orderDetail', params: { id } })`），记录路由名称
- 如果某个阶段的搜索结果为空或不确定，明确标注"未找到"而不是猜测
