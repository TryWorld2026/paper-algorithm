<p align="center">
  <img src="assets/hero.svg" alt="TryWorld" width="100%">
</p>

<p align="right"><sub>English · <a href="README.zh-CN.md">简体中文</a> · <a href="docs/index.html">HTML edition</a></sub></p>

---

<p align="center">
  <b>TryWorld · A Collection of Codex Skills</b><br>
  <sub>Five skills, one content pipeline: topic · script · video · research · writing</sub>
</p>

## Skills

<details open>
<summary><b>01 · tryworld-koubo-pipeline</b> — voiceover entry point, auto-routing</summary>

- Detects Mode A (script given) and Mode B (pick a topic); sub-commands; dedup by finished deliverables; automatic email notice after delivery.
- Deliverables: full delivery · email notice
- Depends on: other skills · `qq-email`

</details>

<details>
<summary><b>02 · tryworld-paper-algorithm</b> — Paper Algorithm video production</summary>

- Script → Azure YunxiNeural voiceover → HyperFrames composition & render → covers, titles, captions; the vermillion「试界原创」seal stays throughout.
- Deliverables: video · covers · titles
- Depends on: HyperFrames · edge-tts · FFmpeg

</details>

<details>
<summary><b>03 · tryworld-koubo-selection</b> — AI-news topic selection</summary>

- Pulls curated AIHOT items, scores them against growth principles; each candidate ships with an angle, source links, and priority; auto-skips produced topics.
- Deliverables: 3–8 candidate topics
- Depends on: AIHOT API · PowerShell / curl

</details>

<details>
<summary><b>04 · tryworld-hv-analysis</b> — Horizontal–Vertical deep research</summary>

- Trace the life arc vertically, compare the landscape horizontally, cross the two axes for insight; outputs a polished PDF report.
- Deliverables: PDF research report
- Depends on: Python · WeasyPrint · Markdown

</details>

<details>
<summary><b>05 · tryworld-writer</b> — WeChat long-form writing</summary>

- Turns source material (PDF / links / transcripts / briefs) into a TryWorld-style WeChat article.
- Deliverables: finished long-form article
- Depends on: —

</details>

## Workflow

```mermaid
flowchart LR
    U(["One sentence"]) --> P["tryworld-koubo-pipeline"]
    P -- "Mode A · script given" --> A["tryworld-paper-algorithm<br/>Optimize → confirm → produce"]
    P -- "Mode B · pick a topic" --> S["tryworld-koubo-selection<br/>AIHOT news → topic list"]
    S -- "you choose" --> A
    A --> O["Deliverables<br/>Video · covers · titles · schedule"]
    O -. "automatic" .-> M["Email notice<br/>Deliverables + publish times"]
```

For the video pipeline, remember one entry: `$tryworld-koubo-pipeline`. `tryworld-hv-analysis` and `tryworld-writer` are standalone.

## Design System · Paper Algorithm

Paper is the stage, ink is the text, vermillion is the accent, the seal is the signature.

| Swatch | Value | Role |
|---|---|---|
| Paper | `#F4EFE4` | Background |
| Ink | `#1C1916` | Text & lines |
| Vermillion | `#C0452F` | The only accent |
| Ink Blue | `#2E5E8C` | Secondary notes |

Type: Noto Serif SC · LXGW WenKai · monospace. Motion: ink drop, brush stroke, seal stamp.

## Install

Each skill folder is self-contained. Copy it into your local skills directory:

```powershell
Copy-Item -Path .\skills\* -Destination "$env:USERPROFILE\.codex\skills" -Recurse
```

`~/.agents/skills` works on other hosts too. Then just say: "Make me a TryWorld voiceover video."

## Layout

```text
tryworld-skills/
├── assets/                  # hero, license badge
├── docs/index.html          # full HTML design edition
├── README.md                # English
├── README.zh-CN.md          # 简体中文
├── LICENSE                  # CC BY-NC 4.0
└── skills/                  # five skills
```

## License

Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0): share and adapt freely for **non-commercial** purposes, with attribution. Commercial use is not permitted. Full terms: [LICENSE](LICENSE).

[![CC BY-NC 4.0](assets/license-badge.svg)](https://creativecommons.org/licenses/by-nc/4.0/)

---

<p align="center"><sub>TryWorld · Making AI clear for everyone — set in Paper Algorithm · MMXXVI</sub></p>