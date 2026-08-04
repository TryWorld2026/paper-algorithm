<div align="center">

# TryWorld Koubo Selection

**在热点里找值得做的选题。**

> 不是追爆款，而是用一致标准找出更稳、更好做、更有表达空间的选题。

</div>

---

## 它能解决什么问题

- 每天有很多内容方向，但不知道选哪个
- 不想靠感觉追热点，想要可复用的判断方式
- 需要一份可直接继续写脚本的选题单

---

## 适用场景

- AI 视频选题池生成
- 选题评估与优先级判断
- 从热点/资讯里筛选内容机会
- 为 pipeline、writer、paper-algorithm 提供输入

---

## 输入

- 用户直接说要做选题
- 任务、目标、平台或内容方向
- 是否需要覆盖本周/近期已知热点
- 是否需要保留 AI 新闻、热点追踪、选题建议等扩展结果

---

## 输出

- 3-8 个可执行选题
- 每个选题带理由、来源、爆点判断
- 选题标签、优先级、扩展方向
- 可直接进入 `tryworld-koubo-pipeline` 使用

---

## 工作流摘要

1. 抓取/整理最新热点信息
2. 按频道定位和选题规则筛选
3. 判断选题可表达性、差异性和传播点
4. 产出选题卡、对比结论和建议顺序
5. 同步记录已完成选题，降低重复

---

## 快速开始

```bash
cd skills/tryworld-koubo-selection
```

直接查看该目录下的 `SKILL.md`，按说明执行选题流程。

---

## 与其他 Skills 的关系

- 选题结果直接进入 `tryworld-koubo-pipeline`
- 研究型选题可先进入 `tryworld-hv-analysis`
- 技术选题可交给 `tryworld-paper-algorithm`
- 长文表达可交给 `tryworld-writer`

---

## License

MIT
