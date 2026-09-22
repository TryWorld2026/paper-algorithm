#!/usr/bin/env python3
"""Pipeline runner. Executes step scripts in order, stops on first failure.

Usage:
  python -m pipeline.runner --project-dir <dir> [--steps 1,2,3] [--dry-run]
                           [--script <script.md>] [--theme-content <theme.json>]
                           [--confirm] [--quality draft|high] [--video <main.mp4>]

Each step is a Python module in pipeline/steps/ named step_NN_<name>.py, invoked
as `python -m pipeline.steps.step_NN_<name>` (direct script invocation keeps
working; steps keep their own argparse). Per-step arguments are forwarded from
the runner flags through STEP_ARGS below.

Run state is recorded in <project-dir>/work/pipeline_run.json for diagnostics
only — it is never an input to any gate. Gate semantics live in the steps
(marker freshness in pipeline/state.py) and are unchanged by this runner.
"""
import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
STEPS_DIR = Path(__file__).resolve().parent / "steps"

# Arguments each step accepts that the runner can forward. Steps keep their own
# argparse definitions; this table only controls what the runner passes through.
# A flag is forwarded only when the user set it explicitly on the runner CLI
# (or, for --confirm, when the flag is present).
STEP_ARGS: dict[int, list[str]] = {
    1: ["--script", "--theme-content"],
    3: ["--confirm"],
    4: ["--theme-content"],
    5: ["--quality"],
    6: ["--video"],
}


def discover_steps() -> list[tuple[int, str, Path]]:
    """Find all step_NN_*.py scripts sorted by step number."""
    steps = []
    for f in sorted(STEPS_DIR.glob("step_*.py")):
        parts = f.stem.split("_", 2)
        if len(parts) >= 2 and parts[1].isdigit():
            steps.append((int(parts[1]), parts[2] if len(parts) > 2 else "", f))
    steps.sort(key=lambda x: x[0])
    return steps


def forwarded_args(step_num: int, args: argparse.Namespace) -> list[str]:
    """Build the argument list the runner passes to one step.

    Only flags the user set explicitly on the runner command line are
    forwarded; otherwise the step's own defaults apply. --confirm is forwarded
    only when present, so the confirmation gate still blocks by default.
    """
    forwarded: list[str] = []
    for flag in STEP_ARGS.get(step_num, []):
        dest = flag.lstrip("-").replace("-", "_")
        value = getattr(args, dest, None)
        if flag == "--confirm":
            if value:
                forwarded.append(flag)
        elif value is not None:
            forwarded += [flag, str(value)]
    return forwarded


def forwarded_summary(step_num: int, args: argparse.Namespace) -> dict[str, str]:
    """Human/JSON-friendly view of what will be forwarded to a step."""
    summary: dict[str, str] = {}
    for flag in STEP_ARGS.get(step_num, []):
        dest = flag.lstrip("-").replace("-", "_")
        value = getattr(args, dest, None)
        if flag == "--confirm":
            if value:
                summary[flag] = "true"
        elif value is not None:
            summary[flag] = str(value)
    return summary


def run_step(script: Path, project_dir: Path, extra_args: list[str]) -> subprocess.CompletedProcess:
    """Run a single step as a module (repo root on sys.path via cwd)."""
    cmd = [
        sys.executable, "-X", "utf8", "-m", f"pipeline.steps.{script.stem}",
        "--project-dir", str(project_dir),
    ]
    cmd += extra_args
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(REPO))


def write_run_state(state_path: Path, state: dict) -> None:
    """Persist run diagnostics; never blocks the pipeline on failure."""
    try:
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError as exc:
        print(f"warning: cannot write run state {state_path}: {exc}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description="Paper Algorithm pipeline runner")
    parser.add_argument("--project-dir", type=Path, default=Path.cwd())
    parser.add_argument("--steps", default="", help="Comma-separated step numbers to run (default: all)")
    parser.add_argument("--script", type=Path, default=None, help="Input script for step 01 (.md/.txt)")
    parser.add_argument("--theme-content", type=Path, default=None,
                        help="Theme JSON forwarded to step 01 (content theme) / step 04 (brand/visual theme)")
    parser.add_argument("--confirm", action="store_true",
                        help="Forward the confirmation flag to step 03; without it the gate blocks")
    parser.add_argument("--quality", choices=["draft", "high"], default=None,
                        help="Render quality forwarded to step 05 (default: the step's own default, high)")
    parser.add_argument("--video", type=Path, default=None,
                        help="Main video path forwarded to step 06 when outputs/ holds multiple mp4 files")
    parser.add_argument("--dry-run", action="store_true", help="Show steps and forwarded args without running")
    parser.add_argument("--list", action="store_true", help="List available steps")
    args = parser.parse_args()

    steps = discover_steps()
    if not steps:
        print("No step scripts found in pipeline/steps/")
        return 1

    if args.list:
        print("Available steps:")
        for num, name, path in steps:
            forwardable = ", ".join(STEP_ARGS.get(num, [])) or "-"
            print(f"  {num:02d}  {name:30s} {path.name:24s} forwards: {forwardable}")
        return 0

    selected = steps
    if args.steps:
        tokens = [x.strip() for x in args.steps.split(",")]
        if any(not token.isdigit() for token in tokens):
            parser.error("--steps must contain comma-separated step numbers")
        wanted = {int(x) for x in tokens if x}
        selected = [(n, name, p) for n, name, p in steps if n in wanted]
        if not selected:
            parser.error("--steps does not select any available step")

    selected_nums = {num for num, _, _ in selected}

    # Step 01 needs an input script; give a clear error instead of an argparse crash.
    if 1 in selected_nums and not args.script:
        print("FAIL: step 01 requires --script <path to .md/.txt input script>.")
        print("Example: python -m pipeline.runner --project-dir <dir> --steps 1,2 --script script.md")
        return 2

    if args.dry_run:
        print("Steps to run:")
        for num, name, path in selected:
            forwarded = forwarded_summary(num, args)
            suffix = f"  [forwards: {forwarded}]" if forwarded else ""
            print(f"  {num:02d}  {name}{suffix}")
        skipped = [(n, name) for n, name, _ in steps if n not in selected_nums]
        if skipped:
            print("\nSkipped:")
            for num, name in skipped:
                print(f"  {num:02d}  {name}")
        print(f"\nProject dir: {args.project_dir}")
        return 0

    state: dict = {
        "startedAt": datetime.now(timezone.utc).isoformat(),
        "projectDir": str(args.project_dir),
        "steps": [],
    }
    state_path = args.project_dir / "work" / "pipeline_run.json"
    write_run_state(state_path, state)

    print(f"Pipeline runner | project: {args.project_dir}")
    print(f"Steps: {len(selected)}")
    print("=" * 60)

    for num, name, path in selected:
        print(f"\n[{num:02d}] {name}")
        print("-" * 40)
        forwarded = forwarded_args(num, args)
        started = time.monotonic()
        result = run_step(path, args.project_dir, forwarded)
        duration_ms = round((time.monotonic() - started) * 1000)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)

        entry: dict = {
            "step": num,
            "name": name,
            "status": "ok" if result.returncode == 0 else "failed",
            "exitCode": result.returncode,
            "durationMs": duration_ms,
            "args": forwarded_summary(num, args),
        }
        if result.returncode != 0 and num == 3 and not args.confirm:
            entry["status"] = "blocked"
            print("\nConfirmation gate blocked: review the draft, then re-run with --confirm.")
        state["steps"].append(entry)
        write_run_state(state_path, state)

        if result.returncode != 0:
            print(f"\nFAILED at step {num:02d} ({name}), exit code {result.returncode}")
            print("Stopping pipeline.")
            state["result"] = "failed"
            state["finishedAt"] = datetime.now(timezone.utc).isoformat()
            write_run_state(state_path, state)
            return result.returncode
        print(f"[{num:02d}] OK")

    state["result"] = "complete"
    state["finishedAt"] = datetime.now(timezone.utc).isoformat()
    write_run_state(state_path, state)

    print("\n" + "=" * 60)
    print("Pipeline complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
