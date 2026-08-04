<p align="center">
  <img src="assets/tryworld-logo.png" alt="TryWorld logo" width="320" />
</p>

<h1 align="center">TryWorld Skills</h1>

<p align="center">
  <strong>一个 AI 内容创作者的完整 skill 栈。</strong><br>
  不是帮你写一句回复，是帮你完成选题、写稿、分析、出片、交付的一整条链路。
</p>

<p align="center">
  <a href="#skills-overview">Skills</a> &nbsp;&middot;&nbsp;
  <a href="#tryworld-writer">公众号</a> &nbsp;&middot;&nbsp;
  <a href="#tryworld-hv-analysis">研究</a> &nbsp;&middot;&nbsp;
  <a href="#tryworld-paper-algorithm">视频</a> &nbsp;&middot;&nbsp;
  <a href="#koubo">口播</a>
</p>

---

## 这是什么东西

我做一个内容频道时，不想零散地装一堆 skill，再用时想不起来。

所以我把自己做 AI 内容时最常用的工作流，压成了 5 个 skill。它们的设计目标是：你只需给一个主题，它就能沿着一条明确的生产链路往下走。

---

## Skills 总览

### 1. 公众号长文写作

将你的素材、观察、产品体验，转成一篇有节奏、有判断、有真人感的公众号长文。

- 输入任意素材：brief、新闻链接、PDF、语音转文字、一段零散想法
- 输出：符合「试界 TryWorld」文风的公众号文章
- 质量门禁：四层自检体系

<p align="center">
  <a href="skills/tryworld-writer/README.md">查看 skill 详情</a>
</p>

---

### 2. 横纵分析深度研究

把对一个产品、公司、概念或人物的研究，压成一篇可以直接交付的 PDF。

- 纵向：从诞生到当下的完整生命周期
- 横向：与同期竞品/同类做系统性对比
- 交汇：给出新的判断，而不是前面内容的缩写

<p align="center">
  <a href="skills/tryworld-hv-analysis/README.md">查看 skill 详情</a>
</p>

---

### 3. 纸上算法视频

将 AI 口播稿直接变成一条品牌化的「纸上算法」视频。

- 统一视觉系统：纸张质感、墨水蓝、朱红印章
- 自动配音：Azure YunxiNeural
- 自动出字幕、封面、横竖构图、平台标题

<p align="center">
  <a href="skills/tryworld-paper-algorithm/README.md">查看 skill 详情</a>
</p>

---

### 4. 口播工作流总入口

想做 AI 口播视频时，不用记下面该调哪个 skill，直接走这里。

- 模式 A：你已经有口播稿，直接优化、出片
- 模式 B：从选题开始，拉 AIHOT 资讯 → 筛选选题 → 写稿 → 优化 → 出片

<p align="center">
  <a href="skills/tryworld-koubo-pipeline/README.md">查看 skill 详情</a>
</p>

---

### 5. AIHOT 口播选题

当你不确定这周该讲什么时，用这个 skill 从 AIHOT 最新资讯里筛出 3 到 8 个值得做的选题。

- 自动拉取最近 7 天精选 + 日报
- 按流量原则评估：共鸣、认可、槽点、嘴替、价值认同
- 输出可直接进入写稿流程的选题清单

<p align="center">
  <a href="skills/tryworld-koubo-selection/README.md">查看 skill 详情</a>
</p>

---

## 适合谁用

如果你符合下面任意一条，这个 repo 大概率对你有用：

- 你运营一个 AI 内容频道，想要稳定产出的工作流
- 你是个人创作者，不想每次都从零开始搭选题、写稿、出片流程
- 你希望内容风格保持一致，而不是每次换个 AI 就换一种语气
- 你想直接复用一套已经被验证过的「研究 -> 写作 -> 视频」链路

---

## 快速上手

```bash
git clone https://github.com/TryWorld2026/tryworld-skills.git
cd tryworld-skills
```

每个 skill 目录下都有独立 README 和详细说明。直接进入对应 skill 目录阅读即可。

---

## 一个典型工作流

这是我在实际做内容时最常用的链路：

1. `tryworld-koubo-selection`：从 AIHOT 拉最新资讯，筛出 3 到 8 个选题
2. `tryworld-koubo-pipeline`：选题、写初稿、进入标准化出片流程
3. `tryworld-paper-algorithm`：优化脚本、配音、构图、渲染、封面、标题
4. `tryworld-writer`：如果需要同步产出一篇公众号长文
5. `tryworld-hv-analysis`：当某个话题值得单独做一期深度研究时

这些 skill 不是孤立的。`koubo-pipeline` 就是总入口，它会根据你的输入自动路由到下面合适的 skill。

---

## 设计原则

这套 skill 的设计遵循几个基本原则：

- **链路完整，不是单点工具**
- **风格锁死，不是每次都随机生成**
- **真实优先，不编造数据、不虚构经历**
- **交付可验收，不是给半成品**

---

## 贡献

如果你在内容创作上有自己的 workflow，也欢迎提 PR。不过请先阅读 CONTRIBUTING.md，确保提交的 skill 符合这个 repo 的风格和质量标准。

---

## License

[CC BY-NC 4.0](LICENSE)

非商业使用可自由转载和修改，但请注明出处。
