#!/usr/bin/env python3
"""Step 03: Confirmation gate. This step ALWAYS blocks until user confirms.

Usage: python step_03_confirm.py --project-dir <dir> --confirm
"""
import argparse
import sys
from pathlib import Path

try:
    from pipeline.state import marker_matches_draft, write_marker
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from pipeline.state import marker_matches_draft, write_marker


def main() -> int:
    parser = argparse.ArgumentParser(description="Step 03: User confirmation gate")
    parser.add_argument("--project-dir", type=Path, default=Path.cwd())
    parser.add_argument("--confirm", action="store_true", help="Explicitly confirm draft")
    args = parser.parse_args()

    draft = args.project_dir / "work" / "draft.md"
    if not draft.exists():
        print("FAIL: draft.md not found. Run step_01 and step_02 first.")
        return 1

    prose_pass = args.project_dir / "work" / ".prose_pass"
    if not prose_pass.exists():
        print("FAIL: prose gate has not passed. Run step_02 first.")
        return 1
    if not marker_matches_draft(prose_pass, draft):
        print("FAIL: prose gate is stale for the current draft. Run step_02 first.")
        return 1

    if not args.confirm:
        print("=" * 60)
        print("CONFIRMATION GATE")
        print("=" * 60)
        print(f"Draft: {draft}")
        print("\nRead the draft above. If you approve it, re-run with --confirm")
        print("Without --confirm, this step blocks the pipeline.")
        return 1

    confirmed = args.project_dir / "work" / ".confirmed"
    write_marker(confirmed, draft)
    print("Draft confirmed. Proceeding to next steps.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
