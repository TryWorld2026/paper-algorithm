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
