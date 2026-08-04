---
name: tryworld-topics
description: 基于 aihot.virxact.com 最新 AI 资讯，为 AI 口播频道（试界TryWorld · 纸上算法风格）产出选题。当用户说"帮我选题""我要选题""给我几个选题""口播选题""做口播选题""这周做什么口播""最近有什么值得做的 AI 选题""AI 口播选题""本周 AI 圈有什么可讲的""做个 AI 资讯盘点"等，或需要从 AI 新闻里筛选题、写选题建议、做周更栏目选题时使用。产出为 3-8 个候选选题（含选题名、角度、素材与原文链接、流量原理命中、优先级），可直接进入 tryworld-paper 流程做片。
---

# AIHOT 口播选题

为试界TryWorld 的 AI 口播频道做选题：先拉取 AIHOT 最新 AI 资讯，再按频道选题规则筛出值得做的选题清单。

## 流程

1. **拉数据**：运行 `scripts/fetch_aihot.ps1`（Windows PowerShell；拉最近 7 天精选 + 最新日报 + 五分类，落盘到 `work/aihot/`）。非 Windows 环境按 `references/api.md` 的端点用 curl 拉取（**必须带浏览器 UA**，否则 403）。
2. **读规则**：打开 `references/selection-rules.md`，按频道定位与筛选清单处理数据。
3. **筛选题**：从拉到的条目中选出 3-8 个候选，每条标注：选题名、为什么选（命中哪个增长原理）、核心素材与原文链接、切入角度、优先级。
4. **输出**：用 `references/selection-rules.md` 的模板输出选题清单（markdown，人话，不暴露接口细节）。用户选中某个选题后，可继续给口播稿骨架或直接转入 `$tryworld-paper` 流程。
5. **维护**：用户确认开做的选题追加到 `references/done-topics.md`（日期、标题），避免重复选题。

## 数据源要点

- 默认走**精选**（`items?mode=selected&since=<时间窗>`）；用户明确说"日报"才走 `daily`；明确说"全部/所有/完整"才走 `mode=all`。
- items 只返回最近 7 天；更早走日报存档 `daily/{YYYY-MM-DD}`。
- 每条保留 `url`（原文链接），摘要为 LLM 生成，引用前回原文核对。
- 时间展示转北京时间 + 相对时间（"2 小时前"），不展示 ISO 串。
- 完整端点与错误处理见 `references/api.md`。

## 资源

- `scripts/fetch_aihot.ps1`：一键拉取并生成 UTF-8 报告（Windows）
- `references/api.md`：AIHOT API 端点、路由规则、输出规范
- `references/selection-rules.md`：试界TryWorld 选题规则与输出模板
- `references/done-topics.md`：已做选题清单（持续维护）