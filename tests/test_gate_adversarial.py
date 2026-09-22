"""Adversarial tests for the pipeline gates: can a run skip user confirmation?

These encode the attacks a careless operator (or an over-eager agent) would try,
so a future refactor cannot quietly turn the confirmation gate into a no-op.

Offline only: every case here fails *before* edge-tts / ffmpeg / hyperframes is
invoked, because the marker checks run first.

Known limitation (by design, not covered here): `.confirmed` / `.prose_pass` are
plain JSON files under `work/` bound to the draft's sha256, so a process running
as the same user can forge them. The gate therefore assumes the *human* really
did confirm outside the agent; it protects against accidents and drift, not
against a determined same-user forgery.
"""
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CLEAN_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "clean_prose.md"


def run_runner(project_dir: Path, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-X", "utf8", "-m", "pipeline.runner",
         "--project-dir", str(project_dir), *extra],
        cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


def fresh_project(tmp_path: Path, name: str) -> Path:
    import shutil
    p = tmp_path / name
    if p.exists():
        shutil.rmtree(p)
    (p / "work").mkdir(parents=True)
    return p


def steps_1_2(project_dir: Path) -> subprocess.CompletedProcess:
    return run_runner(project_dir, "--steps", "1,2", "--script", str(CLEAN_FIXTURE))


class TestGateBypassAttempts:
    def test_step_04_alone_is_blocked(self, tmp_path):
        p = fresh_project(tmp_path, "a")
        r = run_runner(p, "--steps", "4")
        assert r.returncode != 0
        assert "confirm" in (r.stdout + r.stderr).lower()
        assert not (p / "work" / ".confirmed").exists()

    def test_step_05_alone_is_blocked(self, tmp_path):
        p = fresh_project(tmp_path, "b")
        r = run_runner(p, "--steps", "5")
        assert r.returncode != 0
        assert "confirm" in (r.stdout + r.stderr).lower()

    def test_skipping_step_03_with_confirm_still_blocks_step_04(self, tmp_path):
        """--confirm on the runner must not substitute for running step 03."""
        p = fresh_project(tmp_path, "c")
        r = run_runner(p, "--steps", "1,2,4", "--confirm", "--script", str(CLEAN_FIXTURE))
        assert r.returncode != 0
        combined = (r.stdout + r.stderr).lower()
        assert "confirm" in combined
        # steps 1-2 still did their job; only the gate stopped the run
        assert (p / "work" / "draft.md").exists()
        assert (p / "work" / ".prose_pass").exists()
        assert not (p / "work" / ".confirmed").exists()

    def test_step_03_without_a_draft_fails(self, tmp_path):
        p = fresh_project(tmp_path, "d")
        r = run_runner(p, "--steps", "3", "--confirm")
        assert r.returncode != 0
        assert "draft" in (r.stdout + r.stderr).lower()

    def test_step_03_failure_stops_the_run_before_step_04(self, tmp_path):
        p = fresh_project(tmp_path, "e")
        r = run_runner(p, "--steps", "3,4", "--confirm")
        assert r.returncode != 0
        assert "[03]" in r.stdout
        assert "[04]" not in r.stdout

    def test_stale_confirmation_blocks_step_04(self, tmp_path):
        p = fresh_project(tmp_path, "f")
        assert steps_1_2(p).returncode == 0
        assert run_runner(p, "--steps", "3", "--confirm").returncode == 0
        draft = p / "work" / "draft.md"
        draft.write_text(draft.read_text(encoding="utf-8") + "\n未确认的新增内容。\n", encoding="utf-8")

        r = run_runner(p, "--steps", "4")
        assert r.returncode != 0
        assert "stale" in (r.stdout + r.stderr).lower()

    def test_stale_prose_marker_blocks_step_03(self, tmp_path):
        """Editing the draft after the prose gate must force step 02 again."""
        p = fresh_project(tmp_path, "g")
        assert steps_1_2(p).returncode == 0
        draft = p / "work" / "draft.md"
        draft.write_text(draft.read_text(encoding="utf-8") + "\n未过门禁的新增内容。\n", encoding="utf-8")

        r = run_runner(p, "--steps", "3", "--confirm")
        assert r.returncode != 0
        assert "prose" in (r.stdout + r.stderr).lower() or "门禁" in (r.stdout + r.stderr)
        assert not (p / "work" / ".confirmed").exists()

    def test_corrupt_run_state_does_not_affect_any_gate(self, tmp_path):
        p = fresh_project(tmp_path, "h")
        assert steps_1_2(p).returncode == 0
        (p / "work" / "pipeline_run.json").write_text("{ not json", encoding="utf-8")

        r = run_runner(p, "--steps", "3")
        assert r.returncode != 0
        assert "confirm" in (r.stdout + r.stderr).lower()

        r = run_runner(p, "--steps", "3", "--confirm")
        assert r.returncode == 0
        state = json.loads((p / "work" / "pipeline_run.json").read_text(encoding="utf-8"))
        assert state["result"] == "complete"
