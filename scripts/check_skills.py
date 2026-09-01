#!/usr/bin/env python3
"""Run the repository-local static gates for TryWorld skills."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_check(label: str, cmd: list[str]) -> bool:
    print(f"[RUN] {label}")
    result = subprocess.run(
        cmd,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    output = result.stdout.strip()
    errors = result.stderr.strip()
    if output:
        print(output)
    if errors:
        print(errors, file=sys.stderr)
    status = "OK" if result.returncode == 0 else "FAIL"
    print(f"[{status}] {label}")
    return result.returncode == 0


def main() -> int:
    failures: list[str] = []

    python_scripts = sorted(ROOT.glob("skills/**/scripts/*.py"))
    if not python_scripts:
        print("No Python skill scripts found.", file=sys.stderr)
        return 1
    if not run_check(
        "compile skill scripts",
        [sys.executable, "-m", "py_compile", *[str(path) for path in python_scripts]],
    ):
        failures.append("compile skill scripts")

    prose_checker = ROOT / "skills/tryworld-paper/scripts/check_prose.py"
    prose_files = sorted(
        path
        for path in (*ROOT.glob("examples/**/*.md"), *ROOT.glob("examples/**/titles.txt"))
        if path.name != "README.md"
    )
    for path in prose_files:
        label = f"prose gate {path.relative_to(ROOT).as_posix()}"
        if not run_check(label, [sys.executable, "-X", "utf8", str(prose_checker), str(path)]):
            failures.append(label)

    if failures:
        print("\nChecks failed:")
        for item in failures:
            print(f"- {item}")
        return 1

    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())