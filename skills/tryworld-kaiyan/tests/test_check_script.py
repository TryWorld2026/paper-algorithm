from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check_script.py"


FULL_PARAGRAPHS = [
    [
        "很多人还把 AI 当成一个更聪明的搜索框。",
        "它回答得快，不代表它能替你办事。",
        "真正进入工作以后，变化不在聊天窗口。",
        "变化在它能不能接住一件完整的小事。",
    ],
    [
        "你每天都有不少重复动作。",
        "找资料，改格式，核对信息，再把结果发给别人。",
        "每件事都不难，却会一起吃掉下午。",
        "AI 的价值，就看你愿不愿意把其中一段交给它。",
    ],
    [
        "公开资料里，已经有不少产品开始处理这种连续任务。",
        "它们会读取你允许的文件，调用你授权的工具，再把结果放回原来的位置。",
        "这里的关键不在演示有多热闹。",
        "关键是每一步都要留下确认，也要能撤回。",
    ],
    [
        "所以别把自动化想成按一下按钮就完事。",
        "能跑通的任务，通常边界清楚，结果也能检查。",
        "涉及付款、发布和删除的操作，仍然需要你亲手确认。",
        "少了这一步，效率越高，返工越贵。",
    ],
    [
        "一个常见的场景，是每周整理同一批表格。",
        "以前你要复制、粘贴、核对，再写一段说明。",
        "现在可以让工具先做草稿，你只看错漏和判断。",
        "省下来的常常是反复切窗口的注意力，打字时间反而没那么多。",
    ],
    [
        "这也解释了为什么演示很好看，落到自己工作里却常常卡住。",
        "工具不知道你的验收标准，也不知道哪些错误不能接受。",
        "你要先把规则说清楚，它才有可能稳定执行。",
        "规则越具体，后面返工越少。",
        "拿写周报举例，你可以把素材来源和格式要求提前写清。",
        "工具先整理初稿，再标出证据不足的地方。",
        "你只需要做判断，不用从头敲一遍。",
        "每周复盘一次，把常错的地方补进规则。",
        "下一次它就会少犯同类错误。",
    ],
    [
        "你可以先挑一件每周都做的小事。",
        "把输入、步骤和验收标准写下来，再交给工具试一次。",
        "先让它做草稿，你来决定最后一步。",
        "今天花十分钟找出这件小事，比再收藏十个工具更有用。",
    ],
]

SHORT_PARAGRAPHS = FULL_PARAGRAPHS[:4] + [
    [
        "先选一件每周都做的小事。",
        "把步骤写清楚，让工具试一次。",
        "你只检查结果，最后一步自己确认。",
    ]
]


def join_paragraphs(paragraphs: list[list[str]]) -> str:
    return "\n\n".join("".join(paragraph) for paragraph in paragraphs)


def full_script() -> str:
    return join_paragraphs(FULL_PARAGRAPHS)


def short_script() -> str:
    return join_paragraphs(SHORT_PARAGRAPHS)


class CheckerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)

    def write(self, text: str, name: str = "script.md") -> Path:
        path = self.root / name
        path.write_text(text, encoding="utf-8")
        return path

    def run_checker(
        self, text: str | None = None, *args: str, path: Path | None = None
    ) -> subprocess.CompletedProcess[str]:
        if path is None:
            path = self.write(text if text is not None else full_script())
        command = [sys.executable, "-X", "utf8", str(CHECKER), str(path), *args]
        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=str(ROOT),
            check=False,
        )

    def run_json(self, text: str, *args: str) -> tuple[subprocess.CompletedProcess[str], dict]:
        result = self.run_checker(text, "--json", *args)
        try:
            report = json.loads(result.stdout)
        except json.JSONDecodeError as error:
            self.fail(f"JSON 输出无法解析：{error}\nstdout={result.stdout}\nstderr={result.stderr}")
        return result, report

    def assert_hard_error(self, text: str, code: str) -> dict:
        result, report = self.run_json(text)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertFalse(report["passed"])
        self.assertIn(code, [issue["code"] for issue in report["errors"]])
        return report

    def test_valid_full_script_passes(self) -> None:
        result, report = self.run_json(full_script())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(report["passed"])
        self.assertGreaterEqual(report["metrics"]["han"], 550)
        self.assertLessEqual(report["metrics"]["han"], 800)
        self.assertEqual(report["metrics"]["paragraphs"], len(FULL_PARAGRAPHS))
        self.assertGreater(report["metrics"]["sentences"], 10)

    def test_valid_short_script_passes(self) -> None:
        result, report = self.run_json(short_script(), "--short")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(report["passed"])
        self.assertTrue(report["short"])
        self.assertGreaterEqual(report["metrics"]["han"], 300)
        self.assertLessEqual(report["metrics"]["han"], 450)

    def test_colon_is_hard_error(self) -> None:
        text = full_script().replace(
            "它回答得快，不代表它能替你办事。",
            "它回答得快：不代表它能替你办事。",
        )
        self.assert_hard_error(text, "punctuation")

    def test_em_dash_is_hard_error(self) -> None:
        text = full_script().replace(
            "每件事都不难，却会一起吃掉下午。",
            "每件事都不难——却会一起吃掉下午。",
        )
        self.assert_hard_error(text, "punctuation")

    def test_technical_punctuation_is_exempt(self) -> None:
        text = full_script().replace(
            "一个常见的场景，是每周整理同一批表格。",
            "一个常见的场景，是整理 16:9 的画面和 12:30 的记录。",
        )
        result, report = self.run_json(text)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn(
            "punctuation", [issue["code"] for issue in report["errors"]]
        )

    def test_jargon_is_hard_error(self) -> None:
        text = full_script().replace(
            "规则越具体，后面返工越少。",
            "规则越具体，越容易形成迭代闭环。",
        )
        self.assert_hard_error(text, "jargon")

    def test_pivot_is_hard_error(self) -> None:
        text = full_script().replace(
            "这里的关键不在演示有多热闹。",
            "这并不是演示有多热闹，而是任务能不能跑通。",
        )
        self.assert_hard_error(text, "pivot")

    def test_greeting_opening_is_hard_error(self) -> None:
        self.assert_hard_error("大家好。" + full_script(), "opening_greeting")

    def test_three_short_brand_signatures_pass(self) -> None:
        signatures = (
            "哈喽，我是TryWorld。",
            "哈喽大家好，我是TryWorld。",
            "我是TryWorld。",
        )
        for signature in signatures:
            with self.subTest(signature=signature):
                result, report = self.run_json(signature + full_script())
                self.assertEqual(
                    result.returncode, 0, result.stdout + result.stderr
                )
                self.assertTrue(report["passed"])
                self.assertNotIn(
                    "opening_greeting",
                    [issue["code"] for issue in report["errors"]],
                )

    def test_brand_signature_case_and_punctuation_are_flexible(self) -> None:
        signatures = (
            "哈喽, 我是 tryworld.",
            "哈喽大家好, 我是 TRYWORLD.",
            "我是tryworld.",
        )
        for signature in signatures:
            with self.subTest(signature=signature):
                result, report = self.run_json(signature + full_script())
                self.assertEqual(
                    result.returncode, 0, result.stdout + result.stderr
                )
                self.assertNotIn(
                    "opening_greeting",
                    [issue["code"] for issue in report["errors"]],
                )

    def test_brand_signature_then_direct_hook_in_same_paragraph_passes(self) -> None:
        text = "哈喽，我是TryWorld。" + full_script()
        result, report = self.run_json(text)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(report["passed"])
        self.assertNotIn(
            "opening_greeting", [issue["code"] for issue in report["errors"]]
        )

    def test_brand_signature_alone_then_direct_hook_passes(self) -> None:
        text = "哈喽，我是TryWorld。\n\n" + full_script()
        result, report = self.run_json(text)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(report["passed"])
        self.assertNotIn(
            "opening_greeting", [issue["code"] for issue in report["errors"]]
        )

    def test_brand_signature_does_not_allow_following_greeting(self) -> None:
        same_paragraph = (
            "我是TryWorld。大家好。" + full_script()
        )
        self.assert_hard_error(same_paragraph, "opening_greeting")

        next_paragraph = (
            "我是TryWorld。\n\n大家好。\n\n" + full_script()
        )
        self.assert_hard_error(next_paragraph, "opening_greeting")

        welcome = (
            "我是TryWorld。欢迎来到我的频道。" + full_script()
        )
        self.assert_hard_error(welcome, "opening_greeting")

    def test_long_brand_opening_is_still_rejected(self) -> None:
        text = (
            "哈喽大家好，欢迎来到我的频道，我是TryWorld，今天我们聊聊。"
            + full_script()
        )
        self.assert_hard_error(text, "opening_greeting")

    def test_summary_ending_is_hard_error(self) -> None:
        text = full_script() + "\n\n总的来说，这件事值得每个人认真想一想。"
        self.assert_hard_error(text, "summary_ending")

    def test_long_sentence_and_paragraph_warn(self) -> None:
        long_sentence = (
            "它们会读取你允许的文件并在你点头以后调用已经授权的工具"
            "最后再把处理结果放回你原来工作的位置。"
        )
        text = full_script().replace(
            "它们会读取你允许的文件，调用你授权的工具，再把结果放回原来的位置。",
            long_sentence,
        )
        result, report = self.run_json(text)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        codes = [issue["code"] for issue in report["warnings"]]
        self.assertIn("long_sentence", codes)

        paragraphs = ["".join(paragraph) for paragraph in FULL_PARAGRAPHS]
        collapsed = "\n".join(paragraphs[:3]) + "\n\n" + "\n\n".join(paragraphs[3:])
        result, report = self.run_json(collapsed)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        codes = [issue["code"] for issue in report["warnings"]]
        self.assertIn("long_paragraph", codes)

    def test_parallelism_warns(self) -> None:
        text = full_script().replace(
            "以前你要复制、粘贴、核对，再写一段说明。",
            "有人用它找资料，有人用它改格式，有人用它写说明。",
        )
        result, report = self.run_json(text)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(
            "parallelism", [issue["code"] for issue in report["warnings"]]
        )

    def test_missing_cta_warns(self) -> None:
        text = full_script().replace(
            "拿写周报举例，你可以把素材来源和格式要求提前写清。",
            "拿写周报举例，素材来源和格式要求最好提前写清。",
        ).replace(
            "你可以先挑一件每周都做的小事。"
            "把输入、步骤和验收标准写下来，再交给工具试一次。"
            "先让它做草稿，你来决定最后一步。"
            "今天花十分钟找出这件小事，比再收藏十个工具更有用。",
            "这件事没有统一答案。"
            "每个人的工作不同，适合的方法也不同。"
            "工具只是工具，最后的判断仍然在人手里。",
        )
        result, report = self.run_json(text)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("missing_cta", [issue["code"] for issue in report["warnings"]])

    def test_vague_judgment_warns(self) -> None:
        text = full_script().replace(
            "规则越具体，后面返工越少。",
            "这个方向很重要，未来可期。",
        )
        result, report = self.run_json(text)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(
            "vague_judgment", [issue["code"] for issue in report["warnings"]]
        )

    def test_short_length_is_enforced_for_full_script(self) -> None:
        result, report = self.run_json(short_script())
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("length", [issue["code"] for issue in report["errors"]])

    def test_json_shape(self) -> None:
        result, report = self.run_json(full_script())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(
            set(report),
            {
                "passed",
                "path",
                "platform",
                "short",
                "title",
                "metrics",
                "errors",
                "warnings",
            },
        )
        self.assertIsNone(report["title"])
        self.assertEqual(
            set(report["metrics"]),
            {
                "han",
                "estimated_seconds",
                "estimated_minutes",
                "sentences",
                "avg_sentence_han",
                "longest_sentence_han",
                "paragraphs",
            },
        )
        if report["errors"]:
            self.assertEqual(
                set(report["errors"][0]),
                {"code", "line", "message", "excerpt"},
            )

    def test_master_title_up_to_eight_characters_passes(self) -> None:
        result, report = self.run_json(
            full_script(), "--title", "AI替你规划路线"
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(report["passed"])
        self.assertEqual(report["title"]["characters"], 8)
        self.assertEqual(report["title"]["limit"], 8)
        self.assertNotIn(
            "title_length",
            [issue["code"] for issue in report["title"]["errors"]],
        )

    def test_master_title_over_eight_characters_fails(self) -> None:
        result, report = self.run_json(
            full_script(), "--title", "AI替你规划新路线"
        )
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertFalse(report["passed"])
        self.assertEqual(report["title"]["characters"], 9)
        self.assertIn(
            "title_length",
            [issue["code"] for issue in report["title"]["errors"]],
        )
        length_error = next(
            issue
            for issue in report["title"]["errors"]
            if issue["code"] == "title_length"
        )
        self.assertIn("标点计入，空格不计", length_error["message"])

    def test_title_spaces_do_not_count_but_punctuation_does(self) -> None:
        spaced = "AI 替 你 规 划 路 线"
        result, report = self.run_json(full_script(), "--title", spaced)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(report["title"]["characters"], 8)

        with_punctuation = "AI，替你规划路线"
        result, report = self.run_json(
            full_script(), "--title", with_punctuation
        )
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(report["title"]["characters"], 9)
        self.assertIn(
            "title_length",
            [issue["code"] for issue in report["title"]["errors"]],
        )

    def test_douyin_six_characters_pass_and_seven_fail(self) -> None:
        result, report = self.run_json(
            full_script(),
            "--platform",
            "douyin",
            "--title",
            "AI替你规划",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(report["title"]["limit"], 6)
        self.assertNotIn(
            "title_length",
            [issue["code"] for issue in report["title"]["errors"]],
        )

        result, report = self.run_json(
            full_script(),
            "--platform",
            "douyin",
            "--title",
            "AI替你规划路",
        )
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "title_length",
            [issue["code"] for issue in report["title"]["errors"]],
        )

    def test_shipinhao_is_supported_and_limits_title_to_six(self) -> None:
        result, report = self.run_json(
            full_script(),
            "--platform",
            "shipinhao",
            "--title",
            "AI替你规划",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(report["platform"], "shipinhao")
        self.assertEqual(report["title"]["limit"], 6)

        result, report = self.run_json(
            full_script(),
            "--platform",
            "shipinhao",
            "--title",
            "AI替你规划路",
        )
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "title_length",
            [issue["code"] for issue in report["title"]["errors"]],
        )

    def test_clickbait_title_is_hard_error(self) -> None:
        result, report = self.run_json(
            full_script(), "--title", "震惊AI替你上班"
        )
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(report["title"]["characters"], 8)
        self.assertFalse(report["title"]["passed"])
        self.assertIn(
            "title_clickbait",
            [issue["code"] for issue in report["title"]["errors"]],
        )

    def test_vague_title_warns_without_blocking_script(self) -> None:
        result, report = self.run_json(full_script(), "--title", "AI很重要")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(report["passed"])
        self.assertTrue(report["title"]["passed"])
        self.assertIn(
            "title_vague",
            [issue["code"] for issue in report["title"]["warnings"]],
        )

    def test_empty_title_fails(self) -> None:
        result, report = self.run_json(full_script(), "--title", "   ")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertFalse(report["passed"])
        self.assertEqual(report["title"]["characters"], 0)
        self.assertIn(
            "title_empty",
            [issue["code"] for issue in report["title"]["errors"]],
        )

    def test_term_density_is_warning_not_hard_error(self) -> None:
        text = full_script() + (
            "\n\n这段只用来测试大模型、Agent 和工作流这三个词"
            "会不会触发术语密度提醒。"
        )
        result, report = self.run_json(text)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(report["passed"])
        self.assertIn(
            "term_density", [issue["code"] for issue in report["warnings"]]
        )
        self.assertNotIn(
            "term_density", [issue["code"] for issue in report["errors"]]
        )

    def test_light_cues_are_masked(self) -> None:
        base_result, base_report = self.run_json(full_script())
        self.assertEqual(base_result.returncode, 0, base_result.stdout + base_result.stderr)
        with_cues = full_script() + (
            "\n\n[停顿] 第一段后停一下\n"
            "[重音] 强调完整的小事\n"
            "[交给画面] 显示表格和窗口\n"
        )
        result, report = self.run_json(with_cues)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(report["metrics"]["han"], base_report["metrics"]["han"])
        self.assertNotIn("punctuation", [issue["code"] for issue in report["errors"]])

    def test_missing_file_exits_two(self) -> None:
        result = self.run_checker(path=self.root / "missing.md")
        self.assertEqual(result.returncode, 2)

    def test_bad_platform_exits_two(self) -> None:
        result = self.run_checker(full_script(), "--platform", "wechat")
        self.assertEqual(result.returncode, 2)

    def test_no_han_exits_two(self) -> None:
        result = self.run_checker("only latin text here", path=self.write("### title\n\nonly latin text here"))
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
