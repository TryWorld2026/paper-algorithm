#!/usr/bin/env python3
"""Step 05: Render video. Requires hyperframes CLI."""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Step 05: Render")
    parser.add_argument("--project-dir", type=Path, default=Path.cwd())
    parser.add_argument("--quality", choices=["draft", "high"], default="high")
    args = parser.parse_args()

    confirmed = args.project_dir / "work" / ".confirmed"
    if not confirmed.exists():
        print("FAIL: draft not confirmed.")
        return 1

    audio_dir = args.project_dir / "work" / "audio"
    if not audio_dir.exists() or not (audio_dir / "narration.mp3").exists():
        print("FAIL: narration.mp3 not found. Run step_04_tts.py first.")
        return 1

    npx = shutil.which("npx")
    if not npx:
        print("FAIL: npx not found. Install Node.js >= 22.")
        return 1

    # Check hyperframes availability (with timeout and error handling)
    try:
        hf_check = subprocess.run(
            [npx, "--no-install", "hyperframes", "--version"],
            capture_output=True, text=True, timeout=15,
        )
        hf_available = hf_check.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        hf_available = False

    if not hf_available:
        print("WARNING: hyperframes CLI not available or timed out.")
        print("Fallback: audio + captions only (no video rendering).")
        print("Output files in work/audio/ are still valid for manual assembly.")
        return 0  # Non-blocking: audio is still usable, but no video

    print(f"Rendering with hyperframes ({args.quality})...")
    out_dir = args.project_dir / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    output = out_dir / "main.mp4"

    result = subprocess.run(
        [npx, "hyperframes", "render", "--fps", "30", "--quality", args.quality, "--output", str(output)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(args.project_dir),
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    if result.returncode != 0:
        print("RENDER FAILED.")
        return result.returncode

    print(f"Render complete: {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
