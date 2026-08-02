# 生产流程（按顺序执行）

环境前提：Node >= 22、FFmpeg（含 ffprobe，加入 PATH；`winget install Gyan.FFmpeg` 可安装，装后用 `npx hyperframes doctor` 验证）、Python 3.10+、`edge-tts`（`python -m pip install edge-tts`）、hyperframes CLI（`npx hyperframes`）。转写需要 whisper（`npx hyperframes transcribe` 首次使用会给出安装提示）。

## 1. 输入与分段

输入：口播稿文本（可直接粘贴或 .txt/.md 路径）+ 可选图片目录。

口播稿约定（保证配音无生硬停顿/卡顿）：

- 句子以句号/问号/感叹号/省略号结束；句内不要为排版硬换行（脚本会自动把句子中间的换行合并，不会产生停顿）。
- 段落之间留空行；段落会在句号边界切分合成，停顿只出现在句子结束处。
- 脚本里的 markdown 标题行（`#`）是结构标记，不会被朗读；`**`、反引号、列表符等符号会自动去除，不要依赖它们表达语气。
- 若某句实际读起来仍不顺，检查该句标点（过长句可拆成两句）。

分段规则（时长不限，按口播时长自适应）：

- 每章 40-90 秒口播（约 180-400 字）。
- 不足 1 分钟：不分章，单场景直接做。
- 1-3 分钟：1-3 个章节。
- 3-10 分钟：3-6 个章节。
- 10 分钟以上：按每章 40-90 秒推算章节数，逐章递增。
- 每章标记：章节标题、3-5 个关键词、2-4 个数据点、图片/图表提示、重音句。
- 章节结构建议：开场钩子（0-15s）→ 概念讲解 → 数据/示例 → 小结。每章结尾留一个可做转场的"结论句"。

产出：`plan.json`（或 Markdown 场景规划表），含每章标题、口播段落、场景数、节奏模式。

## 2. 配音（云希）

```powershell
python scripts/tts_yunxi.py script.txt --out work/audio
```

输出：

- `work/audio/segment-XXX.mp3`：每段落一轨
- `work/audio/narration.mp3`：合并全片
- `work/audio/segments.json`：每段 start/duration，用于章节时间轴

参数：默认 `--rate +8%`（语速偏快一档，可按内容微调 +5%~+15%）、`--voice zh-CN-YunxiNeural`。

用户提供云希音频时：跳过本步，直接用其音频，记录章节切点。

## 3. 字幕时间轴

字幕同步使用 `work/audio/sentences.json`（edge-tts 句级时间戳，脚本已按段落偏移换算为绝对时间）。每句含 start/end/text，用于字幕淡入与关键词高亮窗口。

可选：如需词级时间轴（更细的高亮），安装 whisper 后运行 `npx hyperframes transcribe work/audio/narration.mp3`。

## 4. 场景规划

在写 HTML 前声明节奏，例如：

`开场快-讲解慢-数据重音-小结慢-章节墨染`

每个章节 1-3 个场景：章节标题卡、讲解场景、数据卡/图片场景。长视频每 8-15 秒必须有一个动效重音。

## 5. 构图

- 项目结构：`npx hyperframes init <slug> --non-interactive`（或用现有项目）。
- 把 `assets/` 的纸纹、印章、水印复制进项目。
- 主构图 `index.html`：1920x1080；多章节用子构图（sub-composition）组织。
- 先按 style-system.md 写静态布局（hero frame），再加 GSAP 入场；遵守 hyperframes 全部规则（时间轴注册、data-track-index、无 repeat:-1、无随机、场景转场等）。
- 字幕与配音同步：逐词时间轴驱动关键词高亮；不逐词闪动普通句子。
- 防伪：水印元素常驻；印章元素按 45-60s 间隔或章节起始时间点出现（用精确时间位置，不用随机）。

## 6. 检查

```powershell
npx hyperframes lint
npx hyperframes validate
npx hyperframes inspect --samples 15
```

对比度警告在色板内调整（正文 4.5:1，大字 3:1）。溢出问题优先用 max-width/字号/换行解决；装饰性元素用 `data-layout-ignore`。长视频建议跑 animation-map 检查节奏与死区。

## 7. 渲染主视频

```powershell
npx hyperframes render --fps 30 --quality high --output outputs/tryworld_<slug>.mp4
```

迭代用 `--quality draft`。确认总时长 ≈ 口播时长 + 头尾留白（通常 +2-4s）。

## 8. 封面

制作两个静态构图（可用主构图截帧，但推荐独立构图保证信息密度）：

- `covers/horizontal.html`：1920x1080
- `covers/vertical.html`：1080x1920

构图规则见 style-system.md 封面系统。渲染后取帧：

```powershell
npx hyperframes render --output covers/h.mp4
ffmpeg -y -i covers/h.mp4 -frames:v 1 outputs/cover_16x9.png
npx hyperframes render --output covers/v.mp4
ffmpeg -y -i covers/v.mp4 -frames:v 1 outputs/cover_9x16.png
```

封面必须含：主标题、2-4 个信息块、品牌条、水印、印章。

## 9. 标题

按 `references/titles.md` 生成 3-5 个候选，标注平台推荐，输出 `outputs/titles.txt`。

## 10. 交付清单

`outputs/` 下应有：

- `tryworld_<slug>.mp4`（主视频）
- `cover_16x9.png`、`cover_9x16.png`
- `titles.txt`（含平台推荐）
- `narration.mp3` + `transcript.json`（配音与字幕时间轴，便于二次编辑）
- `plan.json`（场景规划，便于复用章节结构）

## 常见问题

- edge-tts 报错/无网络：用 `npx hyperframes tts --voice zm_yunxi` 兜底并告知用户音色差异，或改用用户提供的音频。
- 转写时间轴与章节对不上：用 segments.json 的 start/duration 校准，而不是逐句估算。
- 字体不支持：按 style-system.md 回退链换字，不换风格。
- 渲染时长异常：检查 data-duration 与 timeline 长度、音频时长；确认没有空 tween 撑时长。
- 配音出现不自然停顿/卡顿：检查脚本是否有句子中间换行或段落被硬切；脚本已按句切分，合成边界只在句号/问号/感叹号处。
