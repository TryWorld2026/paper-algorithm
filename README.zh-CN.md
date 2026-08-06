<p align="center">
  <img src="assets/hero.svg" alt="试界 TryWorld Skills" width="100%">
</p>

<div align="center">
  <b style="font-family:Georgia,'Noto Serif SC','Songti SC','SimSun',serif; font-size:18px; color:#1C1916; letter-spacing:8px;">纸上算法 · PAPER ALGORITHM</b><br/>
  <span style="color:#5C5445; font-size:14px;">从一句话到一条生产线——把 AI 讲清楚，让每个普通人都看得懂、用得上。</span>
</div>

<p align="center">
  <a href="README.md">English</a> · <b>简体中文</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/状态-已启用-8FAF8C?style=flat-square" alt="status">
  <img src="https://img.shields.io/badge/技能-5-1C1916?style=flat-square" alt="skills">
  <img src="https://img.shields.io/badge/平台-Codex%20%E2%80%A2%20Claude-2E5E8C?style=flat-square" alt="platform">
  <img src="https://img.shields.io/badge/许可-CC%20BY--NC%204.0-C0452F?style=flat-square" alt="license">
</p>

---

<div align="center">
<table style="border:1px solid #E4DCC8; border-radius:8px; background:#FBF7EC;">
<tr><td style="border-left:4px solid #C0452F; padding:14px 18px;">
  <b style="font-family:Georgia,'Noto Serif SC','Songti SC',serif; color:#1C1916; font-size:16px;">纸面是舞台，墨迹是文字，朱红是重点，印章是签名。</b><br/>
  <span style="color:#5C5445; font-size:13px;">五个技能各守一页，合起来就是一页会动的算法笔记——从「这周做什么」到成片交付、自动邮件通知、四平台发布计划。</span>
</td></tr>
</table>
</div>

## 📑 目录

- [五张纸页 · 技能总览](#-五张纸页--技能总览)
- [一条口播工作流](#-一条口播工作流)
- [纸上算法 · 设计系统](#-纸上算法--设计系统)
- [活人感门禁](#-活人感门禁)
- [快速开始](#-快速开始)
- [仓库结构](#-仓库结构)
- [许可](#-许可)

---

## 🧩 五张纸页 · 技能总览

<div align="center">
<table>
<tr>
<td width="33%" valign="top" style="border:1px solid #E4DCC8; border-top:3px solid #C0452F; background:#FBF7EC; border-radius:6px; padding:12px 14px;">
  <b style="font-family:Georgia,'Noto Serif SC','Songti SC',serif; color:#1C1916; font-size:15px;">🎬 口播总入口</b><br/>
  <span style="color:#C0452F; font-size:12px; font-weight:bold;">tryworld-koubo</span>
  <br/><br/><span style="font-size:13px; color:#1C1916;">一句人话，自动路由选题、写稿、优化、出片。</span>
  <br/><br/><span style="font-size:12px; color:#2E5E8C;">产出：全流程交付 + 邮件通知</span><br/>
  <code style="font-size:12px;">$tryworld-koubo</code>
</td>
<td width="34%" valign="top" style="border:1px solid #E4DCC8; border-top:3px solid #C0452F; background:#FBF7EC; border-radius:6px; padding:12px 14px;">
  <b style="font-family:Georgia,'Noto Serif SC','Songti SC',serif; color:#1C1916; font-size:15px;">📜 纸上算法视频</b><br/>
  <span style="color:#C0452F; font-size:12px; font-weight:bold;">tryworld-paper</span>
  <br/><br/><span style="font-size:13px; color:#1C1916;">口播稿 → 品牌化横屏视频，一页会动的算法笔记。</span>
  <br/><br/><span style="font-size:12px; color:#2E5E8C;">产出：主视频 · 横竖封面 · 标题 · 字幕</span><br/>
  <code style="font-size:12px;">$tryworld-paper</code>
</td>
<td width="33%" valign="top" style="border:1px solid #E4DCC8; border-top:3px solid #C0452F; background:#FBF7EC; border-radius:6px; padding:12px 14px;">
  <b style="font-family:Georgia,'Noto Serif SC','Songti SC',serif; color:#1C1916; font-size:15px;">🎯 AI 口播选题</b><br/>
  <span style="color:#C0452F; font-size:12px; font-weight:bold;">tryworld-topics</span>
  <br/><br/><span style="font-size:13px; color:#1C1916;">每天几百条 AI 新闻，压成 3-8 个能做、能火、不重复的选题。</span>
  <br/><br/><span style="font-size:12px; color:#2E5E8C;">产出：选题清单（角度 · 来源 · 优先级）</span><br/>
  <code style="font-size:12px;">$tryworld-topics</code>
</td>
</tr>
<tr>
<td width="33%" valign="top" style="border:1px solid #E4DCC8; border-top:3px solid #C0452F; background:#FBF7EC; border-radius:6px; padding:12px 14px;">
  <b style="font-family:Georgia,'Noto Serif SC','Songti SC',serif; color:#1C1916; font-size:15px;">🔬 横纵分析法</b><br/>
  <span style="color:#C0452F; font-size:12px; font-weight:bold;">tryworld-research</span>
  <br/><br/><span style="font-size:13px; color:#1C1916;">纵轴追生命历程，横轴比竞品格局，交叉出独到洞察。</span>
  <br/><br/><span style="font-size:12px; color:#2E5E8C;">产出：万字 PDF 研究报告</span><br/>
  <code style="font-size:12px;">$tryworld-research</code>
</td>
<td width="34%" valign="top" style="border:1px solid #E4DCC8; border-top:3px solid #C0452F; background:#FBF7EC; border-radius:6px; padding:12px 14px;">
  <b style="font-family:Georgia,'Noto Serif SC','Songti SC',serif; color:#1C1916; font-size:15px;">✍️ 公众号长文</b><br/>
  <span style="color:#C0452F; font-size:12px; font-weight:bold;">tryworld-write</span>
  <br/><br/><span style="font-size:13px; color:#1C1916;">按试界风格，把素材写成读得下去的公众号长文。</span>
  <br/><br/><span style="font-size:12px; color:#2E5E8C;">产出：长文成品</span><br/>
  <code style="font-size:12px;">$tryworld-write</code>
</td>
<td width="33%" valign="top"></td>
</tr>
</table>
</div>

---

## 🎬 一条口播工作流

只记一个入口：**`$tryworld-koubo`**。给稿走模式 A，要选题走模式 B；`tryworld-research` 与 `tryworld-write` 独立使用。

```mermaid
flowchart LR
    U(["你的一句话"]) --> P["🎬 tryworld-koubo<br/>统一入口 · 自动路由"]
    P -- "模式 A · 直接给稿" --> A["📜 tryworld-paper<br/>优化 → 确认 → 出片"]
    P -- "模式 B · 帮我选题" --> S["🎯 tryworld-topics<br/>AIHOT 资讯 → 选题清单"]
    S -- "你挑选" --> A
    A --> O["✅ 成片交付<br/>视频 · 封面 · 标题 · 发布计划"]
    O -. "自动" .-> M["📧 邮件通知<br/>产物 + 四平台发布时间"]
    H["🔬 tryworld-research"] -. "独立" .-> R["📄 PDF 报告"]
    W["✍️ tryworld-write"] -. "独立" .-> C["📝 公众号长文"]
```

---

## 🎨 纸上算法 · 设计系统

试界视频的视觉契约——**科学手稿 + 中文印刷传统**，一条不允许为省事让步的锁定契约。

<div align="center">
<table>
<tr>
<td align="center" style="background:#F4EFE4; color:#1C1916; padding:10px 14px; border:1px solid #E4DCC8;">
  <b style="font-family:Georgia,'Noto Serif SC','Songti SC',serif;">纸面</b><br/>
  <code>#F4EFE4</code><br/>
  <small>背景主色</small>
</td>
<td align="center" style="background:#1C1916; color:#F4EFE4; padding:10px 14px; border:1px solid #E4DCC8;">
  <b style="font-family:Georgia,'Noto Serif SC','Songti SC',serif;">墨黑</b><br/>
  <code>#1C1916</code><br/>
  <small>主文字 · 线条</small>
</td>
<td align="center" style="background:#C0452F; color:#F4EFE4; padding:10px 14px; border:1px solid #E4DCC8;">
  <b style="font-family:Georgia,'Noto Serif SC','Songti SC',serif;">朱红</b><br/>
  <code>#C0452F</code><br/>
  <small>唯一强调色</small>
</td>
<td align="center" style="background:#2E5E8C; color:#F4EFE4; padding:10px 14px; border:1px solid #E4DCC8;">
  <b style="font-family:Georgia,'Noto Serif SC','Songti SC',serif;">墨水蓝</b><br/>
  <code>#2E5E8C</code><br/>
  <small>次级批注 · 图表</small>
</td>
</tr>
</table>
</div>

| 维度 | 约定 |
|---|---|
| **字体** | 思源宋体（主标题）· 霞鹜文楷 / ZCOOL 小薇（批注）· 等宽字体（数据） |
| **动效** | 墨落纸 · 笔写入 · 盖章——全片三种签名动效 |
| **防伪** | 朱红「试界原创」印章右上角全程常驻，是视频唯一水印 |

---

## 🔒 活人感门禁

成片之前，每一版口播稿与平台标题都要过一道机器门禁——**禁的是修辞动作，不是字面**。换一套字做同一个动作，仍然算命中。

- **翻案腔**：先立读者没有的误解再推翻抬价。已知外衣不限于「不是……而是……」「并非……而是……」「不在于……而在于……」「表面……实际……」「看似……实则……」「你以为……其实……」「回头才发现」「说到底」「答案恰恰相反」，判断从正面下，先给判断再给依据。
- **同构排比**：三项以上整齐排比，两项为限。
- **抒情借喻**：不给抽象名词配具体动词（「时间保管细节」类），写具体事物不受影响。
- **动词名词化**：「实现了效率的提升」还原成「快了多少、省了几个人」。
- **标点分级**：破折号全禁；冒号只允许引出人物直接原话。
- **黑话两档**：绝对禁词 + 语境判断词，清单由检测器维护。

检测器 `tryworld-paper/scripts/check_prose.py`（源自 [human-writing](https://github.com/KKKKhazix/human-writing) v1.1.0，MIT）自动执行以上检查，并额外给出统计层提示——句长变异系数、连词密度、模型偏爱抒情词、「」金句密度。**硬禁项清零才允许进入用户确认闸门，失败不交付。**

---

## 🚀 快速开始

每个技能文件夹都是独立的 Skill，复制到本机技能目录即可：

```powershell
# 安装全部技能
Copy-Item -Path .\skills\* -Destination "$env:USERPROFILE\.agents\skills" -Recurse

# 或只安装单个技能
Copy-Item -Path .\skills\tryworld-paper -Destination "$env:USERPROFILE\.agents\skills" -Recurse
```

> 其他宿主（Codex / Claude Code / Cursor 等）同样读取 `~/.agents/skills`。安装后在会话中直接说：

```text
帮我做一期口播
用 $tryworld-koubo 出片
```

---

## 🗂 仓库结构

```text
tryworld-skills/
├── assets/
│   ├── hero.svg                 # 品牌横幅
│   └── license-badge.svg        # 许可徽章
├── README.md                    # 索引（English）
├── README.zh-CN.md              # 索引（简体中文）
├── LICENSE                      # CC BY-NC 4.0
└── skills/
    ├── tryworld-koubo/          # 口播总入口（路由 + 邮件通知）
    ├── tryworld-paper/          # 纸上算法视频制作
    ├── tryworld-topics/         # AIHOT 口播选题
    ├── tryworld-research/       # 横纵分析法深度研究
    └── tryworld-write/          # 公众号长文写作
```

---

## ⚖️ 许可

本仓库采用知识共享 **署名-非商业性使用 4.0 国际（CC BY-NC 4.0）**：允许署名、非商业用途的自由分享与演绎，禁止商业用途。完整条款见 [LICENSE](LICENSE)。

[![CC BY-NC 4.0](assets/license-badge.svg)](https://creativecommons.org/licenses/by-nc/4.0/)

---

<p align="center"><sub>试界 TryWorld · 持续把 AI 讲清楚 · 让每个普通人都看得懂、用得上</sub></p>
