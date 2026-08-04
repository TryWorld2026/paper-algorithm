<h1 align="center">TryWorld Skills</h1>

<p align="center">
  <b>A collection of Codex Skills by 试界 TryWorld</b><br/>
  topic selection · scriptwriting · video production · deep research · long-form writing
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
  <b><a href="README.md">English</a></b> · <a href="README.zh-CN.md">简体中文</a>
</p>

---

## Skills at a glance

| Icon | Skill | What it does | Key deliverables |
|---|---|---|---|
| 🎬 | [tryworld-koubo-pipeline](skills/tryworld-koubo-pipeline/) | **Single entry point** for the voiceover video workflow; auto-routes to the right skill | End-to-end delivery: topic → script → video → publishing plan |
| 📜 | [tryworld-paper-algorithm](skills/tryworld-paper-algorithm/) | Produces branded “Paper Algorithm” style AI knowledge videos | Main video, horizontal & vertical covers, platform titles |
| 🎯 | [tryworld-koubo-selection](skills/tryworld-koubo-selection/) | Picks video topics from the latest AIHOT AI news | 3–8 candidate topics with angles & source links |
| 🔬 | [tryworld-hv-analysis](skills/tryworld-hv-analysis/) | Deep research with Horizontal-Vertical Analysis | Polished PDF research report |
| ✍️ | [tryworld-writer](skills/tryworld-writer/) | Long-form WeChat article writing in TryWorld's style | Long-form article |

## How the skills fit together

```mermaid
flowchart LR
    U(["User request"]) --> P["🎬 tryworld-koubo-pipeline<br/>Single entry point"]
    P -- "Mode A: script given" --> A["📜 tryworld-paper-algorithm<br/>Optimize → produce"]
    P -- "Mode B: need topics" --> S["🎯 tryworld-koubo-selection<br/>AIHOT topic picks"]
    S --> A
    A --> O["✅ Deliverables<br/>Video / covers / titles / schedule"]
    H["🔬 tryworld-hv-analysis<br/>Deep research"] -. "Standalone" .-> R["📄 PDF report"]
    W["✍️ tryworld-writer<br/>Long-form writing"] -. "Standalone" .-> C["📝 WeChat article"]
```

For video work, just remember `$tryworld-koubo-pipeline`: give it a script (Mode A) or ask for topics (Mode B), and it routes to the other skills for you. `tryworld-hv-analysis` and `tryworld-writer` are standalone — call them directly when needed.

## Tech stack

| Skill | Built with |
|---|---|
| tryworld-paper-algorithm | HyperFrames, edge-tts (Azure YunxiNeural), FFmpeg, Node.js ≥ 22, Python 3.10+ |
| tryworld-koubo-selection | PowerShell script / curl, AIHOT API |
| tryworld-hv-analysis | Python, WeasyPrint, Markdown |
| tryworld-writer | — |
| tryworld-koubo-pipeline | Router on top of the skills above |

## Quick start

Every skill folder is a self-contained Skill. Copy it into your local skills directory (Windows example):

```powershell
# Install all skills
Copy-Item -Path .\skills\* -Destination "$env:USERPROFILE\.codex\skills" -Recurse

# Or install a single skill
Copy-Item -Path .\skills\tryworld-paper-algorithm -Destination "$env:USERPROFILE\.codex\skills" -Recurse
```

`~/.agents/skills` works on other hosts as well. Then call the skill by name:

```text
Use $tryworld-koubo-pipeline to make a video from this voiceover script.
```

## Repository layout

```text
tryworld-skills/
├── README.md                 # Index (English)
├── README.zh-CN.md           # Index (简体中文)
└── skills/
    ├── tryworld-koubo-pipeline/     # Voiceover workflow entry (router)
    ├── tryworld-paper-algorithm/    # Paper Algorithm video production
    ├── tryworld-koubo-selection/    # AIHOT topic selection
    ├── tryworld-hv-analysis/        # Horizontal-Vertical deep research
    └── tryworld-writer/             # WeChat long-form writing
```

## License

All rights reserved. No license is attached to this repository yet.
