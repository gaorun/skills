#!/usr/bin/env python3
"""Generate project_report.html from collected frontend project data."""

import json
import sys
import argparse
import textwrap
import webbrowser
from pathlib import Path


def load_data(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def escape_html(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def build_mermaid(navigations):
    if not navigations:
        return ""
    lines = ["graph LR"]
    for nav in navigations:
        fr = nav.get("from", "")
        to = nav.get("to", "")
        label = nav.get("label", "")
        fr_id = "P" + fr.replace("/", "_").replace("-", "_").replace(":", "").replace(".", "_") or "P_root"
        to_id = "P" + to.replace("/", "_").replace("-", "_").replace(":", "").replace(".", "_") or "P_root"
        if label:
            lines.append(f'    {fr_id}["{escape_html(fr)}"] -->|"{escape_html(label)}"| {to_id}["{escape_html(to)}"]')
        else:
            lines.append(f'    {fr_id}["{escape_html(fr)}"] --> {to_id}["{escape_html(to)}"]')
    return "\n".join(lines)


def make_card(page, idx):
    badges = ""
    api_count = len(page.get("api_calls", []))
    sub_routes = page.get("sub_routes", [])

    api_rows = ""
    for api in page.get("api_calls", []):
        method = api.get("method", "GET")
        color = {"GET": "#22c55e", "POST": "#3b82f6", "PUT": "#f59e0b", "DELETE": "#ef4444", "PATCH": "#8b5cf6"}.get(method.upper(), "#6b7280")
        api_rows += f'<tr><td style="width:80px"><span style="display:inline-block;padding:2px 8px;border-radius:4px;background:{color};color:#fff;font-size:12px;font-weight:600">{escape_html(method.upper())}</span></td><td><code>{escape_html(api.get("path",""))}</code></td></tr>'

    nav_rows = ""
    for nav in page.get("navigates_to", []):
        target = escape_html(nav.get("target", ""))
        label = escape_html(nav.get("label", ""))
        nav_rows += f'<li><span class="nav-arrow">→</span> <a href="#page-{target.replace("/", "_")}">{target}</a>{" · " + label if label else ""}</li>'

    sub = ""
    if sub_routes:
        sub = '<div style="margin:8px 0 0"><strong>子路由：</strong>' + " ".join(f'<code>{escape_html(s)}</code>' for s in sub_routes) + "</div>"

    return f'''
    <div class="page-card" id="page-{escape_html(page.get("path","")).replace("/","_")}">
      <div class="page-header">
        <span class="page-index">#{idx + 1}</span>
        <span class="page-domain-tag">{escape_html(page.get("business_domain","未划分"))}</span>
        <h3 class="page-title">{escape_html(page.get("title","未命名页面"))}</h3>
        <span class="page-path">{escape_html(page.get("path",""))}</span>
      </div>
      <div class="page-body">
        <div class="page-meta">
          <div><strong>组件：</strong><code>{escape_html(page.get("component",""))}</code></div>
          {sub}
        </div>
        <div class="page-desc">
          <p>{escape_html(page.get("description","暂无描述"))}</p>
        </div>
        {f'<div class="page-apis"><h4>接口依赖 ({api_count})</h4><table class="api-table"><tbody>{api_rows}</tbody></table></div>' if api_rows else ''}
        {f'<div class="page-navs"><h4>跳转到</h4><ul>{nav_rows}</ul></div>' if nav_rows else ''}
      </div>
    </div>'''


def build_html(data):
    project_name = escape_html(data.get("project_name", "未知项目"))
    project_desc = escape_html(data.get("project_description", ""))
    framework = escape_html(data.get("framework", "未知"))
    routing_type = escape_html(data.get("routing_type", "未知"))
    total_pages = data.get("total_pages", len(data.get("pages", [])))
    total_api = data.get("total_api_calls", 0)
    total_ms = data.get("total_microservices", len(data.get("microservices", [])))

    pages = data.get("pages", [])
    microservices = data.get("microservices", [])
    navigations = data.get("navigations", [])

    cards = "\n".join(make_card(p, i) for i, p in enumerate(pages))

    ms_rows = ""
    for ms in microservices:
        name = escape_html(ms.get("name", ""))
        count = ms.get("api_count", len(ms.get("endpoints", [])))
        endpoints = ms.get("endpoints", [])
        used_by = ms.get("used_by_pages", [])
        ep_list = "<ul>" + "".join(f'<li><code>{escape_html(e)}</code></li>' for e in endpoints) + "</ul>"
        used_list = " ".join(f'<a href="#page-{p.replace("/","_")}"><code>{escape_html(p)}</code></a>' for p in used_by) if used_by else "<span style='color:#999'>未知</span>"
        ms_rows += f'''
        <tr>
          <td><strong>{name}</strong></td>
          <td style="text-align:center"><span class="count-badge">{count}</span></td>
          <td style="max-width:400px">{ep_list}</td>
          <td>{used_list}</td>
        </tr>'''

    nav_count = len(navigations)
    mermaid_def = build_mermaid(navigations)
    mermaid_section = ""
    if navigations:
        mermaid_section = f'''
    <section class="section">
      <h2>页面跳转关系图</h2>
      <p style="color:#666;margin-bottom:16px">共 {nav_count} 条跳转关系</p>
      <div class="mermaid-wrapper">
        <pre class="mermaid">
{mermaid_def}
        </pre>
      </div>
    </section>'''

    ms_section = ""
    if ms_rows:
        ms_section = f'''
    <section class="section">
      <h2>微服务统计</h2>
      <p style="color:#666;margin-bottom:16px">共 {total_ms} 个微服务，{total_api} 个接口</p>
      <div class="table-wrapper">
        <table class="data-table">
          <thead>
            <tr><th>服务名称</th><th style="width:100px">接口数量</th><th>端点列表</th><th>使用页面</th></tr>
          </thead>
          <tbody>
            {ms_rows}
          </tbody>
        </table>
      </div>
    </section>'''

    page_list_rows = ""
    for i, p in enumerate(pages):
        path = escape_html(p.get("path", ""))
        title = escape_html(p.get("title", ""))
        domain = escape_html(p.get("business_domain", ""))
        desc = escape_html(p.get("description", ""))
        api_n = len(p.get("api_calls", []))
        page_list_rows += f'<tr><td><a href="#page-{path.replace("/","_")}"><code>{path}</code></a></td><td>{title}</td><td><span class="domain-tag-sm">{domain}</span></td><td>{desc[:60]}{"..." if len(desc)>60 else ""}</td><td style="text-align:center">{api_n}</td></tr>'

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{project_name} - 项目分析报告</title>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<style>
  :root {{
    --bg: #f5f7fa;
    --card: #ffffff;
    --primary: #3b82f6;
    --primary-light: #eff6ff;
    --text: #1e293b;
    --text-secondary: #64748b;
    --border: #e2e8f0;
    --radius: 12px;
  }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Noto Sans SC', sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; }}
  .container {{ max-width: 1100px; margin: 0 auto; padding: 24px 20px; }}
  .hero {{ background: linear-gradient(135deg, #1e293b 0%, #334155 100%); color: #fff; padding: 48px 40px; border-radius: var(--radius); margin-bottom: 32px; }}
  .hero h1 {{ font-size: 28px; font-weight: 700; margin-bottom: 8px; }}
  .hero p {{ color: #94a3b8; font-size: 15px; }}
  .hero-meta {{ display: flex; gap: 24px; flex-wrap: wrap; margin-top: 24px; }}
  .hero-meta-item {{ display: flex; flex-direction: column; }}
  .hero-meta-item .label {{ font-size: 12px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; }}
  .hero-meta-item .value {{ font-size: 20px; font-weight: 700; color: #fff; }}
  .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 32px; }}
  .stat-card {{ background: var(--card); border-radius: var(--radius); padding: 24px; border: 1px solid var(--border); }}
  .stat-card .stat-value {{ font-size: 32px; font-weight: 700; color: var(--primary); }}
  .stat-card .stat-label {{ font-size: 14px; color: var(--text-secondary); margin-top: 4px; }}
  .section {{ background: var(--card); border-radius: var(--radius); padding: 32px; margin-bottom: 24px; border: 1px solid var(--border); }}
  .section h2 {{ font-size: 20px; font-weight: 600; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 2px solid var(--primary); display: inline-block; }}
  .table-wrapper {{ overflow-x: auto; }}
  .data-table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
  .data-table th {{ background: #f8fafc; text-align: left; padding: 12px 16px; font-weight: 600; color: var(--text-secondary); font-size: 13px; border-bottom: 2px solid var(--border); }}
  .data-table td {{ padding: 12px 16px; border-bottom: 1px solid var(--border); vertical-align: top; }}
  .data-table tr:hover td {{ background: #f8fafc; }}
  .data-table code {{ background: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-size: 13px; }}
  .count-badge {{ display:inline-block; background: var(--primary-light); color: var(--primary); padding:2px 12px; border-radius:20px; font-weight:600; font-size:14px; }}
  .domain-tag-sm {{ display:inline-block; background: #f0f9ff; color: #0369a1; padding:2px 8px; border-radius:4px; font-size:12px; }}
  .page-card {{ background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); margin-bottom: 20px; overflow: hidden; }}
  .page-header {{ display: flex; align-items: center; gap: 12px; padding: 16px 20px; background: #f8fafc; border-bottom: 1px solid var(--border); flex-wrap: wrap; }}
  .page-index {{ display:inline-flex; align-items:center; justify-content:center; width:28px; height:28px; border-radius:50%; background: var(--primary); color:#fff; font-size:13px; font-weight:600; }}
  .page-domain-tag {{ display:inline-block; background: #f0fdf4; color: #15803d; padding:2px 10px; border-radius:4px; font-size:12px; font-weight:500; }}
  .page-title {{ font-size: 16px; font-weight: 600; flex: 1; }}
  .page-path {{ font-size: 13px; color: var(--text-secondary); font-family: monospace; }}
  .page-body {{ padding: 20px; }}
  .page-meta {{ margin-bottom: 12px; font-size: 14px; color: var(--text-secondary); }}
  .page-meta code {{ background: #f1f5f9; padding: 2px 6px; border-radius: 4px; }}
  .page-desc {{ background: #f8fafc; padding: 12px 16px; border-radius: 8px; margin-bottom: 12px; font-size: 14px; color: var(--text); line-height: 1.7; border-left: 3px solid var(--primary); }}
  .page-apis h4, .page-navs h4 {{ font-size: 14px; font-weight: 600; margin-bottom: 8px; color: var(--text-secondary); }}
  .api-table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  .api-table td {{ padding: 6px 8px; border-bottom: 1px solid var(--border); }}
  .api-table tr:last-child td {{ border-bottom: none; }}
  .page-navs ul {{ list-style: none; padding: 0; }}
  .page-navs li {{ padding: 4px 0; font-size: 14px; }}
  .nav-arrow {{ color: var(--primary); font-weight: 700; margin-right: 4px; }}
  a {{ color: var(--primary); text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  .mermaid-wrapper {{ background: #f8fafc; border-radius: 8px; padding: 24px; overflow-x: auto; text-align: center; }}
  .footer {{ text-align: center; padding: 32px 0; color: var(--text-secondary); font-size: 13px; }}
  ul {{ padding-left: 20px; }}
  li {{ margin: 4px 0; }}
</style>
</head>
<body>
<div class="container">
  <div class="hero">
    <h1>{project_name}</h1>
    {f"<p>{project_desc}</p>" if project_desc else ""}
    <div class="hero-meta">
      <div class="hero-meta-item"><span class="label">前端框架</span><span class="value">{framework}</span></div>
      <div class="hero-meta-item"><span class="label">路由类型</span><span class="value">{routing_type}</span></div>
    </div>
  </div>

  <div class="stats-grid">
    <div class="stat-card"><div class="stat-value">{total_pages}</div><div class="stat-label">页面总数</div></div>
    <div class="stat-card"><div class="stat-value">{total_api}</div><div class="stat-label">接口总数</div></div>
    <div class="stat-card"><div class="stat-value">{total_ms}</div><div class="stat-label">微服务数</div></div>
    <div class="stat-card"><div class="stat-value">{nav_count}</div><div class="stat-label">页面跳转关系</div></div>
  </div>

  <section class="section">
    <h2>页面清单</h2>
    <p style="color:#666;margin-bottom:16px">共 {total_pages} 个页面</p>
    <div class="table-wrapper">
      <table class="data-table">
        <thead><tr><th>路径</th><th>页面标题</th><th>业务域</th><th>功能描述</th><th style="width:80px">接口数</th></tr></thead>
        <tbody>
          {page_list_rows}
        </tbody>
      </table>
    </div>
  </section>

  {ms_section}

  {mermaid_section}

  <section class="section">
    <h2>页面详情</h2>
    <p style="color:#666;margin-bottom:16px">每个页面的功能描述、接口依赖和跳转关系</p>
    {cards}
  </section>

  <div class="footer">
    <p>由 FE Project Report 技能自动生成 · {__import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
  </div>
</div>
<script>mermaid.initialize({{startOnLoad:true,theme:'base',themeVariables:{{primaryColor:'#3b82f6',primaryBorderColor:'#3b82f6',lineColor:'#94a3b8',fontSize:'14px'}}}});</script>
</body>
</html>'''


def main():
    parser = argparse.ArgumentParser(description="Generate frontend project report HTML")
    parser.add_argument("data_file", help="Path to JSON data file")
    parser.add_argument("-o", "--output", default="project_report.html", help="Output HTML file path")
    parser.add_argument("--no-open", action="store_true", help="Do not open the report in browser")
    args = parser.parse_args()

    data = load_data(args.data_file)
    html = build_html(data)

    output_path = Path(args.output).resolve()
    output_path.write_text(html, encoding="utf-8")
    print(f"✅ Report generated: {output_path}")
    print(f"   Pages: {len(data.get('pages', []))} | APIs: {data.get('total_api_calls', 0)} | Microservices: {len(data.get('microservices', []))}")

    if not args.no_open:
        webbrowser.open(output_path.as_uri())
        print(f"   Opened in browser")


if __name__ == "__main__":
    main()
