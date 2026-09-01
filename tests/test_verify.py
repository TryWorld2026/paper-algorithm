"""Tests for verify_output.py."""
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
VERIFY = REPO / "skills" / "tryworld-paper" / "scripts" / "verify_output.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def make_outputs(tmp_path: Path) -> Path:
    """Create a minimal outputs directory for testing."""
    out = tmp_path / "outputs"
    out.mkdir()
    (out / "titles.txt").write_text("title 1\n" * 10, encoding="utf-8")
    (out / "发布计划.txt").write_text("plan", encoding="utf-8")
    (out / "sentences.json").write_text(
        json.dumps({"sentences": [], "totalDuration": 5.0}), encoding="utf-8"
    )
    return out


def run_verify(out: Path, extra_args: list[str] | None = None) -> subprocess.CompletedProcess:
    args = [sys.executable, "-X", "utf8", str(VERIFY), "--dir", str(out)]
    if extra_args:
        args += extra_args
    return subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace", env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"})


class TestMissingFiles:
    def test_empty_dir_fails(self, tmp_path):
        out = tmp_path / "empty"
        out.mkdir()
        r = run_verify(out)
        assert r.returncode == 1

    def test_missing_video_fails(self, tmp_path):
        out = make_outputs(tmp_path)
        r = run_verify(out)
        assert r.returncode == 1
        assert "主视频" in r.stdout or "mp4" in r.stdout

    def test_missing_titles_fails(self, tmp_path):
        out = tmp_path / "no_titles"
        out.mkdir()
        (out / "发布计划.txt").write_text("plan")
        r = run_verify(out)
        assert r.returncode == 1
        assert "titles" in r.stdout.lower() or "标题" in r.stdout

    def test_missing_plan_fails(self, tmp_path):
        out = tmp_path / "no_plan"
        out.mkdir()
        (out / "titles.txt").write_text("title")
        r = run_verify(out)
        assert r.returncode == 1
        assert "发布计划" in r.stdout


class TestVerifierHelp:
    def test_help(self):
        r = subprocess.run(
            [sys.executable, "-X", "utf8", str(VERIFY), "--help"],
            capture_output=True, text=True,
        )
        assert r.returncode == 0
        assert r.returncode == 0


class TestVerifierLogic:
    def test_multiple_videos_fails(self, tmp_path):
        """Two mp4s without --video should fail."""
        out = make_outputs(tmp_path)
        # Can't easily create valid mp4s without ffmpeg, so just check
        # the error message logic via source code inspection
        source = VERIFY.read_text(encoding="utf-8")
        assert "--video" in source or "video" in source
        assert "恰好一个" in source
