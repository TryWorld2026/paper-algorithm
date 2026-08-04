<p align="center">
  <img src="assets/hero.svg" alt="试界 TryWorld" width="100%">
</p>

<p align="right"><sub><a href="README.md">English</a> · 简体中文</sub></p>

---

**试界 TryWorld · Codex Skills 合集。**

五个技能，一条内容生产线：选题、写稿、出片、深度研究、公众号写作。每个技能独立可用，合在一起便是一套完整的口播工作流——从「这周做什么」到成片交付、自动邮件通知、四平台发布计划。

## 技能

| 编号 | 技能 | 定位 | 产出 |
|---|---|---|---|
| 01 | [tryworld-koubo-pipeline](skills/tryworld-koubo-pipeline/) | 口播统一入口，自动路由 | 全流程交付 · 邮件通知 |
| 02 | [tryworld-paper-algorithm](skills/tryworld-paper-algorithm/) | 纸上算法视频制作 | 主视频 · 封面 · 标题 |
| 03 | [tryworld-koubo-selection](skills/tryworld-koubo-selection/) | AI 资讯选题 | 3-8 个候选选题 |
| 04 | [tryworld-hv-analysis](skills/tryworld-hv-analysis/) | 横纵分析法深度研究 | PDF 研究报告 |
| 05 | [tryworld-writer](skills/tryworld-writer/) | 公众号长文写作 | 长文成品 |

## 工作流

```mermaid
flowchart LR
    U(["一句话"]) --> P["tryworld-koubo-pipeline"]
    P -- "模式 A · 直接给稿" --> A["tryworld-paper-algorithm<br/>优化 → 确认 → 出片"]
    P -- "模式 B · 帮我选题" --> S["tryworld-koubo-selection<br/>AIHOT 资讯 → 选题清单"]
    S -- "你挑选" --> A
    A --> O["成片交付<br/>视频 · 封面 · 标题 · 发布计划"]
    O -. "自动" .-> M["邮件通知<br/>产物 + 四平台发布时间"]
```

口播链路只需记住一个入口：`$tryworld-koubo-pipeline`。给稿走模式 A，要选题走模式 B；`tryworld-hv-analysis` 与 `tryworld-writer` 独立使用。

## 设计系统 · 纸上算法

纸面是舞台，墨迹是文字，朱红是重点，印章是签名。

| 色 | 值 | 用途 |
|---|---|---|
| 纸面 | `#F4EFE4` | 背景主色 |
| 墨黑 | `#1C1916` | 主文字、线条 |
| 朱红 | `#C0452F` | 唯一强调色 |
| 墨水蓝 | `#2E5E8C` | 次级批注 |

字体：思源宋体 · 霞鹜文楷 · 等宽。动效：墨落纸、笔写入、盖章。防伪：右上角朱红「试界原创」印章全程常驻。

## 安装

每个技能文件夹都是独立 Skill，复制到本机技能目录即可：

```powershell
Copy-Item -Path .\skills\* -Destination "$env:USERPROFILE\.codex\skills" -Recurse
```

其他宿主可放 `~/.agents/skills`。安装后直接说：「帮我做一期口播」。

## 目录

```text
tryworld-skills/
├── assets/                  # hero、许可徽章
├── README.md                # English
├── README.zh-CN.md          # 简体中文
├── LICENSE                  # CC BY-NC 4.0
└── skills/
    ├── tryworld-koubo-pipeline/
    ├── tryworld-paper-algorithm/
    ├── tryworld-koubo-selection/
    ├── tryworld-hv-analysis/
    └── tryworld-writer/
```

## 许可

知识共享 署名-非商业性使用 4.0 国际（CC BY-NC 4.0）：允许署名、非商业用途的自由分享与演绎，禁止商业用途。完整条款见 [LICENSE](LICENSE)。

[![CC BY-NC 4.0](assets/license-badge.svg)](https://creativecommons.org/licenses/by-nc/4.0/)

---

<p align="center"><sub>试界 TryWorld · 持续把 AI 讲清楚 — 排版：纸上算法 · MMXXVI</sub></p>