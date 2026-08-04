<div align="center">

# TryWorld Skills

**一套为真实工作流设计的 AI Skills 合集**

[![License: MIT](assets/license-badge.svg)](LICENSE)
[![Docs](https://img.shields.io/badge/docs-index.html-green)](docs/index.html)
[![GitHub](https://img.shields.io/badge/GitHub-TryWorld2026%2Ftryworld--skills-blue)](https://github.com/TryWorld2026/tryworld-skills)

</div>

---

## 设计理念

大多数人不需要又一个“万能提示词”。  
你需要的是**可复用、可检查、可交接**的工作流。

这套 Skills 的定位很明确：
- 按任务组织，而不是按模型组织；
- 每个 skill 都是完整工作流，不是零散话术；
- 输出结果可直接交付，或交给下一个人继续使用。

---

## 核心技能

| Skill | 一句话定位 | 典型输出 |
|---|---|---|
| `tryworld-hv-analysis` | 纵横分析 | 结构化研究报告 / PDF |
| `tryworld-koubo-selection` | 投放选题 | 选题卡片池 / 对比结论 |
| `tryworld-koubo-pipeline` | 内容生产流程 | 选题到成品的 pipeline |
| `tryworld-paper-algorithm` | 论文与算法拆解 | 论文解读 / 算法讲解稿 |
| `tryworld-writer` | 深度写作 | 公众号长文 / 专栏稿 |

---

## 快速开始

```bash
git clone https://github.com/TryWorld2026/tryworld-skills.git
cd tryworld-skills/skills/<skill-name>
```

每个 skill 目录内都有独立的 `SKILL.md`，可直接按文档执行。

---

## 推荐用法

- 复杂研究类任务：先用 `tryworld-hv-analysis` 建立信息结构
- 内容投放类任务：再进入 `tryworld-koubo-selection` 与 `tryworld-koubo-pipeline`
- 技术传播类任务：使用 `tryworld-paper-algorithm` 拆解论文
- 高质量长文：使用 `tryworld-writer` 完成深度写作

建议把多个 skill 串成流水线，而不是指望一个 skill 解决所有问题。

---

## 仓库结构

```
tryworld-skills/
├── assets/
├── docs/
├── skills/
│   ├── tryworld-hv-analysis/
│   ├── tryworld-koubo-pipeline/
│   ├── tryworld-koubo-selection/
│   ├── tryworld-paper-algorithm/
│   └── tryworld-writer/
├── LICENSE
└── README.md
```

---

## 贡献

欢迎补充新的 skill，或优化现有工作流。  
PR / Issue 皆可。

---

## License

MIT