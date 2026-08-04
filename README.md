<div align="center">

![TryWorld Skills Hero](assets/hero.svg)

# TryWorld Skills

### 一套面向交付的 AI 技能系统

> 这里的目标不是提供“万能提示词”，而是提供可以研究、选题、写作、生产的工作流系统。  
> 目标不是更会写 prompt，而是减少无效修改、加速交付，并把人的判断保留到最后。

<br/>

[![GitHub stars](https://img.shields.io/github/stars/TryWorld2026/tryworld-skills?style=social)](https://github.com/TryWorld2026/tryworld-skills)
[![License](https://img.shields.io/badge/license-MIT-success?style=for-the-badge)](LICENSE)
[![Docs](https://img.shields.io/badge/docs-index.html-0a0a0a?style=for-the-badge&logo=readthedocs&logoColor=white)](docs/index.html)
[![GitHub](https://img.shields.io/badge/GitHub-TryWorld2026%2Ftryworld--skills-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/TryWorld2026/tryworld-skills)

</div>

---

## 中文说明

这个仓库不是在堆 skill 数量。  
精炼的方向只有一条：把 AI 能力收束到真实任务里，而不是散成零散话术。

- 研究类任务先做结构化结论
- 选题类任务再落到可执行的选题卡
- 技术内容继续进入论文/算法拆解
- 文章交付进入深度写作与成稿

它适合想要减少返工、提升交付质量的人。

---

## English Intro

This repo is not a prompt dump.  
It is a structured set of skills focused on research, selection, writing, and content production.

Use it when you want:
- cleaner research outputs,
- more executable topic choices,
- repeatable writing and production workflows,
- and a system that can be handed off instead of rebuilt each time.

---

## 核心能力总览

| Skill | 定位 | 典型交付物 |
|---|---|---|
| `tryworld-hv-analysis` | 纵横分析 | 研究报告 / PDF |
| `tryworld-koubo-selection` | 投放选题 | 选题卡 / 对比结论 |
| `tryworld-koubo-pipeline` | 内容生产流程 | 脚本、标题、发布说明 |
| `tryworld-paper-algorithm` | 论文与算法拆解 | 视频脚本、标题、封面 |
| `tryworld-writer` | 深度写作 | 公众号长文 / 专栏稿 |

---

## Core Skills Summary

| Skill | Purpose | Output |
|---|---|---|
| `tryworld-hv-analysis` | Horizontal and vertical analysis | Research briefs / PDF |
| `tryworld-koubo-selection` | Topic selection | Topic cards / priority ranking |
| `tryworld-koubo-pipeline` | Production pipeline | Content checklists / platform metadata |
| `tryworld-paper-algorithm` | Paper/algorithm storytelling | Script, titles, and covers |
| `tryworld-writer` | Long-form writing | Columns, essays, drafts for publication |

---

## 推荐链路

**研究 → 选题 → 结构化创作**

```text
复杂研究
  -> tryworld-hv-analysis

内容投放
  -> tryworld-koubo-selection
  -> tryworld-koubo-pipeline

技术内容
  -> tryworld-paper-algorithm

深度写作
  -> tryworld-writer
```

可以单点使用，也可以按这个顺序串联成系统。

---

## Why This Repo Exists

大多数 AI 技能仓库的问题不是太短，而是太散。  
这个仓库的价值是把“研究、判断、表达、生产”做成一条更短、更可检查的链路。

它适合：
- 独立创作者
- 内容策略者
- 研究型写作者
- 想把 AI 用得更系统，而不是更零散的人

---

## How To Use

```bash
git clone https://github.com/TryWorld2026/tryworld-skills.git
cd tryworld-skills/skills/<skill-name>
```

直接进入对应 skill，查看 `SKILL.md` 开始使用。

---

## 特色

- 按任务组织，而不是按模型组织
- 每个 skill 都有输入合同、执行逻辑、输出格式和交接规则
- 支持单点使用，也支持串成流水线
- 目标不是看起来完整，而是能交付

---

## License

本项目采用 **MIT License**。

### 许可证说明

- **允许**：商用、修改、分发、私人使用
- **条件**：保留原始版权与许可声明
- **限制**：按原样提供，作者不承担后续责任或担保

如果你要在项目内长期引用本仓库的方法论或脚本，请保留原始作者声明。

---

# License

This project is released under the **MIT License**.

### License Notes

- **Permitted**: commercial use, modification, distribution, private use
- **Condition**: retain original copyright and license notice
- **Limitation**: provided as-is without warranty; authors are not liable for downstream use

If you reuse the methodology or scripts publicly, keep the original attribution visible.