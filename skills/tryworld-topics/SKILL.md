---
name: tryworld-topics
description: 基于 aihot.news 最新 AI 资讯，为 AI 口播频道（试界TryWorld · 纸上算法风格）产出选题清单。由 $tryworld-koubo 在模式 B 下路由调用；被显式点名「只要选题」时也可直接触发。产出为 3-8 个候选选题（含选题名、角度、素材与原文链接、流量原理命中、优先级），可直接进入 $tryworld-paper 流程做片。
---

# AIHOT 口播选题

为当前频道的 `content.domain` 领域做选题：先拉取选题数据源（默认 AIHOT，可替换），再按频道选题规则（`content.topic_rules`）筛出值得做的选题清单。默认主题为试界TryWorld 的 AI 口播频道。

## 内容主题

选题规则默认来自 tryworld-paper/themes/content-default.json 的 topic_sources、topic_rules、platforms 字段。换领域/品牌时修改内容主题 JSON，无需改本 SKILL.md。

## 流程

1. **拉数据**：运行 `python -X utf8 scripts/fetch_aihot.py`（跨平台；默认拉最新日报 + 最近 7 天精选，落盘到 `work/aihot/`；`--days` 只能映射到 24h 或 7d，`--take` 是 `--limit` 的兼容别名）。需要完整精选历史镜像时运行 `python -X utf8 scripts/fetch_aihot.py --sync-selected --rebaseline`，之后用 `--sync-selected` 做增量。统一使用这个 Python 脚本，不再提供 PowerShell 回退。无 Python 环境时按 `references/api.md` 的 v1 端点用 curl 拉取（**必须带 UA 和 Accept-Encoding: gzip**）。
2. **读规则**：打开 `references/selection-rules.md`，按频道定位与筛选清单处理数据。
3. **筛选题**：从拉到的条目中选出 3-8 个候选，每条标注：选题名、为什么选（命中哪个增长原理）、核心素材与原文链接、切入角度、优先级。
4. **输出**：用 `references/selection-rules.md` 的模板输出选题清单（markdown，人话，不暴露接口细节）。用户选中某个选题后，可继续给口播稿骨架或直接转入 `$tryworld-paper` 流程。
5. **维护**：用户确认开做的选题追加到 `references/done-topics.md`（日期、选题、形式），避免重复选题。

## 数据源要点

- 默认走**精选**（`/api/v1/items?mode=selected&window=7d&limit=100`）；用户明确说"日报"才走 `/api/v1/dailies/latest`；明确说"全部/所有/完整"且需要历史全集才用精选快照 + 增量。
- `/api/v1/items` 只覆盖最近 24 小时或 7 天；更早的日报用 `/api/v1/dailies/{YYYY-MM-DD}`。
- 每条保留 `links.original`（原文链接）；站内阅读页用 `links.aihot`。摘要为 LLM 生成，引用前回原文核对。
- 时间展示转北京时间 + 相对时间（"2 小时前"），不展示 ISO 串。
- 完整端点与错误处理见 `references/api.md`。

## 资源

- `scripts/fetch_aihot.py`：唯一数据拉取入口，一键拉取并生成 UTF-8 报告（支持 `/api/v1`、gzip、ETag、snapshot/changes）
- `references/api.md`：AIHOT v1 API 端点、字段映射、路由规则、输出规范
- `references/selection-rules.md`：试界TryWorld 选题规则与输出模板（默认；可通过 content.topic_rules 替换）
- `references/done-topics.md`：已做选题清单（持续维护）
