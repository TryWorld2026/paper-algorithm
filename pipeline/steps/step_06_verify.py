#!/usr/bin/env python3
"""Step 06: Verify delivery (hard gate). Uses existing verify_output.py."""
import argparse
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
VERIFY = REPO / "skills" / "tryworld-paper" / "scripts" / "verify_output.py"


def main() -> int:
    parser = argparse.ArgumentParser(description="Step 06: Verify output")
    parser.add_argument("--project-dir", type=Path, default=Path.cwd())
    parser.add_argument("--video", type=Path, default=None)
    args = parser.parse_args()

    out_dir = args.project_dir / "outputs"
    if not out_dir.exists():
        print("FAIL: outputs/ directory not found.")
        return 1

    cmd = [sys.executable, "-X", "utf8", str(VERIFY), "--dir", str(out_dir)]
    if args.video:
        cmd += ["--video", str(args.video)]

    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    if result.returncode != 0:
        print("\nVERIFY: FAIL. Fix issues before delivery.")
        return 1

    print("\nVERIFY: PASS. Delivery allowed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
