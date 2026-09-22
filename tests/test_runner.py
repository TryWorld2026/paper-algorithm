"""End-to-end tests for pipeline/runner.py (offline: steps 01-03 only).

Steps 04-06 need edge-tts / ffmpeg / hyperframes, so their forwarding is
covered indirectly via --dry-run assertions and marker-freshness failures
(which happen before any external tool is invoked).
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
CLEAN_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "clean_prose.md"


def run_runner(project_dir: Path, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-X", "utf8", "-m", "pipeline.runner",
         "--project-dir", str(project_dir), *extra],
        cwd=REPO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def prepare_steps_1_2(project_dir: Path) -> subprocess.CompletedProcess:
    return run_runner(project_dir, "--steps", "1,2", "--script", str(CLEAN_FIXTURE))


def prepare_confirmed_project(project_dir: Path) -> None:
    r = prepare_steps_1_2(project_dir)
    assert r.returncode == 0, f"steps 1,2 failed:\n{r.stdout}\n{r.stderr}"
    r = run_runner(project_dir, "--steps", "3", "--confirm")
    assert r.returncode == 0, f"step 3 --confirm failed:\n{r.stdout}\n{r.stderr}"


class TestDryRun:
    def test_dry_run_lists_steps_and_forwarded_args(self, tmp_path):
        r = run_runner(tmp_path, "--dry-run", "--script", "x.md", "--confirm", "--quality", "draft")
        assert r.returncode == 0
        out = r.stdout
        for name in ("optimize", "check_prose", "confirm", "tts", "render", "verify"):
            assert name in out
        # forwarded args appear on the right steps only
        assert "--script" in out and "x.md" in out
        assert "--confirm" in out
        assert "--quality" in out and "draft" in out
        assert str(tmp_path) in out

    def test_dry_run_does_not_write_state_or_dirs(self, tmp_path):
        r = run_runner(tmp_path, "--dry-run", "--steps", "1", "--script", "x.md")
        assert r.returncode == 0
        assert not (tmp_path / "work").exists()


class TestStepSelection:
    def test_step1_requires_script(self, tmp_path):
        r = run_runner(tmp_path, "--steps", "1")
        assert r.returncode != 0
        assert "--script" in (r.stdout + r.stderr)

    def test_invalid_step_selection_rejected(self, tmp_path):
        for selection in ("999", "abc", "1,abc"):
            r = run_runner(tmp_path, "--steps", selection)
            assert r.returncode != 0
            assert "step" in (r.stdout + r.stderr).lower()

    def test_step_selection_tolerates_spaces_and_trailing_comma(self, tmp_path):
        r = run_runner(tmp_path, "--dry-run", "--steps", " 1 , 2 ,", "--script", "x.md")
        assert r.returncode == 0
        assert "optimize" in r.stdout and "check_prose" in r.stdout
        assert "tts" not in r.stdout.split("Skipped:")[0]

    def test_out_of_order_selection_runs_in_pipeline_order(self, tmp_path):
        r = run_runner(tmp_path, "--dry-run", "--steps", "2,1", "--script", "x.md")
        assert r.returncode == 0
        body = r.stdout.split("Skipped:")[0]
        assert body.index("optimize") < body.index("check_prose")


class TestCwdIndependence:
    """Steps run with cwd=REPO, so relative user paths must be resolved first."""

    def test_relative_paths_resolve_against_the_callers_cwd(self, tmp_path):
        caller = tmp_path / "caller"
        caller.mkdir()
        (caller / "script.md").write_text(
            CLEAN_FIXTURE.read_text(encoding="utf-8"), encoding="utf-8")

        r = subprocess.run(
            [sys.executable, "-X", "utf8", str(REPO / "pipeline" / "runner.py"),
             "--project-dir", "proj", "--steps", "1,2", "--script", "script.md"],
            cwd=str(caller), capture_output=True, text=True,
            encoding="utf-8", errors="replace",
        )
        assert r.returncode == 0, f"runner failed outside repo root:\n{r.stdout}\n{r.stderr}"

        state_path = caller / "proj" / "work" / "pipeline_run.json"
        assert state_path.exists()
        state = json.loads(state_path.read_text(encoding="utf-8"))
        assert Path(state["projectDir"]) == (caller / "proj").resolve()
        assert (caller / "proj" / "work" / "draft.md").exists()
        # Nothing leaked into the repo root, where the step's cwd points.
        assert not (REPO / "proj").exists()
        assert not (REPO / "script.md").exists()


class TestSteps12:
    def test_steps_1_2_run_and_write_markers(self, tmp_path):
        from pipeline.state import marker_matches_draft

        r = prepare_steps_1_2(tmp_path)
        assert r.returncode == 0, f"steps 1,2 failed:\n{r.stdout}\n{r.stderr}"

        draft = tmp_path / "work" / "draft.md"
        prose_pass = tmp_path / "work" / ".prose_pass"
        assert draft.exists()
        assert draft.read_text(encoding="utf-8") == CLEAN_FIXTURE.read_text(encoding="utf-8")
        assert prose_pass.exists()
        assert marker_matches_draft(prose_pass, draft)

    def test_run_state_file_records_steps(self, tmp_path):
        r = prepare_steps_1_2(tmp_path)
        assert r.returncode == 0
        state_path = tmp_path / "work" / "pipeline_run.json"
        assert state_path.exists()
        state = json.loads(state_path.read_text(encoding="utf-8"))
        assert state["projectDir"] == str(tmp_path.resolve())
        assert [s["step"] for s in state["steps"]] == [1, 2]
        assert all(s["status"] == "ok" for s in state["steps"])
        assert state["steps"][0]["args"].get("--script")


class TestConfirmationGate:
    def test_step3_blocks_without_confirm_and_passes_with(self, tmp_path):
        from pipeline.state import marker_matches_draft

        prepare_steps_1_2(tmp_path)
        draft = tmp_path / "work" / "draft.md"
        confirmed = tmp_path / "work" / ".confirmed"

        r = run_runner(tmp_path, "--steps", "3")
        assert r.returncode != 0
        assert "confirm" in (r.stdout + r.stderr).lower()
        assert not confirmed.exists()

        r = run_runner(tmp_path, "--steps", "3", "--confirm")
        assert r.returncode == 0, f"step 3 --confirm failed:\n{r.stdout}\n{r.stderr}"
        assert confirmed.exists()
        assert marker_matches_draft(confirmed, draft)

    def test_stale_confirmation_blocks_downstream(self, tmp_path):
        prepare_confirmed_project(tmp_path)
        draft = tmp_path / "work" / "draft.md"
        draft.write_text(draft.read_text(encoding="utf-8") + "\n新增一句未经确认的修改。\n", encoding="utf-8")

        # Step 04 fails on the stale-confirmation check before touching edge-tts.
        r = run_runner(tmp_path, "--steps", "4")
        assert r.returncode != 0
        combined = r.stdout + r.stderr
        assert "stale" in combined.lower() or "确认" in combined

        # Same via the documented multi-step continuation.
        r = run_runner(tmp_path, "--steps", "3,4", "--confirm")
        assert r.returncode != 0
        assert "stale" in (r.stdout + r.stderr).lower() or "确认" in (r.stdout + r.stderr)


class TestList:
    def test_list_shows_forwardable_args(self, tmp_path):
        r = run_runner(tmp_path, "--list")
        assert r.returncode == 0
        assert "forwards:" in r.stdout
        assert "--script" in r.stdout
        assert "--confirm" in r.stdout
