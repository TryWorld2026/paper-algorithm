# 试界-纸上算法 TryWorld-Paper Algorithm

> 一页会动的算法笔记 —— 把 AI 知识口播稿变成风格统一的横屏视频、横竖封面与平台标题。

![风格](https://img.shields.io/badge/风格-纸上算法-C0452F)
![配音](https://img.shields.io/badge/配音-Azure%20YunxiNeural-2E5E8C)
![画幅](https://img.shields.io/badge/画幅-1920x1080-1C1916)
![状态](https://img.shields.io/badge/状态-已启用-8FAF8C)

## 这是什么

`tryworld-paper-algorithm`（试界-纸上算法 TryWorld-Paper Algorithm）是试界TryWorld 的视频生产 Skill：输入一篇中文 AI 口播稿（可附图片），自动产出：

- **横屏主视频**（16:9，口播最长约 10 分钟）—— 纸上算法风格，真云希配音，全程烧录字幕；超长稿提炼核心精华压缩
- **横版封面 + 竖版封面**（1920x1440 横 4:3 / 1080x1440 竖 3:4）—— 深墨海报风（与视频浅纸面两套视觉语言），标题 + 信息块，适配 B站/抖音/小红书
- **3-5 个平台标题** —— 按 B站/抖音/小红书分别适配
- 全程统一的品牌水印与"试界原创"防伪印章
- 每期固定的默认结尾签名（试界TryWorld 标准收尾，口播+画面同步）

## 设计契约：纸上算法 Paper Algorithm

设计源头：**科学手稿 + 中文印刷传统**。每一期视频都是一页"会动的算法笔记"，纸面是舞台，墨迹是文字，朱红是重点，印章是签名。

### 色板（4 色锁定，不新增）

| 色 | 值 | 用途 |
|---|---|---|
| 纸面 | `#F4EFE4` | 背景主色 |
| 墨黑 | `#1C1916` | 主文字、线条 |
| 朱红 | `#C0452F` | 唯一强调色：关键词、数字、印章 |
| 墨水蓝 | `#2E5E8C` | 次级批注、图表线 |

### 字体

- 主标题：思源宋体（Noto Serif SC）
- 批注/引用：霞鹜文楷（LXGW WenKai）
- 数据/坐标：等宽字体（JetBrains Mono）

### 动效签名（全片统一）

| 签名 | 感觉 | 缓动 |
|---|---|---|
| 墨落纸 | 主入场 | `power3.out` |
| 笔写入 | 批注/小元素 | `sine.inOut` |
| 盖章 | 数字/结论/印章 | `back.out(1.4)` |

转场统一为**墨染过渡**：前场景被墨色浸染溶解，新场景从纸面浮现；章节间留纸面空场。

### 动态图表

数据/对比/流程用风格统一的动态图表表达：数字滚动盖章、柱状墨迹增长、折线一笔描画、进度环、对比卡片；等宽数字 + 朱红强调 + 墨水蓝网格，GSAP/SVG 实现，避免大段静态文字配解说。

## 配音质量保障

- **真云希**：Azure YunxiNeural（edge-tts 本地合成，无需 API Key）
- **默认语速** +8%，可按内容微调 +5%~+15%
- **防卡顿机制**：文本自动规整（清除 markdown、合并句中换行），按句切分合成——停顿只允许出现在句号/问号/感叹号处，句子中间永不硬断
- 句级时间戳（`sentences.json`）直接驱动字幕同步，不依赖 whisper

## 工作流

```text
口播稿 → 读稿理解 → 第一性原理优化 → 净化写作标记 → 用户确认优化稿 → 句级切分 → 云希配音 → 句级时间轴
   → 章节/场景规划 → HyperFrames 构图 → lint/validate/inspect --strict
   → 渲染前核验 → 渲染 16:9 主视频 → 横竖封面 → 平台标题 → outputs/ 交付
```

## 使用方式

在 Codex 会话中给出口播稿（纯文字或 .txt/.md，可附图片）：

```text
用 $tryworld-paper-algorithm 把这篇口播稿做成视频，加上横竖封面和标题。
```

可选输入：图片目录（AI 概念图 / 截图 / 图表，会自动"纸面化"处理）。

## 目录结构

```text
tryworld-paper-algorithm/
├── SKILL.md                    # 主说明：品牌契约、工作流、质量门禁
├── agents/
│   └── openai.yaml             # UI 元数据
├── references/
│   ├── style-system.md         # 视觉契约（色板/字体/动效/封面）
│   ├── workflow.md             # 生产流程与命令
│   └── titles.md               # 平台标题规则
├── scripts/
│   └── tts_yunxi.py            # 云希配音管线（句级切分 + 拼接 + 时间轴）
└── assets/
    ├── paper-grain.svg         # 纸纹叠加层
    ├── seal.svg                # 朱红"试界原创"印章
    └── watermark.svg           # 单行品牌水印
```

## 环境要求

- Node.js >= 22
- FFmpeg（含 ffprobe，加入 PATH；`winget install Gyan.FFmpeg`）
- Python 3.10+，`pip install edge-tts`
- HyperFrames CLI（`npx hyperframes`）

运行 `npx hyperframes doctor` 可一键检查环境。

## 防伪标识

视频与封面统一携带：

- 右下角单行水印 **试界TryWorld 纸上算法**（保护区，字幕与内容不得贴近）
- 右上角每 45-60 秒（或每章节开头）盖朱红**试界原创**印章（保护区，内容不得覆盖）

## 许可

本仓库暂未附带开源许可证；在添加许可证之前，默认保留所有权利。
