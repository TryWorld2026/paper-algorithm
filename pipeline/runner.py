#!/usr/bin/env python3
"""Pipeline runner. Executes step scripts in order, stops on first failure.

Usage:
  python -m pipeline.runner --project-dir <dir> [--steps 1,2,3] [--dry-run]

Each step is a Python script in pipeline/steps/ named step_NN_<name>.py.
Steps check their own preconditions and fail fast if prerequisites are missing.
"""
import argparse
import importlib
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
STEPS_DIR = Path(__file__).resolve().parent / "steps"


def discover_steps() -> list[tuple[int, str, Path]]:
    """Find all step_NN_*.py scripts sorted by step number."""
    steps = []
    for f in sorted(STEPS_DIR.glob("step_*.py")):
        parts = f.stem.split("_", 2)
        if len(parts) >= 2 and parts[1].isdigit():
            steps.append((int(parts[1]), parts[2] if len(parts) > 2 else "", f))
    steps.sort(key=lambda x: x[0])
    return steps


def run_step(script: Path, project_dir: Path, extra_args: list[str]) -> subprocess.CompletedProcess:
    """Run a single step script."""
    cmd = [sys.executable, "-X", "utf8", str(script), "--project-dir", str(project_dir)]
    cmd += extra_args
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def main() -> int:
    parser = argparse.ArgumentParser(description="Paper Algorithm pipeline runner")
    parser.add_argument("--project-dir", type=Path, default=Path.cwd())
    parser.add_argument("--steps", default="", help="Comma-separated step numbers to run (default: all)")
    parser.add_argument("--dry-run", action="store_true", help="Show steps without running")
    parser.add_argument("--list", action="store_true", help="List available steps")
    args = parser.parse_args()

    steps = discover_steps()
    if not steps:
        print("No step scripts found in pipeline/steps/")
        return 1

    if args.list:
        print("Available steps:")
        for num, name, path in steps:
            print(f"  {num:02d}  {name:30s} {path.name}")
        return 0

    selected = steps
    if args.steps:
        wanted = {int(x.strip()) for x in args.steps.split(",") if x.strip().isdigit()}
        selected = [(n, name, p) for n, name, p in steps if n in wanted]

    if args.dry_run:
        print("Steps to run:")
        for num, name, path in selected:
            print(f"  {num:02d}  {name}")
        print(f"\nProject dir: {args.project_dir}")
        return 0

    print(f"Pipeline runner | project: {args.project_dir}")
    print(f"Steps: {len(selected)}")
    print("=" * 60)

    for num, name, path in selected:
        print(f"\n[{num:02d}] {name}")
        print("-" * 40)
        result = run_step(path, args.project_dir, [])
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        if result.returncode != 0:
            print(f"\nFAILED at step {num:02d} ({name}), exit code {result.returncode}")
            print("Stopping pipeline.")
            return result.returncode
        print(f"[{num:02d}] OK")

    print("\n" + "=" * 60)
    print("Pipeline complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
