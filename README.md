<div align="center">

# TryWorld Skills

**把 AI 工具链，整理成真正可交付的工作流**

> 不是“又一个提示词仓库”，是一套面向研究、选题、论文解读和深度写作的 Skills 体系。

<div align="center">

[![GitHub](https://img.shields.io/badge/GitHub-TryWorld2026%2Ftryworld--skills-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/TryWorld2026/tryworld-skills)
[![License](https://img.shields.io/badge/License-MIT-success?style=for-the-badge)](LICENSE)
[![Docs](https://img.shields.io/badge/docs-index.html-0a0a0a?style=for-the-badge&logo=readthedocs&logoColor=white)](docs/index.html)

</div>

</div>

---

## 先看这张图

<p align="center">
  <img src="assets/hero.svg" alt="TryWorld Skills 结构示意图" width="720">
</p>

<p align="center">
  <a href="https://github.com/TryWorld2026/tryworld-skills/blob/main/assets/hero.svg">点击查看原图</a>
</p>

---

## 我会给你什么

先回答一个更直接的问题：你拿到后可以直接做什么。

- 研究一件事：不是给一段话，而是给出可检查的研究结论
- 选题与落地：从热点追踪到输出规范，一链到底
- 技术内容：把论文、算法、技术点讲清楚
- 深度写作：写出更长、更有结构、更有个人风格的长文

如果你不是来看“万能提示词模板”的，这套 skills 会更理解你。

---

## 核心能力总览

| Skill | 定位 | 典型交付物 | 推荐何时用 |
|---|---|---|---|
| `tryworld-hv-analysis` | 纵横分析 | 研究报告 / PDF | 研究产品、公司、概念、人物 |
| `tryworld-koubo-selection` | 投放选题 | 选题卡、对比结论 | 需要选题池、选题依据、选题方向 |
| `tryworld-koubo-pipeline` | 内容生产流程 | 流程文件、成片清单 | 从选题到成片需要一个清晰 SOP |
| `tryworld-paper-algorithm` | 论文与算法拆解 | 视频脚本、封面、标题 | 想输出“论文精讲/算法拆解”视频 |
| `tryworld-writer` | 深度写作 | 公众号长文、专栏稿 | 要写有观点、有细节、可发布的长文 |

这套仓库的价值，是把不同 skill 串在一起，而不是期待一个 skill 解决所有问题。

---

## 推荐链路

**研究 → 选题 → 结构化创作**

```text
复杂研究
  -> tryworld-hv-analysis

内容投放
  -> tryworld-koubo-selection
  -> tryworld-koubo-pipeline

技术视频 / 知识内容
  -> tryworld-paper-algorithm

深度写作 / 专栏 / 公众号
  -> tryworld-writer
```

你可以按任务单点使用，也可以按这个顺序像流水线一样接起来。

---

## 快速开始

```bash
git clone https://github.com/TryWorld2026/tryworld-skills.git
cd tryworld-skills/skills/<skill-name>
```

每个 skill 目录里都有独立 `SKILL.md`，不是零散话术，而是完整工作流。

---

## 设计原则

- **按任务组织，不按模型组织**
- **每个 skill 都是可交付链，不是只言片语**
- **优先给可检查的结果，而不是看起来很完整的草稿**
- **保留人的判断，AI 负责加速研究、整理、转述和结构化**
- **输出可交接：下一个人能直接接手继续用**

---

## 技术说明

| 项目 | 说明 |
|---|---|
| 命名空间 | `tryworld-*` |
| 面向目标 | AI 研究、AI 视频、AI 写作 |
| 类型 | 仓库级可复用 Skills 合集 |
| 来源 | GitHub：TryWorld2026 / tryworld-skills |

---

## 资源索引

| 资源 | 链接 |
|---|---|
| 首页 | [README.md](README.md) |
| 在线文档 | [docs/index.html](docs/index.html) |
| 许可证 | [LICENSE](LICENSE) |

---

## 贡献方式

欢迎：
- 新增 task-level skill
- 补充参考资料、脚本、模板、示例
- 优化现有工作流和输出结构

直接开 PR / Issue 即可。

---

## License

[MIT](LICENSE)