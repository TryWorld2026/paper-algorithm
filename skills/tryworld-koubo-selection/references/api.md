# AIHOT API 参考（aihot.virxact.com）

## 先决条件

- 调 `/api/public/*` 必须带浏览器 UA，否则 403：
  `Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36`
- PowerShell 用 `System.Net.WebClient` + `Encoding=UTF8`（见 `scripts/fetch_aihot.ps1`）；非 Windows 用 curl `-H "User-Agent: ..."`。
- 匿名访问，无需 Key；限流 600 req/min/IP，串行调用。

## 端点

| 端点 | 用途 | 主要参数 |
|---|---|---|
| `/api/public/daily` | 最新日报 | 无 |
| `/api/public/daily/{YYYY-MM-DD}` | 指定日期日报 | path: date |
| `/api/public/dailies?take=N` | 日报归档列表 | take 1-180 |
| `/api/public/items` | AI 动态 | mode / category / since / take / cursor / q |

items 参数：`mode=selected|all`（默认 selected）；`category=ai-models|ai-products|industry|paper|tip`；`since=ISO-8601`（最近 7 天硬上限，未来时间 400）；`take` 上限 100；`q` 关键词（≥2 字符，title+中文 title+中文 summary 三列匹配）；`cursor` 翻页（不透明 token，原样透传）。

## 路由规则

- 宽问题（"今天 AI 圈""过去 24 小时大新闻""最近 AI"）→ `mode=selected&since=<语义窗>`。
- 明确说"日报"→ `daily`（UTC 0 点切片成品；当天北京时间 08:00 前可能还没有，404 时拉昨天）。
- 明确说"全部/完整/所有/全量"→ `mode=all`。
- 分类/时间窗/关键词可正交组合（如 `mode=selected&category=paper&q=RAG&since=7天前`）。
- 用户问"最近 N 天 X"时显式带 `since=<N 天前>`。

## 返回字段（items）

必有：`id` / `title` / `url` / `source`；可空：`title_en` / `summary` / `publishedAt` / `category`。

## 输出规范

- 展示中文 `title`；`title_en` 仅当用户要求英文或 title 为空。
- `publishedAt`（ISO UTC）转北京时间 + 相对时间（"2 小时前"）。
- 每条保留 `url`，方便回溯原文；`summary` 为 LLM 生成，引用前回原文核对。
- 不暴露端点路径、raw 参数、限流、cursor 等基础设施细节；数据来源最多写"数据来自 aihot.virxact.com"。

## 错误处理

- 404 `No daily report available yet.` → 拉昨天日报。
- 400：date 非 `YYYY-MM-DD`；mode/category/since/take 参数非法。
- 429：限流，串行 + 间隔重试。