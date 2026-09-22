# Changelog

所有显著改动记录在此文件中。格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。

## [Unreleased]

_本分支（`refactor/runner-fixes-docs-consolidation`）的改动记录见下文；发布时再并入正式版本号。_

### Added

- `tests/test_runner.py`：覆盖 pipeline runner 的参数转发、门禁拦截、运行状态文件等行为
- `tests/test_fetch_aihot.py`：覆盖 `fetch_aihot.py` 的 CLI 与 `fetch_json` 重试逻辑

### Changed

- `pipeline/runner.py`：修复参数转发缺失（README 中的命令此前无法直接运行）、改为以模块方式调用各步骤、新增 `--list` 与运行诊断 JSON、明确报错与门禁提示
- `fetch_aihot.py`：新增 `--base-url`（默认 `https://aihot.virxact.com`），与 `.ps1` 回退脚本的 `-BaseUrl` 对齐
- `scripts/notify_delivery.ps1`、`skills/tryworld-topics/scripts/fetch_aihot.ps1`、`scripts/doctor.ps1`：标注为已废弃的 Windows 回退脚本，`.py` 为唯一规范路径
- `README.md` / `README.zh-CN.md` / `CONTRIBUTING.md` / 各 `SKILL.md` / `references/`：统一指向 `.py` 脚本，移除 `.ps1` 作为规范路径的表述
- `pipeline/steps/step_04_tts.py`：澄清 `--theme-content` 帮助文本（品牌/视觉主题，默认 `themes/paper-algorithm.json`），并提示与 step 01 的“内容主题”同名不同义
- `CHANGELOG.md`：将此前 `[Unreleased]` 内容并入 `[1.0.0]`，改为真正的“未发布”区

### Fixed

- `README.md` / `README.zh-CN.md`：测试数量不再硬编码，改为引导用 `pytest --collect-only` 读取实际数量
- `verify_output.py`：ffprobe/ffmpeg 发现逻辑与 `tts_yunxi.py` 的 `find_bin` 对齐（PATH 优先 → `HYPERFRAMES_FFMPEG_DIR` / `FFMPEG_BIN` → WinGet 目录），PATH 未配置时不再直接判定“工具不可用”而退出
- `pipeline/runner.py`：在仓库根目录以外启动时，用户写的相对路径不再解析错位（步骤以 `cwd=REPO` 运行，runner 现在先把 `--project-dir` / `--script` / `--theme-content` / `--video` 解析为绝对路径）；`--steps` 容忍空格与空 token（如 `"1, 2,"`），非法 token 的报错直接指出问题值
- `fetch_aihot.py`：`--base-url` 归一化去掉尾部斜杠，避免拼出 `//api/...`
- `notify_delivery.ps1` / `fetch_aihot.ps1`：DEPRECATED 头中的规范路径改为仓库相对路径，避免与 `scripts/` 混淆

## [1.0.0] - 2026-09-05

首个正式版本。

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