# TryWorld Skills（试界技能合集）

试界 TryWorld 的 Codex Skills 集合仓库。所有技能按标准结构组织（`SKILL.md` + `references/` + `scripts/` + `assets/` + `agents/`），每个文件夹即一个可独立安装的 Skill。

![状态](https://img.shields.io/badge/状态-已启用-8FAF8C)

## 技能总览

| Skill | 用途 | 调用方式 |
|---|---|---|
| [tryworld-koubo-pipeline](skills/tryworld-koubo-pipeline/) | 口播视频全流程统一入口（选题 / 写稿 / 优化 / 出片），自动路由 | `$tryworld-koubo-pipeline` |
| [tryworld-paper-algorithm](skills/tryworld-paper-algorithm/) | 纸上算法风格 AI 知识视频制作（HyperFrames + Azure YunxiNeural 真云希配音），产出主视频、横竖封面与平台标题 | `$tryworld-paper-algorithm` |
| [tryworld-koubo-selection](skills/tryworld-koubo-selection/) | 基于 AIHOT 最新 AI 资讯，按试界定位产出口播选题清单 | `$tryworld-koubo-selection` |
| [tryworld-hv-analysis](skills/tryworld-hv-analysis/) | 横纵分析法深度研究（纵轴发展历程 × 横轴竞品对比），产出排版精美的 PDF 研究报告 | `$tryworld-hv-analysis` |
| [tryworld-writer](skills/tryworld-writer/) | 公众号长文写作（试界 TryWorld 个人风格） | `$tryworld-writer` |

## 技能关系

- `tryworld-koubo-pipeline` 是口播链路的**唯一入口**，使用它时无需再单独引用其他技能：
  - 模式 A（直接给稿）：交给 `tryworld-paper-algorithm` 优化并出片；
  - 模式 B（要选题）：先走 `tryworld-koubo-selection` 选题 → 写初稿 → 再交给 `tryworld-paper-algorithm` 出片。
- `tryworld-hv-analysis` 与 `tryworld-writer` 相互独立，分别用于深度研究与公众号写作。

## 安装

每个技能文件夹可独立复制到本机技能目录，例如 Windows 的 `%USERPROFILE%\.codex\skills`：

```powershell
# 安装全部技能
Copy-Item -Path .\skills\* -Destination "$env:USERPROFILE\.codex\skills" -Recurse

# 或只安装单个技能
Copy-Item -Path .\skills\tryworld-paper-algorithm -Destination "$env:USERPROFILE\.codex\skills" -Recurse
```

安装后在 Codex 会话中按技能名调用，例如：

```text
用 $tryworld-koubo-pipeline 做一期口播视频。
```

## 目录结构

```text
tryworld-skills/
├── README.md                        # 本索引
└── skills/
    ├── tryworld-koubo-pipeline/     # 口播总入口（路由）
    ├── tryworld-paper-algorithm/    # 纸上算法视频制作
    ├── tryworld-koubo-selection/    # AIHOT 口播选题
    ├── tryworld-hv-analysis/        # 横纵分析法深度研究
    └── tryworld-writer/             # 公众号长文写作
```

## 许可

本仓库暂未附带开源许可证；在添加许可证之前，默认保留所有权利。
