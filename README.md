<div align="center">

# TryWorld Skills

<em>一条内容生产链路。五个 skill。零废话。</em>

<br>

[System](#system) &nbsp;&middot;&nbsp; [Skills](#skills) &nbsp;&middot;&nbsp; [Manifesto](#manifesto) &nbsp;&middot;&nbsp; [Usage](#usage)

</div>

---

## System

```
TryWorld Skills 不是工具集合。
它是内容生产链路。
```

五个 skill 按固定顺序衔接，形成从选题到交付的完整管线。每个 skill 有明确的输入、输出和质量门禁。skill 之间不重叠，但可以独立调用。

---

## Skills

**S01 · tryworld-koubo-selection**  
从 AIHOT 最新资讯中筛出值得做的选题。  
输入：最近 7 天 AI 资讯  
输出：3 到 8 个候选选题，含角度、素材链接、流量原理、优先级  
[查看 skill →](skills/tryworld-koubo-selection/README.md)

**S02 · tryworld-koubo-pipeline**  
口播视频的总入口。  
模式 A：已有口播稿，直接优化、出片  
模式 B：从选题开始，完整执行到交付  
[查看 skill →](skills/tryworld-koubo-pipeline/README.md)

**S03 · tryworld-paper-algorithm**  
将口播稿变成一条品牌化的「纸上算法」视频。  
视觉系统：纸张质感、墨水蓝、朱红印章  
配音：Azure YunxiNeural  
交付物：主视频、横竖封面、平台标题、字幕时间轴  
[查看 skill →](skills/tryworld-paper-algorithm/README.md)

**S04 · tryworld-writer**  
公众号长文写作。  
四层自检体系。固定文风约束。  
输入：任意素材  
[查看 skill →](skills/tryworld-writer/README.md)

**S05 · tryworld-hv-analysis**  
深度研究，输出 PDF 报告。  
方法：横纵分析法  
纵向：从诞生到当下  
横向：与竞品对比  
交汇：给出新判断  
[查看 skill →](skills/tryworld-hv-analysis/README.md)

---

## Manifesto

**链路完整，不是单点工具。**  
每个 skill 都设计成可以在生产链路中独立运行，也可以被其他 skill 调用。没有多余的环节，也没有缺失的环节。

**风格锁死，不是每次都随机生成。**  
文风、视觉系统、交付物格式都有明确契约。换一个 operator 不会换一种风格。

**真实优先，不编造数据、不虚构经历。**  
所有 skill 都内置了真实性约束。数据必须有来源，经历必须来自真实观察。找不到的信息诚实标注，不凑合。

**交付可验收，不是给半成品。**  
每个 skill 都有明确的质量门禁。交付物不是“先看看，后面再改”，而是经过检查可以直接使用。

---

## Workflow

```
 ┌─────────────┐
 │  S01        │
 │  选题筛选    │
 └──────┬──────┘
        │
        ▼
 ┌─────────────┐
 │  S02        │
 │  口播总入口   │
 └──────┬──────┘
        │
        ▼
 ┌─────────────┐
 │  S03        │
 │  纸上算法     │
 └──────┬──────┘
        │
        ▼
 ┌─────────────┐
 │  S04        │
 │  公众号写作   │
 └──────┬──────┘
        │
        ▼
 ┌─────────────┐
 │  S05        │
 │  横纵分析     │
 └─────────────┘
```

这是主链路。不是每个项目都需要跑完全程。  
skill 支持独立调用。你可以只选题、只写稿、只优化不出片。

---

## Usage

```bash
git clone https://github.com/TryWorld2026/tryworld-skills.git
cd tryworld-skills
```

进入对应 skill 目录，阅读 README。每个 skill 都有独立的使用说明和触发条件。

---

## Who

- 运营 AI 内容频道，需要稳定产出工作流的创作者
- 个人创作者，不想每次都从零开始搭流程
- 希望内容风格保持一致，而不是每次换个 AI 就换一种语气
- 想直接复用一套已经被验证过的「研究 → 写作 → 视频」链路

---

<div align="center">

[CC BY-NC 4.0](LICENSE) &nbsp;&middot;&nbsp; 非商业使用可自由转载和修改，请注明出处

</div>
