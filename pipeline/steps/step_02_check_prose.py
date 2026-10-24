#!/usr/bin/env python3
"""Step 02: Run check_prose.py on draft.md. Fail if any hard-gate triggers."""
import argparse
import subprocess
import sys
from pathlib import Path

try:
    from pipeline.state import write_marker
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from pipeline.state import write_marker

REPO = Path(__file__).resolve().parents[2]
CHECK_PROSE = REPO / "skills" / "tryworld-paper" / "scripts" / "check_prose.py"


def main() -> int:
    parser = argparse.ArgumentParser(description="Step 02: Prose gate")
    parser.add_argument("--project-dir", type=Path, default=Path.cwd())
    parser.add_argument(
        "--whitelist",
        type=Path,
        default=None,
        help="Optional regex-per-line file exempting literal terms from the gate. "
        "Visible opt-out: the run records it and prints a notice; it is not a silent bypass.",
    )
    args = parser.parse_args()

    draft = args.project_dir / "work" / "draft.md"
    if not draft.exists():
        print(f"FAIL: draft.md not found at {draft}")
        print("Run step_01 first.")
        return 1

    cmd = [sys.executable, "-X", "utf8", str(CHECK_PROSE), str(draft)]
    if args.whitelist:
        if not args.whitelist.is_file():
            print(f"FAIL: whitelist file not found: {args.whitelist}")
            return 1
        cmd += ["--whitelist", str(args.whitelist)]

    result = subprocess.run(
        cmd,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if args.whitelist:
        # Keep the exemption visible: it deletes matched text before analysis,
        # so a run that used it must not look identical to a clean run.
        print(f"NOTE: prose gate ran with a whitelist ({args.whitelist}). "
              "Exempted text was not checked.")

    if result.returncode != 0:
        print("\nPROSE GATE: FAIL. Fix issues in draft.md, then re-run step_02.")
        return 1

    print("\nPROSE GATE: PASS.")
    # Write marker for step_03
    marker = args.project_dir / "work" / ".prose_pass"
    write_marker(marker, draft)
    if args.whitelist:
        print(f"whitelist_used: {args.whitelist}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
