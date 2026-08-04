<div align="center">

![TryWorld Skills Hero](assets/hero.svg)

# TryWorld Skills

### An Operating System for AI-First Creators

> Not a repo of one-liners.  
> A curated system of **research**, **selection**, **writing**, and **production** workflows — designed to move from noise to a deliverable.

<br/>

[![GitHub stars](https://img.shields.io/github/stars/TryWorld2026/tryworld-skills?style=social)](https://github.com/TryWorld2026/tryworld-skills)
[![License](https://img.shields.io/badge/license-MIT-success?style=for-the-badge)](LICENSE)
[![Docs](https://img.shields.io/badge/docs-index.html-0a0a0a?style=for-the-badge&logo=readthedocs&logoColor=white)](docs/index.html)
[![GitHub](https://img.shields.io/badge/GitHub-TryWorld2026%2Ftryworld--skills-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/TryWorld2026/tryworld-skills)

</div>

---

## This is not a skills dump.

Most AI skill repos are a pile of prompts, shotguns of shortcut phrases, and pages that look finished but still leave you editing the same draft three hours later.

**TryWorld Skills is built around a different premise:**  
if you want better output, you need a better workflow, not more prompt fragments.

Each skill here is a **repeatable sequence** with:
- **input contract**
- **process logic**
- **output format**
- **handoff rules**

That means you can use it alone, or stack it end-to-end.

---

## What You Get

| Skill | What It Does | Best For |
|---|---|---|
| `tryworld-hv-analysis` | **Horizontal + vertical research** | Products, companies, industries, concepts, people |
| `tryworld-koubo-selection` | **Topic selection system** | Finding AI video topics that are publishable |
| `tryworld-koubo-pipeline` | **Content production pipeline** | Turning topic ideas into scripts, covers, and checklists |
| `tryworld-paper-algorithm` | **Paper/algorithm explainer system** | Technical deep dives with consistent visual language |
| `tryworld-writer` | **Long-form writing system** | Columns, newsletters, and publishable essays |

This repo is designed so these skills become a **content operating system**, not isolated fragments.

---

## Recommended Flow

```text
Research
  -> tryworld-hv-analysis

Distribution topics
  -> tryworld-koubo-selection
  -> tryworld-koubo-pipeline

Technical storytelling
  -> tryworld-paper-algorithm

Deep writing
  -> tryworld-writer
```

You can:
- **use one skill** for a single task
- **chain them** for research → topic → production → writing

---

## Why This Repo Exists

**If you only remember one thing:**  
the goal is not to write a better prompt.  
The goal is to **simplify decisions, tighten drafts, and hand off cleaner work**.

This repo is built around four principles:
1. **Task first.** Organize by outcome, not by model.
2. **Workflow first.** Prompting is only one component.
3. **Quality first.** Lean toward research depth, structure clarity, and execution discipline.
4. **Human-ready.** Keep ownership, judgment, and editorial voice with you.

---

## How To Use

```bash
git clone https://github.com/TryWorld2026/tryworld-skills.git
cd tryworld-skills/skills/<skill-name>
```

Each skill has:
- `SKILL.md` for the main workflow
- `references/` for rules, templates, and methodology
- `scripts/` for execution support
- `assets/` for visual system files

You do not need to install this as a package.  
You can copy or reference the skill directly.

---

## Skill Highlights

### tryworld-hv-analysis
- Horizontal comparison
- Longitudinal development mapping
- Source verification
- Risk identification
- Research conclusions that can be reviewed by another person

### tryworld-koubo-selection
- Input parsing and topic decoding
- Hot-trend mining
- Channel-based selection rules
- Output scoring by feasibility, expressiveness, and differentiation

### tryworld-koubo-pipeline
- Two main modes: topic-first or script-first
- Draft review and upgrade path
- Cover, metadata, title, and delivery checklist generation
- One-flow path from rough idea to publishable clip

### tryworld-paper-algorithm
- Paper-algorithm visual storytelling format
- Script cleanup and storytelling upgrade
- Consistent 16:9 master video, 4:3 and 3:4 covers
- Platform title optimization and caption design

### tryworld-writer
- HKR-style idea screening
- Human voice and judgment retention
- Expansion, condensation, and rewriting
- Publication-ready long-form output

---

## File Structure

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

## Contribution

If you want to improve output quality instead of adding more abstract descriptions, this repo is open to improvement in:
- new task-level skills
- better references and evaluation criteria
- clearer handoff formats
- richer examples and execution scripts

Open an issue or pull request.

---

## License

MIT