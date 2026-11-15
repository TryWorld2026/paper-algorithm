# AIHOT API 参考（aihot.news v1）

## 先决条件

- Base URL：`https://aihot.news`
- 匿名访问，无需 API Key；所有请求带明确的 `User-Agent`。
- 规范做法是运行 `scripts/fetch_aihot.py`。脚本已内置 gzip、ETag、304 缓存、429/503 重试和报告生成。
- 自行实现时，请求头至少包含：
  - `User-Agent: Mozilla/5.0 (compatible; paper-algorithm/1.1)`
  - `Accept: application/json`
  - `Accept-Encoding: gzip`

## 端点

| 端点 | 用途 | 主要参数 |
|---|---|---|
| `/api/v1/dailies/latest` | 最新日报 | 无 |
| `/api/v1/dailies/{YYYY-MM-DD}` | 指定上海日历日期日报 | path: date |
| `/api/v1/dailies?limit=N` | 日报归档索引 | limit 1–180 |
| `/api/v1/items` | 最近滚动窗口动态 | mode / category / window / by / q / limit / cursor |
| `/api/v1/selected/snapshot` | 精选全集快照（首次 bootstrap） | fields / limit / page |
| `/api/v1/selected/changes` | 精选增量变更 | cursor / limit |

### `/api/v1/items`

- `mode=selected|all`，默认 `selected`。
- `window=24h|7d`，只支持这两个滚动窗口。
- `limit=1..100`，默认 50；本技能的默认取 100。
- `category=ai-models|ai-products|industry|paper|tip|opinion` 可筛选。
- `by=timeline|published`，默认 `timeline`。
- `q` 为标题/摘要关键词，2–200 个字符。
- `cursor` 是滚动窗口的游标，不应跨天持久化。需要完整精选镜像时改用 snapshot + changes。

## v1 返回结构

### 日报

日报接口返回包层：

```json
{
  "schemaVersion": 1,
  "report": {
    "date": "2026-11-15",
    "lead": {"title": "...", "leadParagraph": "..."},
    "sections": [
      {
        "label": "...",
        "items": [
          {"title": "...", "source": {"name": "..."}, "links": {"original": "...", "aihot": "..."}}
        ]
      }
    ],
    "flashes": []
  }
}
```

**必须读取 `report` 字段**，不能按旧版顶层日报结构解析。`report.lead` 可能为 `null`；`sections`、`flashes` 可能为空数组。

### 条目

`items` 数组中的每条至少包含：

```json
{
  "id": "...",
  "title": "...",
  "originalTitle": "... 或 null",
  "summary": "... 或 null",
  "source": {"name": "..."},
  "links": {
    "original": "https://...",
    "aihot": "https://aihot.news/..."
  },
  "publishedAt": "... 或 null",
  "discoveredAt": "...",
  "category": "... 或 null",
  "score": 0,
  "selected": true,
  "reason": "..."
}
```

字段映射规则：

- `url` → `links.original`
- `permalink` → `links.aihot`
- `title_en` → `originalTitle`
- `source` → `source.name`
- 旧日报里的 `sourceName` → `source.name`
- `reason` 只在 `/api/v1/items` 中稳定返回；snapshot/changes 不保证带它

代码只把上述 v1 字段作为写入格式；读取时可兼容旧字段，但不要依赖旧字段继续生成新数据。

## 精选全集同步

适用于需要维护完整本地精选镜像的场景，例如“所有精选历史条目”，不要用 `/api/v1/items` 拼接历史全集。

### 首次 snapshot

1. 请求 `/api/v1/selected/snapshot?limit=500`。
2. 从第一页读取 `cursor` 和 `asOf`，保留第一页的 `cursor`。
3. 若 `hasMore=true`，用 `nextPage` 作为下一页的 `page` 参数继续请求。
4. 合并所有页的 `items`，直到 `hasMore=false`。
5. 落盘 `selected.json`，结构至少包含 `asOf`、`cursor`、`items`。

第一页请求不要发送 `If-None-Match`；它是一次新的 bootstrap。只有完整快照成功后才用新 cursor 做增量。

### 增量 changes

1. 请求 `/api/v1/selected/changes?cursor=<cursor>&limit=100`。
2. 按顺序应用 `upsert` 和 `remove`。
3. **先应用并落盘，再保存响应里的新 `cursor`**，不要反过来。
4. 若 `hasMore=true`，继续用新 cursor 拉下一页。
5. 收到 `409 snapshot_required`，丢弃当前 cursor，重新执行 snapshot。

`selected.json` 和 `http-cache.json` 放在被 `.gitignore` 忽略的 `work/aihot/`。`--rebaseline` 会删除这两份状态，并强制重新 snapshot，不读取旧 cursor、旧 ETag 或旧域名缓存。

## HTTP 缓存与重试

- 每个完整 URL（含 query）单独记录 ETag 与缓存 body。
- 200 响应保存 ETag；下一次请求同一 URL 时发送 `If-None-Match`。
- 收到 304 时使用本地缓存 body，不覆盖现有状态。
- 响应带 `Content-Encoding: gzip` 时必须解压后再解析 JSON。
- 429/503：读取 `Retry-After`，串行等待；不要并发重试。
- `--watch` 轮询间隔不得小于 60 秒；默认 60 秒。

## 路由规则

- 宽问题（“今天 AI 圈”“过去 24 小时大新闻”“最近 AI”）→ `mode=selected&window=24h|7d`。
- 明确说“日报”→ `/api/v1/dailies/latest`；需要历史日期才用 `/api/v1/dailies/{date}`。
- 明确说“全部/所有/完整”且需要历史全集→ snapshot + changes，不是 `/items` 全量翻页。
- 分类/关键词可正交组合，例如 `mode=selected&category=paper&q=RAG&window=7d`。

## 输出规范

- 展示中文 `title`；`originalTitle` 只在用户要求英文或标题为空时使用。
- `publishedAt` 转北京时间 + 相对时间；`discoveredAt` 保留用于判断发现时间。
- 每条原文链接使用 `links.original`；站内阅读页使用 `links.aihot`。
- 摘要为模型生成，引用前回原文核对。
- 不向最终选题清单暴露端点、cursor、ETag、限流等基础设施细节。

## 错误处理

- 401/403：检查 UA 和请求头；不要重试到死循环。
- 404：日报可能尚未生成；不要猜日期，改用归档索引确认。
- 400：参数非法，修正 `window`、`limit`、日期或 cursor。
- 409：精选 cursor 失效，重新 snapshot。
- 429/503：按 `Retry-After` 串行等待后重试。
