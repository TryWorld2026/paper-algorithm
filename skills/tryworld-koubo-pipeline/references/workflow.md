 工作流明细（tryworld-koubo-pipeline）

## 模式判定规则

按以下顺序判定，命中即停：

1. 子命令关键词："只要选题" → 子流程 S1；"只要写稿" → S2；"只优化""只出优化稿""不出片" → 模式 A 到闸门为止。
2. 选题意图："帮我选题""这周做什么口播""最近有什么值得做的 AI 选题""AI 口播选题""本周 AI 圈""做个 AI 资讯盘点" → 模式 B。
3. 稿子输入：用户粘贴口播稿正文（通常 >300 字），或给出 .md/.txt 稿子文件路径 → 模式 A。
4. 无法判定时，向用户确认："你是要选题，还是要直接优化现有稿子？"

## 模式 A：直接给稿 → 优化 → 出片

1. 通读稿子，理解主题、受众、核心结论、章节结构。
2. 进入 `$tryworld-paper-algorithm`：
   - 优化并净化（流量第一性原理；清除章节标签等写作标记）；
   - 展示优化稿 + 优化说明 + 元素落点 + 数据来源清单；
   - **闸门：等用户确认**；未确认禁止配音/构图/渲染。
3. 确认后按 paper-algorithm 流程：分段 → 云希配音 → 场景规划 → 构图 → lint/validate/inspect → 渲染 → 封面 → 标题。
4. 交付到项目 `outputs/`，并补 `发布计划.txt`。

## 模式 B：选题 → 写稿 → 优化 → 出片

### B1 拉数据与产出选题

1. 进入 `$tryworld-koubo-selection`：
   - 运行 `scripts/fetch_aihot.ps1`（默认 7 天、100 条，落盘 `work/aihot/`）；
   - 读 `references/selection-rules.md`；
   - 产出 3-8 个候选选题（选题名、为什么选、核心素材+原文链接、切入角度、优先级、命中原理）。

### B2 去重判定（以工作区实际成片为准）

扫描 `E:\Codex口播视频` 一级子文件夹，并**递归**查找其中的 outputs 目录（项目可能嵌套，如 deepseek-v4-flash）：

```powershell
Get-ChildItem -LiteralPath "E:\Codex口播视频" -Directory | ForEach-Object {
  $proj = $_.FullName
  $outs = Get-ChildItem -LiteralPath $proj -Recurse -Directory -Filter "outputs" -ErrorAction SilentlyContinue
  $done = $false
  foreach ($o in $outs) {
    $mp4 = @(Get-ChildItem -LiteralPath $o.FullName -Filter *.mp4 -ErrorAction SilentlyContinue)
    $png = @(Get-ChildItem -LiteralPath $o.FullName -Filter *.png -ErrorAction SilentlyContinue)
    if ($mp4.Count -ge 1 -and $png.Count -ge 2) { $done = $true; break }
  }
  [PSCustomObject]@{ Folder = $_.Name; Done = $done }
}
```

判定规则：

- 候选选题按关键词与该文件夹名/文件夹内口播稿标题做包含匹配（如"中美 AI"命中 `zhongmei-ai`）。
- 命中且该 outputs 目录同时存在 ≥1 个 *.mp4 与 ≥2 个封面 png（横竖两张）→ **已做，排除**，并同步记录到 `tryworld-koubo-selection/references/done-topics.md`（缓存）。
- 未命中，或命中的 outputs 缺视频/缺封面 → **未做，可推荐**。

### B3 闸门 1：选题清单

- 展示清单，停，等用户挑选；用户可"换一批"或给自定义主题。
- 用户未选择前，禁止进入写稿。

### B4 写稿初稿

按 SKILL.md"写稿规范"：

- 标准版 2800-3000 字；短版（30-60 秒）按用户要求。
- 开场钩子 → 3-5 层结构 → 结论 + 固定签名。
- 数据带原文链接；未核实标"待核实"。
- 写作标记不进正文。
- 初稿不单独停（按用户设定：只在选题与优化稿两处停）。

### B5 优化与闸门 2

- 进入 `$tryworld-paper-algorithm` 优化净化，展示优化稿 + 说明 + 数据来源。
- **闸门 2：等用户确认**；确认后出片，未确认禁止继续。

### B6 去重记录

- 用户确认开做后，向 `tryworld-koubo-selection/references/done-topics.md` 追加一行（日期、选题、形式）。

## 子命令

- S1 只要选题：B1 → B2 → B3，停止。
- S2 只要写稿：用户给主题/素材 → 按写稿规范产出初稿 → 展示，停止。
- S3 只优化不出片：模式 A 步骤 1-2，停止。

## 交付清单与发布计划

成片交付 `outputs/` 应包含：

- 主视频（*.mp4，烧录字幕）
- 口播稿（含日期，如 `2026-08-04_主题_口播稿.md`）
- 封面_横版4x3.png / 封面_竖版3x4.png
- 平台标题文案.txt
- 配音文本_script.txt、narration.mp3、transcript.json（时间轴）、plan.json
- 发布计划.txt（固定内容）

发布计划.txt 内容模板：

```
试界TryWorld · 平台发布计划
小红书：中午 12:30
抖音：晚上 19:30
B站：晚上 20:30
微信视频号：晚上 20:30
```

## 异常处理

- AIHOT 请求 403/失败：检查 User-Agent；重试一次；仍失败则说明并暂停。
- 无当日日报：拉昨日日报或改用精选条目。
- 用户对选题清单不满意：换一批（重拉或放宽时间窗/分类）或接受自定义主题。
- 稿子超过 10 分钟：按 paper-algorithm 规则压缩核心精华。
- 用户中途改需求（如"改成短版""只做选题"）：重新判定模式并调整流程。
- 用户提供的稿子含写作标记/占位符：交给 paper-algorithm 净化，不在入口处理。

## 测试要点

- T1 模式 A：贴稿 → 优化稿确认（不渲染）。
- T2 去重：已做（有视频+封面）排除；未做保留。
- T3 模式 B 全链：选题 → 闸门1 → 写稿 → 优化稿 → 闸门2。
- T4 交付：outputs/ 含视频、口播稿、横竖封面、标题、发布计划.txt。
- T5 子命令：S1/S2/S3 只做对应步骤。
- T6 校验：quick_validate 通过；文件 UTF-8 带 BOM。