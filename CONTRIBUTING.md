# 贡献指南

感谢你对本项目感兴趣。在提交 PR 之前，请先阅读本指南。

## 行为准则

参与本项目即表示你同意遵守 [行为准则](CODE_OF_CONDUCT.md)。

## 项目结构

```text
paper-algorithm/
├── skills/                      # 三个技能（口播工作流、出片、选题）
│   ├── tryworld-koubo/          # 口播总入口（选题 → 写稿 → 出片路由）
│   ├── tryworld-paper/          # 出片技能（视觉/配音/渲染/交付核验）
│   └── tryworld-topics/         # 选题技能（AIHOT 数据 → 选题清单）
├── scripts/                     # 仓库级检查脚本
│   ├── check_skills.py          # 编译技能脚本 + 跑活人感门禁
│   └── doctor.ps1               # 环境自检
├── examples/                    # 默认主题产出的示例
└── README.md / README.zh-CN.md  # 中英索引
```

## 可以贡献什么

### 1. 新品牌主题

复制 `skills/tryworld-paper/themes/paper-algorithm.json` 为你的主题文件，按 [theme-guide.md](skills/tryworld-paper/references/theme-guide.md) 修改品牌值。PR 时：

- 附一版 720p 预览视频（放在 PR 描述的链接里即可，不进仓库）
- 确认色板对比度 ≥ 4.5:1（大字 ≥ 3:1）
- 确认新印章 SVG 右上角常驻且不遮挡内容

### 2. 流水线脚本改进

`skills/tryworld-paper/scripts/` 下的 Python 脚本（tts_yunxi / check_prose / verify_output）。PR 要求：

- 不破坏现有流水线契约（见 SKILL.md「流水线契约」章节）
- 附加最小测试或验证步骤说明
- 不引入新的第三方依赖（除非必要并在 PR 说明理由）

### 3. 文档改进

错字、表述不清、缺少说明的段落，直接改，不需要开 Issue 讨论。

### 4. 示例

欢迎提交用你自己的品牌主题产出的示例（口播稿 + 标题 + 截图链接）。示例视频本体不进仓库（体积大），PR 描述附预览链接。

## 不接受什么

- 违反流水线契约的改动（去掉用户确认闸门、去掉硬禁项检查、去掉交付核验等）
- 在主题或示例中包含他人商标或未授权的音色克隆
- 改变根目录 LICENSE（CC BY-SA 4.0）或 `skills/tryworld-paper/LICENSE-MIT` 的归属声明

## 提交流程

1. Fork → 新建分支 → 改动 → commit
2. 本地跑通过再提交 PR：
   ```powershell
   python -X utf8 scripts/check_skills.py   # 应输出 All checks passed
   git diff --check                          # 应无输出
   ```
3. PR 描述写清楚：改了什么、为什么、验证方法

## 提问

Bug 或功能建议请开 [Issue](https://github.com/TryWorld2026/paper-algorithm/issues)，模板里有引导。