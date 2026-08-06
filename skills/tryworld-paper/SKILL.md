---
name: tryworld-paper
description: Create branded 试界TryWorld AI-knowledge videos in the fixed "Paper Algorithm" (纸上算法) style with HyperFrames. Input is a Chinese voiceover script and optional images; output is a 16:9 horizontal video with Azure YunxiNeural (真·云希) voiceover, word-synced captions, ink/paper animations and unified transitions, an always-visible anti-counterfeit red seal, plus horizontal (4:3) and vertical (3:4) cover images and platform-optimized titles for Bilibili/Douyin/Xiaohongshu. Use when the user provides an AI 科普/教程/内容解读/知识分享 script and wants a TryWorld/试界 branded video, asks for the 纸上算法/Paper Algorithm style, or wants a consistent script-to-video pipeline with covers and titles.
---

# TryWorld-Paper Algorithm（试界-纸上算法）

为试界TryWorld 制作 AI 知识类视频。所有产出必须遵守本文件与 `references/style-system.md` 锁定的设计系统，任何一条都不允许为了省事而让步。

## 锁定品牌契约（不可更改）

- 平台名：**试界TryWorld**（视频、封面、标题统一使用）
- 画幅：横屏 1920x1080；口播时长最长约 10 分钟（短可到抖音 30 秒），口播稿过长必须先提炼核心精华压缩，时长与质量并重
- 配音：**Azure YunxiNeural（真·云希）**，用 `scripts/tts_yunxi.py` 合成
- 风格：**纸上算法 Paper Algorithm**（科学手稿 + 中文印刷传统）
- 防伪：右上角朱红"试界原创"印章全程常驻显示（`assets/seal.svg`），必须用根层常驻覆盖实现（`data-start="0"`、`data-duration` = 全片时长），禁止只放在章节首幕；印章为保护区，与文字、内容、动画保持距离，不重叠、不贴近
- 水印：禁止任何"试界TryWorld 纸上算法"文字水印（视频右下角、封面一律不得出现）；印章是唯一水印
- 交付物：主视频（画面内烧录字幕）、横版封面（1920x1440，4:3）、竖版封面（1080x1440，3:4）、3-5 个平台标题、字幕/时间轴
- 默认结尾：每期视频结尾固定使用——"我是试界TryWorld，持续把 AI 讲清楚，让每个普通人都看得懂、用得上。觉得这条视频有用，点个赞，也欢迎关注，谢谢大家，下期见。"（口播与画面同步）

## 启动前必读

1. 读 `references/style-system.md` —— 视觉契约。编写任何 HTML/CSS 前必须先读，并作为 hyperframes 流程中的 DESIGN.md 使用。
2. 读 `references/workflow.md` —— 生产流程与命令，按顺序执行。
3. 编写构图时遵循 hyperframes skill（`$hyperframes`）的全部规则。
4. 生成标题前读 `references/titles.md`。

## 工作流

1. **输入并通读理解**：口播稿（文本或 .txt/.md 文件）与可选图片。先通读全文，理解主题、受众、核心结论与章节结构；图片缺失时跳过图片场景，不允许降级风格。
2. **优化并净化脚本**：按流量第一性原理优化口播稿（共鸣选题带流量、认可攒赞、槽点引评论、嘴替促转发、价值认同涨粉），再按"活人感改稿七遍"清模型腔与注水（看谁在说 → 检查推进/删注水 → 拆表演性中文 → 听中文节奏 → 清硬禁项 → 核现实 → 查结尾，固定签名保留），随后清除写作标记/结构标签（如"一、开场钩子"、"（插入截图）"）——标记不得以原文出现在视频中（不朗读、不上字幕、不显示），按意图转化为实际表达。净化后正文与平台标题必须运行 `scripts/check_prose.py` 清零硬禁项。规则见 workflow.md。
3. **交付优化稿并等待确认**：净化后正文先通过 `scripts/check_prose.py`（硬禁项清零），再把优化后的口播稿完整展示给用户审阅，附简明优化说明（改了什么、为什么）、元素落点清单（钩子/干货/槽点/嘴替/价值收尾）与数据来源清单；**未获用户确认前，禁止进入配音/构图/渲染**。
4. **分段**：按净化后口播时长分段，每章 40-90 秒；不足 1 分钟不分章；口播目标不超过约 10 分钟，超长稿先提炼核心精华压缩再分段；标记章节标题、关键词、数据点、图片提示。
5. **配音**：`python scripts/tts_yunxi.py <净化后的脚本> --out work/audio` 生成云希配音、分段时间与合并音轨。
6. **时间轴**：字幕时间轴来自 `work/audio/sentences.json`（edge-tts 句级时间戳，已带绝对时间）；如需词级时间轴可用 `npx hyperframes transcribe`（依赖 whisper，可选）。
7. **场景规划**：按章节规划场景与节奏（开场-讲解-数据-小结），数据/对比/流程优先规划为动态图表场景，避免大段静态文字；先声明节奏模式再写 HTML。
8. **构图**：把 `assets/` 复制进项目；按 style-system.md 与 hyperframes 规则编写 16:9 主构图。每个场景必须有入场动画与转场；除末场外禁止退场动画。
9. **检查**：`npx hyperframes lint`、`npx hyperframes validate`、`npx hyperframes inspect --strict` 全部通过——错误与警告清零，禁止元素重叠、文字溢出/出画布/截断等排版错误；封面构图同样核验。
10. **渲染前核验**：渲染前必须按 workflow.md 的"渲染前核验清单"逐项对照本文件与 style-system.md 的全部要求，确认无误后才允许渲染；任一项不满足先修改再渲染，避免返工。
11. **渲染**：`npx hyperframes render --fps 30 --quality high` 输出主视频（先 `--quality draft` 预览确认，再 high 出片）。
12. **封面**：按 style-system.md 封面系统独立设计 4:3 与 3:4 静态构图（深墨海报，与视频浅纸面两套视觉语言；禁止截取主视频画面），渲染后取帧为 PNG。
13. **标题**：按 titles.md 生成 3-5 个候选，标注平台推荐与命中的增长原则（共鸣/认可/槽点/嘴替/价值认同）；候选标题同守硬禁词（禁冒号/破折号/翻案句/黑话/模型路标），生成后自检或跑 `scripts/check_prose.py` 清零。
14. **交付**：主视频（烧录字幕）、横竖封面、标题、字幕文件统一放入 `outputs/`。

## 质量门禁（不通过不交付）

- `lint` / `validate` / `inspect` 全部通过。
- 排版：禁止元素重叠、文字溢出/出画布/截断等低级错误；`inspect --strict` 错误与警告清零才可交付，封面同样核验。
- 防伪间距：右上角印章与文字/内容/动画保持安全距离，禁止重叠或贴近；视频与封面均适用。
- 场景间必须转场，禁止硬切；每个场景元素必须有入场动画（hyperframes 硬性规则）。
- 动效丰富度：禁止连续 3 秒静止；每场 ≥1 ambient、≥3 层视觉、≥2 焦点；动效遵守安全护栏——不入侵字幕/印章区、同屏并发 ≤3、只用风格内变换、无诡异运动与重叠。
- 无文字水印：视频与封面禁止出现"试界TryWorld 纸上算法"或类似文字水印；印章是唯一水印。
- 印章常驻：印章必须以根层覆盖实现并全程可见，渲染后抽查首/中/尾帧确认。
- 对比度：正文 4.5:1，大字（24px+ 或 19px+ 粗体）3:1，只能在本风格色板内调整。
- 确定性：禁止 `Math.random()` / `Date.now()`；动画 repeat 必须有限值。
- 配音：句子只允许在句号/问号/感叹号处停顿；`tts_yunxi.py` 会自动规整文本并按句切分，禁止句子中间产生停顿或卡顿。
- 时长：口播最长约 10 分钟；超长稿必须提炼核心精华压缩（保留主线/结论/数据亮点，砍掉重复铺垫与次要细节），时长与质量并重。
- 脚本净化：写作标记/结构标签（如"一、开场钩子"）不得以原文出现在视频中——不朗读、不上字幕、不显示为画面文字，必须转化为实际表达。
- 口播优化：脚本须按流量第一性原理优化（共鸣选题/认可点赞/槽点评论/嘴替转发/价值认同涨粉），成片须具备钩子、干货、讨论点、嘴替句与价值收尾；结尾固定使用默认签名；数据须场景化"人话"解读、不冷冰冰堆数据；专业人认可价值、普通人觉得用得上看完；全程高价值，能留住观众。
- 数据真实性：口播稿所有数据点须有来源（原稿出处或标注"待核实"），确认时附数据来源清单；禁止编造数据。
- 用户确认闸门：优化后的口播稿必须先完整展示给用户审阅并获确认，未经确认禁止生成视频。
- 字幕：主视频烧录字幕并与配音同步；字幕与画面动画文字不得重复——画面展示核心内容时该句字幕可隐藏或精简，同一信息同屏只呈现一次；字幕文件同步交付。
- 数据可视化：数据/对比/流程必须用风格统一的动态图表表达（等宽数字 + 朱红强调 + 墨水蓝网格，GSAP/SVG 实现），禁止大段静态文字或原图图表。
- 标题增长：每个候选标题必须命中至少一个增长原则（共鸣/认可/槽点/嘴替/价值认同），禁止为凑数生成无钩子标题。
- 渲染前核验：渲染前必须逐项对照本文件与 style-system.md/workflow.md 的全部规则并确认通过，未通过禁止渲染。
- 封面：必须独立构图设计，禁止从主视频截帧或裁切充当封面；封面采用深墨海报视觉，与视频浅纸面画面保持两套语言，避免被平台判定为截图。
- 防 AI 味：禁止紫蓝霓虹、黑底光效、通用科技字体、机械匀速动画、空荡背景、每句整屏大字。
- 活人感：净化后口播稿正文与 `titles.txt` 硬禁项清零——动作级禁令：翻案腔（先立误解再推翻抬价，含 9+ 变形）、三项以上同构排比、抒情借喻（抽象名词配具体动词）、动词名词化；标点：破折号全禁、冒号仅引出直接原话可用；硬停词"说白了/说穿了/先说结论"；模型洞察路标；商业与模型黑话（绝对禁词 + 语境判断词两档，清单见 `scripts/check_prose.py`）；`check_prose.py` 失败不交付。

## 语音回退（按序）

1. 默认：`scripts/tts_yunxi.py`（edge-tts，Azure YunxiNeural，需联网）。
2. 用户提供云希音频：直接导入并转写，跳过合成步骤。
3. 离线兜底：`npx hyperframes tts --voice zm_yunxi`（音色偏平，需告知用户差异）。

## 资源

- `references/style-system.md`：设计契约（色板/字体/动效/转场/字幕/图片处理/防伪/封面）
- `references/workflow.md`：详细生产流程与命令
- `references/titles.md`：平台标题规则
- `scripts/tts_yunxi.py`：云希配音管线
- `scripts/check_prose.py`：活人感硬禁项检查脚本（TryWorld 改造版，源自 KKKKhazix/human-writing v1.1.0，MIT；禁令上移到修辞动作级）
- `assets/paper-grain.svg`：纸纹叠加层
- `assets/seal.svg`：朱红"试界原创"印章
