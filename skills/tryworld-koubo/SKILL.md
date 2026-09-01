---
name: tryworld-koubo
description: 试界TryWorld AI 口播视频的统一定位入口，覆盖口播全流程（选题/写稿/优化/出片）。涉及口播的请求都应触发：做口播/口播视频/口播稿/写口播稿/帮我选题/口播选题/这周做什么口播/AI 资讯盘点，或直接粘贴口播稿要求优化出片。自动识别两种模式：①直接给稿 → $tryworld-paper 优化并出片；②要选题 → $tryworld-topics 拉 AIHOT 资讯产选题清单 → 挑选 → 写稿 → 优化 → 出片。子命令：只要选题/只要写稿/只优化不出片。交付附四平台推荐发布时间。无需同时引用其他技能。
---

# TryWorld 口播工作流总入口

统一入口，自动路由。用户无需同时引用 `$tryworld-topics`、`$tryworld-paper` 或 `$hyperframes`。

## 触发词

以下请求都应触发本技能（不限于此表）：

- **做口播**：我要做口播 / 帮我做口播 / 做口播 / 想做口播 / 做一期口播 / 口播视频
- **口播稿**：口播稿 / 写口播稿 / 帮我写口播稿 / 直接粘贴口播稿正文 / 给出 .md/.txt 稿子文件要求优化出片
- **选题**：帮我选题 / 我要选题 / 口播选题 / 给我几个选题 / 这周做什么口播 / 最近有什么值得做的 AI 选题 / 本周 AI 圈有什么可讲的
- **资讯盘点**：做个 AI 资讯盘点 / AI 资讯盘点

## 内容主题

出片前确认内容主题（默认 	ryworld-paper/themes/content-default.json）。内容主题定义选题域、受众、写稿规范、平台列表等。换品牌/换领域时复制此 JSON 并修改——流水线逻辑不变。用户说「用 <主题名> 内容主题」时切换。

```json
{
  "domain": "你的领域",
  "audience": "你的目标受众",
  "topic_sources": ["rss", "manual"],
  "topic_rules": "你的选题筛选标准",
  "tone": "你的写作语调",
  "standard_length_chars": [2000, 3000],
  "platforms": ["你的目标平台"],
  "topic_dedup_dir": "你的成片目录",
  "writing_rules": "tryworld 或 custom"
}
```

## 模式判定

- 输入包含口播稿正文或稿子文件（.md/.txt），且意图是"优化/出片" → **模式 A**
- 输入是选题意图（"帮我选题""这周做什么口播"等） → **模式 B**
- 用户明确"只要选题 / 只要写稿 / 只优化不出片" → 执行对应子命令后停止

## 模式 A：直接给稿 → 优化 → 出片

1. 通读口播稿，理解主题、受众、核心结论与结构。
2. 转入 `$tryworld-paper` 完整流程：优化并净化（含活人感改稿七遍）→ 硬禁项检查（`../tryworld-paper/scripts/check_prose.py` 清零）→ **闸门：展示优化稿等用户确认** → 配音/构图/渲染/封面/标题 → 交付。
3. 交付时按"交付物"补发布计划。

## 模式 B：选题 → 写稿 → 优化 → 出片

1. 调 `$tryworld-topics`：运行其 `scripts/fetch_aihot.ps1` 拉数据，读 `references/selection-rules.md`，产出 3-8 个候选选题。
2. **去重（以工作区实际成片为准）**：扫描 `content.topic_dedup_dir`（内容主题 JSON 定义，默认 `E:\Codex口播视频`）各一级子文件夹，候选选题按关键词与该文件夹名/口播稿标题匹配；若对应文件夹 `outputs/` 同时存在成片视频（*.mp4）与横竖封面（cover_4x3.png / cover_3x4.png 或等价命名）→ 判定已做，从清单排除；反之保留。命令见 `references/workflow.md`。
3. **闸门 1：展示选题清单，停，等用户挑选**（用户可要求换一批或给自定义主题）。
4. 按选中选题 + 素材链接写初稿（规范见"写稿规范"）。
5. 转入 `$tryworld-paper` 优化净化 → **闸门 2：展示优化稿等确认** → 出片。
6. 用户确认开做后，同步更新 `tryworld-topics/references/done-topics.md`（仅作缓存，不作判定依据）。

## 写稿规范（模式 B 初稿）

- 标准版字数从内容主题 JSON 的 `standard_length_chars` 读取（默认 2500-2800 字，约 9-10 分钟，口播语速按约 260 字/分钟估算；成品时长以实际配音为准，超过上限按 paper 规则压缩）；用户指定短版时从 `short_length_seconds` 读取。
- 结构：开场钩子（0-15 秒）→ 3-5 层讲解 → 结论/收尾 + 固定签名（签名语从主题 JSON 的 `brand.sign_off` 读取，不在本文件中写死）。
- 数据点必须带原文来源；无法核实标"待核实"；禁止编造。
- 写作标记（章节标签等）不进入正文，由 paper-algorithm 优化时净化。

### 写稿方法论

完整规则见 `references/writing-methodology.md`（活人感改稿、说话位置、材料自检、硬禁项定义等）。

**边界**：写稿方法论指导写作风格，不覆盖 `check_prose.py` 硬门禁。用户替换方法论时，`check_prose.py` 的禁令仍然生效。在内容主题 JSON 中设置 `"writing_rules": "custom"` 和 `"writing_methodology": "<路径>"` 可替换为自定义方法论。

**默认方法论是试界TryWorld 的核心资产（护城河）。** 用户可以替换为自己的方法论，但流水线门禁（确认闸门、活人感门禁、交付核验）不可关闭。

## 子命令

- "只要选题"：执行模式 B 步骤 1-3，到闸门 1 为止。
- "只要写稿"：给主题/素材 → 直接写初稿 → 展示初稿。
- "只优化不出片"：执行模式 A 步骤 1-2，到优化稿确认为止。

## 交付物（成片）

- 主视频（烧录字幕）、口播稿/文案、横竖封面、平台标题、字幕时间轴
- **发布计划.txt**（固定内容）：小红书 中午 12:30 / 抖音 晚上 19:30 / B站 晚上 20:30 / 微信视频号 晚上 20:30
- **成片交付后自动发通知邮件**：运行 `scripts/notify_delivery.ps1 -ProjectDir <项目目录>`，邮件含产物路径（视频/横竖封面/平台标题）+ 四平台发布时间提醒；凭证未配置时跳过，不阻塞交付。详见 `references/workflow.md`。

## 活人感门禁（不通过不进闸门）

- 净化后口播稿正文与 `titles.txt` 必须硬禁项清零：运行 `python -X utf8 "$env:USERPROFILE\.agents\skills\tryworld-paper\scripts\check_prose.py" <正文或标题文件>`，失败项改写为普通句子后重跑，清零才允许展示优化稿闸门。
- 范围边界：`发布计划.txt`、邮件正文、文件名、数据来源清单不受标点禁令限制。

## 工程约定

- 每个新项目在 `content.topic_dedup_dir`（内容主题 JSON 定义）建独立子文件夹（`<slug>`，如 `zhongmei-ai`），产物进 `work/` 与 `outputs/`。
- 出片阶段完全复用 `$tryworld-paper`，不复制其内容。
- 音色：默认流程不询问，用当前主题的默认音色（默认主题为云希）；用户主动要求换声音（女声/男声/换个音色等）时，把该偏好带入 paper 流程，由 paper 按「音色选择（静默默认，按需试听）」规则用稿子开头合成试听供用户挑选。

## 资源

- `references/workflow.md`：两种模式详细步骤、去重扫描命令、写稿细节、异常处理
- `scripts/notify_delivery.ps1`：成片交付邮件通知（调用 `$qq-email` 发信）
- `../tryworld-paper/scripts/check_prose.py`：活人感硬禁项检查脚本（TryWorld 改造版，源自 KKKKhazix/human-writing v1.1.0，MIT；禁令上移到修辞动作级）

### 品牌适配边界

- 本入口当前默认试界品牌与发布计划。`tryworld-paper` 支持通过主题文件替换出片品牌值；但写稿方法论、topics 选题定位、发布计划模板与 AIHOT 依赖仍是试界视角。换品牌时需同步调整本技能、`tryworld-topics` 的选题规则，或改用自定义素材。
