"""Regression tests for pipeline state binding and step selection."""
import json
import importlib.util
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RUNNER = REPO / "pipeline" / "runner.py"


def test_marker_is_bound_to_current_draft(tmp_path):
    from pipeline.state import marker_matches_draft, write_marker

    draft = tmp_path / "draft.md"
    marker = tmp_path / ".confirmed"
    draft.write_text("第一版。", encoding="utf-8")
    write_marker(marker, draft)

    assert marker_matches_draft(marker, draft)
    draft.write_text("第二版。", encoding="utf-8")
    assert not marker_matches_draft(marker, draft)


def test_runner_rejects_empty_or_unknown_step_selection(tmp_path):
    for selection in ("999", "abc"):
        result = subprocess.run(
            [sys.executable, "-m", "pipeline.runner", "--project-dir", str(tmp_path), "--steps", selection],
            cwd=REPO,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        assert result.returncode != 0
        assert "step" in (result.stdout + result.stderr).lower()


def test_marker_has_digest_json(tmp_path):
    from pipeline.state import write_marker

    draft = tmp_path / "draft.md"
    marker = tmp_path / ".prose_pass"
    draft.write_text("稿件。", encoding="utf-8")
    write_marker(marker, draft)

    payload = json.loads(marker.read_text(encoding="utf-8"))
    assert payload["draft_sha256"]


def test_render_requires_current_draft_confirmation(tmp_path):
    from pipeline.state import marker_matches_draft, write_marker

    draft = tmp_path / "draft.md"
    marker = tmp_path / ".confirmed"
    draft.write_text("已确认稿件。", encoding="utf-8")
    write_marker(marker, draft)
    draft.write_text("未经重新确认的修改。", encoding="utf-8")

    assert not marker_matches_draft(marker, draft)


def test_video_path_must_stay_inside_output_dir(tmp_path):
    verify_path = REPO / "skills" / "tryworld-paper" / "scripts" / "verify_output.py"
    spec = importlib.util.spec_from_file_location("verify_output", verify_path)
    verify_output = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(verify_output)

    output_dir = tmp_path / "outputs"
    output_dir.mkdir()
    assert verify_output.is_within_directory(output_dir / "main.mp4", output_dir)
    assert not verify_output.is_within_directory(tmp_path / "outside.mp4", output_dir)
