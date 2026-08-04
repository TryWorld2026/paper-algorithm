<h1 align="center">TryWorld Skills</h1>

<p align="center">
  <b>试界 TryWorld 的 Codex Skills 合集</b><br/>
  选题 · 写稿 · 出片 · 深度研究 · 公众号写作
</p>

<p align="center">
  <img src="https://img.shields.io/badge/status-active-8FAF8C?style=for-the-badge&logo=github&logoColor=white" alt="status">
  <img src="https://img.shields.io/badge/skills-5-1C1916?style=for-the-badge&logo=markdown&logoColor=white" alt="skills">
  <img src="https://img.shields.io/badge/platform-Codex%20%2F%20Claude-2E5E8C?style=for-the-badge&logo=openai&logoColor=white" alt="platform">
  <img src="https://img.shields.io/badge/Made%20with-%E2%9D%A4%EF%B8%8F-C0452F?style=for-the-badge" alt="made with love">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Node.js-339933?style=for-the-badge&logo=nodedotjs&logoColor=white" alt="Node.js">
  <img src="https://img.shields.io/badge/PowerShell-5391FE?style=for-the-badge&logo=powershell&logoColor=white" alt="PowerShell">
  <img src="https://img.shields.io/badge/FFmpeg-007808?style=for-the-badge&logo=ffmpeg&logoColor=white" alt="FFmpeg">
  <img src="https://img.shields.io/badge/Azure-0078D4?style=for-the-badge&logo=microsoftazure&logoColor=white" alt="Azure">
  <img src="https://img.shields.io/badge/Markdown-000000?style=for-the-badge&logo=markdown&logoColor=white" alt="Markdown">
</p>

<p align="center">
  <a href="README.md">English</a> · <b><a href="README.zh-CN.md">简体中文</a></b>
</p>

---

## 技能总览

| | 技能 | 一句话定位 | 核心产出 |
|---|---|---|---|
| 🎬 | [tryworld-koubo-pipeline](skills/tryworld-koubo-pipeline/) | 口播视频全流程**统一入口**,自动路由 | 从选题到成片的一站式交付 |
| 📜 | [tryworld-paper-algorithm](skills/tryworld-paper-algorithm/) | 「纸上算法」风格 AI 知识视频制作 | 主视频 · 横竖封面 · 平台标题 |
| 🎯 | [tryworld-koubo-selection](skills/tryworld-koubo-selection/) | 基于 AIHOT 最新 AI 资讯产出口播选题 | 3-8 个候选选题清单 |
| 🔬 | [tryworld-hv-analysis](skills/tryworld-hv-analysis/) | 横纵分析法深度研究 | 排版精美的 PDF 研究报告 |
| ✍️ | [tryworld-writer](skills/tryworld-writer/) | 公众号长文写作（试界风格） | 公众号长文 |

## 技能关系

```mermaid
flowchart LR
    U(["用户请求"]) --> P["🎬 tryworld-koubo-pipeline<br/>口播统一入口"]
    P -- "模式 A：直接给稿" --> A["📜 tryworld-paper-algorithm<br/>优化 → 出片"]
    P -- "模式 B：要选题" --> S["🎯 tryworld-koubo-selection<br/>AIHOT 资讯选题"]
    S --> A
    A --> O["✅ 成片交付<br/>视频 / 封面 / 标题 / 发布计划"]
    H["🔬 tryworld-hv-analysis<br/>深度研究"] -. "独立使用" .-> R["📄 PDF 研究报告"]
    W["✍️ tryworld-writer<br/>公众号写作"] -. "独立使用" .-> C["📝 公众号长文"]
```

口播链路只需记住 `$tryworld-koubo-pipeline` 一个入口：直接给稿走模式 A，要选题走模式 B，它会自动调度其余技能；`tryworld-hv-analysis` 与 `tryworld-writer` 相互独立，按需单独调用。

## 技术栈

| 技能 | 依赖 |
|---|---|
| tryworld-paper-algorithm | HyperFrames、edge-tts（Azure YunxiNeural）、FFmpeg、Node.js ≥ 22、Python 3.10+ |
| tryworld-koubo-selection | PowerShell 脚本 / curl、AIHOT API |
| tryworld-hv-analysis | Python、WeasyPrint、Markdown |
| tryworld-writer | — |
| tryworld-koubo-pipeline | 调度上述技能的路由入口 |

## 快速开始

每个技能文件夹都是独立的 Skill，复制到本机技能目录即可安装（Windows 示例）：

```powershell
# 安装全部技能
Copy-Item -Path .\skills\* -Destination "$env:USERPROFILE\.codex\skills" -Recurse

# 或只安装单个技能
Copy-Item -Path .\skills\tryworld-paper-algorithm -Destination "$env:USERPROFILE\.codex\skills" -Recurse
```

其他宿主也可放到 `~/.agents/skills`。安装后在 Codex 会话中按技能名调用：

```text
用 $tryworld-koubo-pipeline 做一期口播视频。
```

## 目录结构

```text
tryworld-skills/
├── README.md                 # 索引（英文）
├── README.zh-CN.md           # 索引（简体中文）
└── skills/
    ├── tryworld-koubo-pipeline/     # 口播总入口（路由）
    ├── tryworld-paper-algorithm/    # 纸上算法视频制作
    ├── tryworld-koubo-selection/    # AIHOT 口播选题
    ├── tryworld-hv-analysis/        # 横纵分析法深度研究
    └── tryworld-writer/             # 公众号长文写作
```

## 许可

本仓库暂未附带开源许可证；在添加许可证之前，默认保留所有权利。
