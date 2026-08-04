<p align="center">
  <img src="assets/hero.svg" alt="TryWorld Skills" width="100%">
</p>

<p align="center">
  <b>TryWorld · A Codex Skills Collection</b><br/>
  one complete content pipeline — from topic selection to video delivery, deep research, and long-form writing
</p>

<p align="center">
  <b>English</b> · <a href="README.zh-CN.md">简体中文</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/status-active-8FAF8C?style=flat-square" alt="status">
  <img src="https://img.shields.io/badge/skills-5-1C1916?style=flat-square" alt="skills">
  <img src="https://img.shields.io/badge/platform-Codex%20%E2%80%A2%20Claude-2E5E8C?style=flat-square" alt="platform">
  <img src="https://img.shields.io/badge/license-CC%20BY--NC%204.0-C0452F?style=flat-square" alt="license">
</p>

---

> **Making AI clear for everyone.** Five skills, each solving one link of the content chain — together they form an end-to-end voiceover pipeline: from "what should I make" to delivered videos, automatic email notices, and a four-platform publishing schedule.

## ✨ Skills at a Glance

| | Skill | Role | One-liner | Key Deliverables |
|---|---|---|---|---|
| 🎬 | [tryworld-koubo](skills/tryworld-koubo/) | **Voiceover entry point** | One sentence in, auto-routed end to end | Full delivery + email notice |
| 📜 | [tryworld-paper](skills/tryworld-paper/) | Paper Algorithm video production | Script → branded horizontal video | Video · covers · titles · captions |
| 🎯 | [tryworld-topics](skills/tryworld-topics/) | AI-news topic selection | Pick worth-making topics from AIHOT | 3–8 candidate topics |
| 🔬 | [tryworld-research](skills/tryworld-research/) | Horizontal–Vertical deep research | Life arc × competitive landscape | Polished PDF report |
| ✍️ | [tryworld-write](skills/tryworld-write/) | WeChat long-form writing | Material → TryWorld-style article | Finished long-form article |

## 🎬 The Voiceover Workflow

```mermaid
flowchart LR
    U(["One sentence from you"]) --> P["🎬 tryworld-koubo<br/>Single entry · auto-route"]
    P -- "Mode A · script given" --> A["📜 tryworld-paper<br/>Optimize → confirm → produce"]
    P -- "Mode B · pick a topic" --> S["🎯 tryworld-topics<br/>AIHOT news → topic list"]
    S -- "you choose" --> A
    A --> O["✅ Deliverables<br/>Video · covers · titles · schedule"]
    O -. "automatic" .-> M["📧 Email notice<br/>Deliverables + publish times"]
    H["🔬 tryworld-research"] -. "standalone" .-> R["📄 PDF report"]
    W["✍️ tryworld-write"] -. "standalone" .-> C["📝 WeChat article"]
```

For the video pipeline, remember one entry: **`$tryworld-koubo`**. Hand it a script (Mode A) or ask for topics (Mode B). `tryworld-research` and `tryworld-write` are standalone.

## 🧩 Inside Each Skill

### 🎬 tryworld-koubo — The Voiceover Router

> The brain of the whole pipeline.

- **What it does**：Detects "script given" (Mode A) vs "pick a topic" (Mode B)；sub-commands（topics only / draft only / optimize only）；dedup by scanning finished deliverables；sends an automatic email notice after delivery.
- **Try it**：`Make me a TryWorld voiceover video` / `Use $tryworld-koubo to produce this`
- **Depends on**：the other skills · `qq-email`

### 📜 tryworld-paper — Paper Algorithm Video Production

> A page of moving algorithm notes: paper is the stage, ink is the text, vermillion is the accent, the seal is the signature.

- **What it does**：Optimizes the script → Azure YunxiNeural voiceover → HyperFrames composition & render → covers, platform titles, caption timeline；a vermillion「试界原创」seal stays visible throughout.
- **Try it**：`Use $tryworld-paper to make a video from this script`
- **Depends on**：HyperFrames · edge-tts · FFmpeg · Node.js ≥ 22 · Python 3.10+

### 🎯 tryworld-topics — AI-News Topic Selection

> Compress hundreds of daily AI headlines into 3–8 topics worth making — fresh, catchy, and not repeated.

- **What it does**：Pulls curated AIHOT items（models / products / industry / papers / tips），scores them against growth principles，each candidate ships with an angle, source links, and priority；auto-skips topics already produced.
- **Try it**：`Help me pick topics` / `What should I cover this week`
- **Depends on**：AIHOT API · PowerShell / curl

### 🔬 tryworld-research — Horizontal–Vertical Deep Research

> Trace the life arc vertically, compare the landscape horizontally, cross the two axes for insight.

- **What it does**：Deep research on a product, company, concept, or person；outputs a beautifully formatted PDF report.
- **Try it**：`Research XX with Horizontal–Vertical Analysis`
- **Depends on**：Python · WeasyPrint · Markdown

### ✍️ tryworld-write — WeChat Long-Form Writing

> A TryWorld-style long-form article generator.

- **What it does**：Turns source material（PDF / links / transcripts / briefs）into a finished WeChat article with the brand's voice and a submission email footer.
- **Try it**：`Turn this into a WeChat article`
- **Depends on**：—

## 🎨 The Paper Algorithm Design System

TryWorld videos follow one visual contract — **scientific manuscript + Chinese print tradition**.

| Swatch | Value | Role |
|---|---|---|
| Paper | `#F4EFE4` | Background |
| Ink | `#1C1916` | Text & lines |
| Vermillion | `#C0452F` | The only accent: keywords, numbers, seal |
| Ink Blue | `#2E5E8C` | Secondary notes & chart guides |

- **Type**：Noto Serif SC (headings) · LXGW WenKai / ZCOOL XiaoWei (notes) · monospace (data)
- **Motion**：ink drop · brush stroke · seal stamp — three signature moves throughout
- **Authenticity**：a vermillion「试界原创」seal stays in the top-right corner

## 🚀 Quick Start

Each skill folder is self-contained. Copy it into your local skills directory:

```powershell
# Install all skills
Copy-Item -Path .\skills\* -Destination "$env:USERPROFILE\.codex\skills" -Recurse

# Or install a single skill
Copy-Item -Path .\skills\tryworld-paper -Destination "$env:USERPROFILE\.codex\skills" -Recurse
```

`~/.agents/skills` works on other hosts too. Then just say it in Codex:

```text
Make me a TryWorld voiceover video
Use $tryworld-koubo to produce this
```

## 🗂 Repository Layout

```text
tryworld-skills/
├── assets/
│   ├── hero.svg                 # Brand banner
│   └── license-badge.svg        # License badge
├── README.md                    # Index (English)
├── README.zh-CN.md              # Index (简体中文)
├── LICENSE                      # CC BY-NC 4.0
└── skills/
    ├── tryworld-koubo/      # Voiceover entry (router + email notice)
    ├── tryworld-paper/     # Paper Algorithm video production
    ├── tryworld-topics/     # AIHOT topic selection
    ├── tryworld-research/         # Horizontal–Vertical deep research
    └── tryworld-write/              # WeChat long-form writing
```

## 🛠 Tech Stack

| Skill | Built with |
|---|---|
| tryworld-paper | HyperFrames · edge-tts (Azure YunxiNeural) · FFmpeg · Node.js ≥ 22 · Python 3.10+ |
| tryworld-topics | PowerShell / curl · AIHOT API |
| tryworld-research | Python · WeasyPrint · Markdown |
| tryworld-koubo | Orchestrates the above · `qq-email` (SMTP / IMAP) |
| tryworld-write | — |

## ⚖️ License

This work is licensed under a **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)** license: share and adapt freely for **non-commercial** purposes, with attribution. Commercial use is not permitted. Full terms: [LICENSE](LICENSE).

[![CC BY-NC 4.0](assets/license-badge.svg)](https://creativecommons.org/licenses/by-nc/4.0/)

---

<p align="center"><sub>TryWorld · Making AI clear for everyone</sub></p>