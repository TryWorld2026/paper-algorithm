"""Tests for scripts/check_skills.py."""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CHECK = REPO / "scripts" / "check_skills.py"


class TestCheckSkills:
    def test_all_checks_pass(self):
        r = subprocess.run(
            [sys.executable, "-X", "utf8", str(CHECK)],
            capture_output=True, text=True, encoding="utf-8", errors="replace", env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"},
        )
        assert r.returncode == 0, f"check_skills failed:\n{r.stdout}\n{r.stderr}"
        assert "All checks passed" in r.stdout

    def test_compiles_all_skill_scripts(self):
        source = CHECK.read_text(encoding="utf-8")
        assert "py_compile" in source
        assert "skills/**/scripts/*.py" in source
