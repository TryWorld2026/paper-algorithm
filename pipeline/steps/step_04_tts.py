#!/usr/bin/env python3
"""Step 04: Synthesize voiceover from confirmed draft."""
import argparse
import subprocess
import sys
from pathlib import Path

try:
    from pipeline.state import marker_matches_draft
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from pipeline.state import marker_matches_draft

REPO = Path(__file__).resolve().parents[2]
TTS = REPO / "skills" / "tryworld-paper" / "scripts" / "tts_yunxi.py"
DEFAULT_THEME = REPO / "skills" / "tryworld-paper" / "themes" / "paper-algorithm.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Step 04: TTS")
    parser.add_argument("--project-dir", type=Path, default=Path.cwd())
    parser.add_argument("--theme-content", type=Path, default=None, help="Path to visual theme JSON (default: paper-algorithm.json)")
    args = parser.parse_args()

    confirmed = args.project_dir / "work" / ".confirmed"
    if not confirmed.exists():
        print("FAIL: draft not confirmed. Run step_03_confirm.py --confirm first.")
        return 1

    draft = args.project_dir / "work" / "draft.md"
    if not marker_matches_draft(confirmed, draft):
        print("FAIL: confirmation is stale for the current draft. Re-run step_03_confirm.py --confirm.")
        return 1
    out_dir = args.project_dir / "work" / "audio"

    cmd = [sys.executable, "-X", "utf8", str(TTS), str(draft), "--out", str(out_dir)]
    theme_file = args.theme_content if args.theme_content else DEFAULT_THEME
    if theme_file.exists():
        cmd += ["--theme", str(theme_file)]

    print(f"Running TTS: {draft.name} -> {out_dir}")
    print(f"Theme: {theme_file.name}")
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    if result.returncode != 0:
        print("TTS FAILED.")
        return result.returncode

    print("TTS complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
