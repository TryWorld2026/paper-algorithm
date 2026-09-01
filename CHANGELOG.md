# Changelog

所有显著改动记录在此文件中。格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。

## [Unreleased]

### Added

- `scripts/check_skills.py`：仓库级检查脚本，编译技能 Python 脚本并跑活人感门禁
- `scripts/doctor.ps1`：环境自检脚本（Python / Node / FFmpeg / edge-tts / HyperFrames / 邮件凭证）
- `CONTRIBUTING.md` 贡献指南
- `CODE_OF_CONDUCT.md` 行为准则
- GitHub Issue 模板与 CI workflow
- 主题文件 `publish_plan` 字段：发布计划平台与时间可按品牌主题配置
- 通知邮件脚本 `-ThemeFile` 参数：邮件主题与正文从主题文件读取品牌名与发布计划（可选参数，缺失时回退默认值）

### Changed

- `verify_output.py`：加固多 mp4 判 FAIL（`--video` 可指定主视频）、视频流检查、ffprobe 缺失兜底、`dur_f` 作用域修复
- `verify_output.py`：兼容中文交付命名（`封面_横版4x3.png` / `封面_竖版3x4.png`）
- `tts_yunxi.py`：`--theme` 参数从主题 JSON 读取默认音色
- `check_prose.py`：冒号分级（引出原话放行、提示性冒号仍禁）、示例标题改为逗号 PASS
- `README.md` / `README.zh-CN.md`：补入 `scripts/` 目录与检查脚本说明
- `skills/tryworld-paper/README.md`：目录结构补入 `verify_output.py`、工作流图补入交付核验步骤
- `skills/tryworld-paper/references/workflow.md`：发布计划.txt 补入交付清单、删重复 plan.json
- `skills/tryworld-koubo/SKILL.md`：补品牌适配边界段
- `examples/README.md`：披露 cursor-spacex 口播稿标点修正