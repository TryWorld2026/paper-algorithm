#!/usr/bin/env python3
"""Step 04: Synthesize voiceover from confirmed draft."""
import argparse
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TTS = REPO / "skills" / "tryworld-paper" / "scripts" / "tts_yunxi.py"
THEME = REPO / "skills" / "tryworld-paper" / "themes" / "paper-algorithm.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Step 04: TTS")
    parser.add_argument("--project-dir", type=Path, default=Path.cwd())
    args = parser.parse_args()

    confirmed = args.project_dir / "work" / ".confirmed"
    if not confirmed.exists():
        print("FAIL: draft not confirmed. Run step_03_confirm.py --confirm first.")
        return 1

    draft = args.project_dir / "work" / "draft.md"
    out_dir = args.project_dir / "work" / "audio"

    cmd = [sys.executable, "-X", "utf8", str(TTS), str(draft), "--out", str(out_dir)]
    if THEME.exists():
        cmd += ["--theme", str(THEME)]

    print(f"Running TTS: {draft.name} -> {out_dir}")
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
