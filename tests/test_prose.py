"""Tests for check_prose.py."""
import importlib.util
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CHECKER = REPO / "skills" / "tryworld-paper" / "scripts" / "check_prose.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def run_checker(path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-X", "utf8", str(CHECKER), str(path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace", env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"},
    )


class TestCleanText:
    def test_clean_prose_passes(self):
        r = run_checker(FIXTURES / "clean_prose.md")
        assert r.returncode == 0, f"clean text should pass:\n{r.stdout}\n{r.stderr}"

    def test_valid_titles_pass(self):
        r = run_checker(FIXTURES / "valid_titles.txt")
        assert r.returncode == 0


class TestForbiddenPunctuation:
    def test_chinese_colon_fails(self):
        r = run_checker(FIXTURES / "bad_colon.md")
        assert r.returncode == 1
        assert "中文冒号" in r.stdout

    def test_dash_fails(self):
        r = run_checker(FIXTURES / "bad_dash.md")
        assert r.returncode == 1
        assert "破折号" in r.stdout


class TestForbiddenWords:
    def test_jargon_fails(self):
        r = run_checker(FIXTURES / "bad_jargon.md")
        assert r.returncode == 1
        assert "黑话" in r.stdout

    def test_hard_stop_fails(self):
        r = run_checker(FIXTURES / "bad_stop.md")
        assert r.returncode == 1
        assert "硬停词" in r.stdout


class TestEdgeCases:
    def test_empty_file_fails(self):
        r = run_checker(FIXTURES / "bad_colon.md")  # use as proxy
        assert r.returncode in (0, 1, 2)

    def test_checker_help(self):
        r = subprocess.run(
            [sys.executable, "-X", "utf8", str(CHECKER), "--help"],
            capture_output=True, text=True,
            encoding="utf-8", errors="replace",
        )
        assert r.returncode == 0
        assert r.returncode == 0


class TestTechnicalNotationExemption:
    """16:9 / 4:3 / 12:30 / 2024–2026 are unavoidable notation for this genre."""

    def _run(self, tmp_path, text):
        f = tmp_path / "t.md"
        f.write_text(text, encoding="utf-8")
        return run_checker(f)

    def test_aspect_ratios_and_times_pass(self, tmp_path):
        r = self._run(tmp_path, "视频做成 16:9 横版，封面用 4:3 和 3:4。\n发布时间 12:30 与 19:30。\n")
        assert r.returncode == 0, f"technical notation must not block:\n{r.stdout}\n{r.stderr}"
        assert "技术记法标点" in r.stdout  # exempted, but visible as a warning

    def test_numeric_range_en_dash_passes(self, tmp_path):
        r = self._run(tmp_path, "数据覆盖 2024–2026 三年，样本共一千二百条，来源为公开年报。\n")
        assert r.returncode == 0, f"2024–2026 must not block:\n{r.stdout}"

    def test_prose_colon_still_fails(self, tmp_path):
        r = self._run(tmp_path, "请注意以下三点：第一带身份证，第二提前到。\n")
        assert r.returncode == 1
        assert "中文冒号" in r.stdout

    def test_em_dash_still_fails(self, tmp_path):
        r = self._run(tmp_path, "价格降了一半——这个降幅很少见。\n")
        assert r.returncode == 1
        assert "破折号" in r.stdout

    def test_en_dash_between_words_still_fails(self, tmp_path):
        # exemption is only digit–digit; a word-adjacent en dash is still a dash
        r = self._run(tmp_path, "上游生态–下游应用的联动被反复提及。\n")
        assert r.returncode == 1

    def test_time_with_space_not_exempt(self, tmp_path):
        # "12 :30" is not the tight digit:digit form — must stay blocked
        r = self._run(tmp_path, "钟点写作 12 :30 这种带空格的格式应被拦。\n")
        assert r.returncode == 1

    def test_fixture_valid_titles_still_pass(self):
        r = run_checker(FIXTURES / "valid_titles.txt")
        assert r.returncode == 0


class TestWhitelistOverride:
    def test_whitelist_exempts_and_is_visible(self, tmp_path):
        draft = tmp_path / "d.md"
        draft.write_text("这里有一个冒号：请豁免它。\n", encoding="utf-8")
        assert run_checker(draft).returncode == 1

        wl = tmp_path / "wl.txt"
        wl.write_text("：\n", encoding="utf-8")
        r = subprocess.run(
            [sys.executable, "-X", "utf8", str(CHECKER), str(draft), "--whitelist", str(wl)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        assert r.returncode == 0, r.stdout
        # invalid regex must not crash the gate
        wl.write_text("[unclosed\n", encoding="utf-8")
        r2 = subprocess.run(
            [sys.executable, "-X", "utf8", str(CHECKER), str(draft), "--whitelist", str(wl)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        assert "WARNING" in r2.stderr + r2.stdout
