# Changelog

所有显著改动记录在此文件中。格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。

## [Unreleased]

_本区记录 `[1.1.0]` 之后、尚未发布的所有改动；发布时把本区内容并入新的版本号。_

## [1.1.0] - 2026-10-24

自 `[1.0.0]` 以来的全部改动（含 2026-09-22 的 runner/测试批次与 2026-10-24 的第一性原理用户视角修复）。

### Added

- `tests/test_runner.py`：覆盖 pipeline runner 的参数转发、门禁拦截、运行状态文件等行为
- `tests/test_fetch_aihot.py`：覆盖 `fetch_aihot.py` 的 CLI 与 `fetch_json` 重试逻辑
- `tests/test_gate_adversarial.py`：8 个对抗式用例，固化“试图绕过用户确认闸门”的几种走法（跳过步骤 03、只传 `--confirm`、过期确认、过期活人感门禁、损坏的运行状态文件），任一步被改坏都会红
- `skills/tryworld-paper/references/workflow.md` §1.4：写明闸门的技术边界——`.prose_pass` / `.confirmed` 只绑 draft 的 sha256，防漂移不防同用户伪造，因此“等用户确认”必须是对话里真实发生的动作
- `check_prose.py --whitelist` 正式接入流水线：`step_02_check_prose.py` 与 `pipeline.runner` 新增 `--whitelist` 透传（路径按调用方 cwd 解析为绝对路径）。此前该参数只存在于脚本内、无任何文档、也无法从流水线使用。豁免是**可见退出**——命中内容不被检查，运行会打印 `NOTE:` 行
- 技术记法标点豁免：数字间的 `16:9`、`4:3`、`12:30`、`2024–2026` 不再判违规（降为提示）。此前这类写法被标点禁令硬拦（exit 1），而它们是这一内容品类绕不开的写法；`：` 提示性冒号、`——` 破折号、带空格的 `12 :30`、词间 `–` 照旧拦截
- `tests/test_prose.py`：新增 8 例覆盖豁免边界（比例/时间/区间放行；提示性冒号、破折号、词间连接号、带空格形式仍拦）与白名单行为（含非法正则不崩溃）

### Changed

- `pipeline/runner.py`：修复参数转发缺失（README 中的命令此前无法直接运行）、改为以模块方式调用各步骤、新增 `--list` 与运行诊断 JSON、明确报错与门禁提示
- `fetch_aihot.py`：新增 `--base-url`（默认 `https://aihot.virxact.com`），与 `.ps1` 回退脚本的 `-BaseUrl` 对齐
- `scripts/notify_delivery.ps1`、`skills/tryworld-topics/scripts/fetch_aihot.ps1`、`scripts/doctor.ps1`：标注为已废弃的 Windows 回退脚本，`.py` 为唯一规范路径
- `README.md` / `README.zh-CN.md` / `CONTRIBUTING.md` / 各 `SKILL.md` / `references/`：统一指向 `.py` 脚本，移除 `.ps1` 作为规范路径的表述
- `pipeline/steps/step_04_tts.py`：澄清 `--theme-content` 帮助文本（品牌/视觉主题，默认 `themes/paper-algorithm.json`），并提示与 step 01 的“内容主题”同名不同义
- `CHANGELOG.md`：将此前 `[Unreleased]` 内容并入 `[1.0.0]`，改为真正的“未发布”区
- `pipeline/steps/step_01_optimize.py` → `step_01_ingest.py`：该步骤一直逐字复制输入，却命名为 optimize 并让用户“审阅 draft.md”，暗示稿子已被润色。改名并改正 docstring、argparse 描述与 `ACTION REQUIRED` 输出，明确“这是逐字副本，优化与净化由 agent 按 SKILL.md 完成，改完重跑步骤 02”；`step_02` 的提示语与 README×2 步骤清单同步为 `01 ingest`
- README（中英）「Pipeline Runner」：如实说明 Runner 是步骤 2–4 的门禁记账器，不写稿也不渲染；步骤 05/06 依赖没有任何步骤会生成的构图，只在项目已存在时执行
- README（中英）「活人感门禁」：删去“禁的是修辞动作不是字面，换词仍算命中”这一与实现不符的说法，改为写清——约 22 类信号中只有 5 类能判失败（标点、硬停词、绝对黑话、模型路标、翻案句式），其余为交给人判断的提示；规则是字面正则与词表，换词改写可能漏网；真正的活人感来自 §1.2.1 七遍改稿指令，无脚本强制
- `references/workflow.md` §1.2.1 第 5 条与 `references/titles.md`：标点口径与检查器同步（技术记法豁免、白名单用法），避免散文与代码漂移

### Fixed

- `README.md` / `README.zh-CN.md`：测试数量不再硬编码，改为引导用 `pytest --collect-only` 读取实际数量
- `verify_output.py`：ffprobe/ffmpeg 发现逻辑与 `tts_yunxi.py` 的 `find_bin` 对齐（PATH 优先 → `HYPERFRAMES_FFMPEG_DIR` / `FFMPEG_BIN` → WinGet 目录），PATH 未配置时不再直接判定“工具不可用”而退出
- `pipeline/runner.py`：在仓库根目录以外启动时，用户写的相对路径不再解析错位（步骤以 `cwd=REPO` 运行，runner 现在先把 `--project-dir` / `--script` / `--theme-content` / `--video` 解析为绝对路径）；`--steps` 容忍空格与空 token（如 `"1, 2,"`），非法 token 的报错直接指出问题值
- `fetch_aihot.py`：`--base-url` 归一化去掉尾部斜杠，避免拼出 `//api/...`
- `notify_delivery.ps1` / `fetch_aihot.ps1`：DEPRECATED 头中的规范路径改为仓库相对路径，避免与 `scripts/` 混淆
- `skills/tryworld-koubo/SKILL.md:21` 与 `skills/tryworld-topics/SKILL.md:12`：修复被转义吃成制表符的路径与字段名（`\tryworld-paper/...`、`\topic_sources`、`\topic_rules`）。这些引用自 `6f81f86`（2026-09-01）起在任何安装环境中都无法解析，本次在 git blob 层修复

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