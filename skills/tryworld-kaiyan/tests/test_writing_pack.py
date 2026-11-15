from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check_script.py"
EXAMPLES = sorted((ROOT / "examples").glob("*.md"))

REQUIRED_SECTIONS = [
    "## 1 选题卡",
    "## 2 事实来源表",
    "## 3 主稿",
    "## 4 视频标题",
    "## 5 平台变体",
    "## 6 轻提示",
    "## 7 自检报告",
]

PLATFORMS = ["抖音", "视频号", "小红书", "B站"]
ALLOWED_CUES = {"停顿", "重音", "交给画面"}
TITLE_LIMITS = {
    "主标题": 8,
    "抖音": 6,
    "视频号": 6,
    "小红书": 8,
    "B站": 8,
}
TITLE_LINE = re.compile(
    r"(?m)^\s*(?:-\s*)?\*{0,2}(主标题|抖音|视频号|小红书|B站)\*{0,2}："
    r"(.+?)（(\d+) 个非空白字符）$"
)


def h2_headings(text: str) -> list[str]:
    return re.findall(r"(?m)^##\s+.+$", text)


def section(text: str, heading: str, next_heading: str) -> str:
    start = text.index(heading)
    end = text.index(next_heading, start)
    return text[start + len(heading) : end]


def title_map(text: str) -> dict[str, tuple[str, int]]:
    titles = {
        label: (title.strip(), int(count))
        for label, title, count in TITLE_LINE.findall(text)
    }
    return titles


def platform_blocks(text: str) -> dict[str, str]:
    pattern = re.compile(
        r"(?ms)^### (抖音|视频号|小红书|B站)\n(.*?)(?=^### |^## |\Z)"
    )
    return {name: body for name, body in pattern.findall(text)}


class WritingPackStructureTests(unittest.TestCase):
    def test_template_has_exact_seven_sections(self) -> None:
        text = (ROOT / "templates" / "writing-pack.md").read_text(encoding="utf-8")
        self.assertEqual(h2_headings(text), REQUIRED_SECTIONS)

    def test_template_has_all_four_platforms(self) -> None:
        text = (ROOT / "templates" / "writing-pack.md").read_text(encoding="utf-8")
        for platform in PLATFORMS:
            self.assertIn(f"### {platform}", text)
        self.assertEqual(text.count("**开头**"), 4)
        self.assertEqual(text.count("**收尾**"), 4)

    def test_template_has_title_review_and_brand_signature(self) -> None:
        text = (ROOT / "templates" / "writing-pack.md").read_text(encoding="utf-8")
        titles = section(text, "## 4 视频标题", "## 5 平台变体")
        self.assertIn("**主标题**", titles)
        for platform in PLATFORMS:
            self.assertIn(f"| {platform} |", titles)
        self.assertIn("12 个候选", titles)
        self.assertIn("前 5 名", titles)
        self.assertIn("加权", titles)
        self.assertIn("哈喽，我是", text)
        self.assertIn("下次见", text)

    def test_topic_history_schema(self) -> None:
        path = ROOT / "state" / "topic-history.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        self.assertIsInstance(value, dict)
        self.assertIsInstance(value.get("topics"), list)
        for item in value["topics"]:
            self.assertIsInstance(item, dict)
            for key in ("date", "slug", "title", "angle", "status"):
                self.assertIn(key, item)
            self.assertIn(item["status"], {"proposed", "selected", "written"})

    def test_skill_frontmatter_and_trigger_boundary(self) -> None:
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
        self.assertIsNotNone(match, "SKILL.md 缺少可解析的 frontmatter")
        frontmatter = match.group(1)
        self.assertIn("name: tryworld-kaiyan", frontmatter)
        description = next(
            line for line in frontmatter.splitlines() if line.startswith("description:")
        )
        for trigger in ("写口播稿", "试界开言", "改这篇口播稿"):
            self.assertIn(trigger, description)
        self.assertIn("不产出封面、配音、分镜", description)

    def test_skill_referenced_files_exist(self) -> None:
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        references = set(
            re.findall(r"`((?:references|templates)/[^`]+\.md)`", text)
        )
        self.assertGreaterEqual(len(references), 7)
        for relative in references:
            with self.subTest(path=relative):
                self.assertTrue((ROOT / relative).is_file(), relative)


class ExampleTests(unittest.TestCase):
    def test_examples_exist(self) -> None:
        self.assertGreaterEqual(len(EXAMPLES), 2)

    def test_every_example_has_exact_seven_sections(self) -> None:
        for path in EXAMPLES:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertEqual(h2_headings(text), REQUIRED_SECTIONS)

    def test_every_example_has_evidence_table_and_platforms(self) -> None:
        for path in EXAMPLES:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                evidence = section(
                    text, "## 2 事实来源表", "## 3 主稿"
                )
                for header in ("稿件中的说法", "来源与发布者", "日期", "链接", "核验内容与限制"):
                    self.assertIn(header, evidence)
                self.assertGreaterEqual(
                    len(re.findall(r"(?m)^\|\s*[^|-]", evidence)),
                    3,
                    "来源表至少需要两条数据行",
                )
                platforms = section(
                    text, "## 5 平台变体", "## 6 轻提示"
                )
                for platform in PLATFORMS:
                    self.assertIn(f"### {platform}", platforms)
                self.assertEqual(platforms.count("**开头**"), 4)
                self.assertEqual(platforms.count("**收尾**"), 4)

    def test_every_example_has_valid_titles(self) -> None:
        for path in EXAMPLES:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                titles = title_map(section(text, "## 4 视频标题", "## 5 平台变体"))
                self.assertEqual(set(titles), set(TITLE_LIMITS))
                for label, (title, stated_count) in titles.items():
                    self.assertTrue(title)
                    actual_count = len(re.sub(r"\s+", "", title))
                    self.assertEqual(actual_count, stated_count, label)
                    self.assertLessEqual(actual_count, TITLE_LIMITS[label], label)

    def test_every_example_has_title_adversarial_review(self) -> None:
        for path in EXAMPLES:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                titles = section(text, "## 4 视频标题", "## 5 平台变体")
                self.assertIn("### 第一轮：12 个候选", titles)
                angles = re.findall(
                    r"(?m)^\|\s*(反常识|代价或损失|具体利益|好奇缺口|身份点名|前后对比)\s*\|",
                    titles,
                )
                self.assertEqual(len(angles), 6, "六种角度必须各有两个候选")
                self.assertIn("### 第二轮：前 5 名互相攻击", titles)
                self.assertIn("### 第三轮：三角色与加权决赛", titles)
                attacks = re.findall(r"(?m)^- \*\*.+?\*\*：", titles)
                self.assertGreaterEqual(len(attacks), 5)

    def test_every_example_uses_short_brand_open_and_fixed_signoff(self) -> None:
        for path in EXAMPLES:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                main = section(text, "## 3 主稿", "## 4 视频标题").strip()
                self.assertRegex(main, r"\A哈喽，我是[^\n。]{1,40}。")
                self.assertRegex(main, r"我是[^\n，。]{1,40}，下次见。\Z")

    def test_platform_brand_rules(self) -> None:
        for path in EXAMPLES:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                platforms = section(text, "## 5 平台变体", "## 6 轻提示")
                blocks = platform_blocks(platforms)
                self.assertEqual(set(blocks), set(PLATFORMS))
                for platform in ("抖音", "小红书"):
                    self.assertNotIn("哈喽，我是", blocks[platform].split("**收尾**")[0])
                for platform in ("视频号", "B站"):
                    self.assertIn("哈喽，我是", blocks[platform].split("**收尾**")[0])
                for block in blocks.values():
                    self.assertIn("下次见", block.split("**收尾**")[1])

    def test_only_allowed_light_cues_and_no_storyboard(self) -> None:
        for path in EXAMPLES:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                cues = section(text, "## 6 轻提示", "## 7 自检报告")
                labels = set(re.findall(r"\[([^\]\n]+)\]", cues))
                self.assertTrue(labels)
                self.assertLessEqual(labels, ALLOWED_CUES)
                for banned in ("景别", "运镜", "转场", "机位", "灯光", "配乐", "音效", "分镜"):
                    self.assertNotIn(banned, cues)

    def test_every_example_main_script_passes_checker(self) -> None:
        for path in EXAMPLES:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                main = section(text, "## 3 主稿", "## 4 视频标题").strip()
                titles = title_map(section(text, "## 4 视频标题", "## 5 平台变体"))
                self.assertIn("主标题", titles)
                self.assertTrue(main)
                with tempfile.TemporaryDirectory() as directory:
                    script = Path(directory) / "main.txt"
                    script.write_text(main + "\n", encoding="utf-8")
                    result = subprocess.run(
                        [
                            sys.executable,
                            "-X",
                            "utf8",
                            str(CHECKER),
                            str(script),
                            "--title",
                            titles["主标题"][0],
                            "--platform",
                            "master",
                            "--json",
                        ],
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                        cwd=str(ROOT),
                        check=False,
                    )
                    self.assertEqual(
                        result.returncode,
                        0,
                        f"{path.name} 未通过检查器\n{result.stdout}\n{result.stderr}",
                    )
                    report = json.loads(result.stdout)
                    self.assertTrue(report["passed"])
                    self.assertGreaterEqual(report["metrics"]["han"], 550)
                    self.assertLessEqual(report["metrics"]["han"], 800)

    def test_examples_do_not_claim_personal_testing(self) -> None:
        forbidden = ("我试过", "我用了", "我亲测", "我朋友", "亲身体验")
        for path in EXAMPLES:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                main = section(text, "## 3 主稿", "## 4 视频标题")
                platforms = section(text, "## 5 平台变体", "## 6 轻提示")
                for phrase in forbidden:
                    self.assertNotIn(phrase, main + platforms)


if __name__ == "__main__":
    unittest.main()
