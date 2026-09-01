#!/usr/bin/env python3
"""Cross-platform environment doctor. Replaces doctor.ps1."""
import importlib
import json
import shutil
import subprocess
import sys

def which(name: str) -> str | None:
    return shutil.which(name)

def check_executable(name: str) -> tuple[bool, str]:
    path = which(name)
    if path:
        return True, f"{name} found in PATH"
    return False, f"{name} not found in PATH"

def check_python() -> tuple[bool, str]:
    return check_executable("python")

def check_node() -> tuple[bool, str]:
    return check_executable("node")

def check_ffmpeg() -> tuple[bool, str]:
    return check_executable("ffmpeg")

def check_ffprobe() -> tuple[bool, str]:
    return check_executable("ffprobe")

def check_edge_tts() -> tuple[bool, str]:
    try:
        importlib.import_module("edge_tts")
        return True, "edge_tts import succeeded"
    except ImportError:
        return False, "run: python -m pip install edge-tts"

def check_hyperframes() -> tuple[bool, str]:
    if not which("npx"):
        return False, "npx not found in PATH"
    try:
        r = subprocess.run(
            ["npx", "--no-install", "hyperframes", "--version"],
            capture_output=True, text=True, timeout=30,
        )
        if r.returncode == 0:
            return True, "hyperframes CLI resolved by npx"
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return False, "run: npx hyperframes, then verify with npx hyperframes doctor"

def check_qq_email() -> tuple[bool, str]:
    import os
    account = os.environ.get("QQ_EMAIL_ACCOUNT", "")
    auth = os.environ.get("QQ_EMAIL_AUTH_CODE", "")
    if account and auth:
        return True, "QQ_EMAIL_ACCOUNT and QQ_EMAIL_AUTH_CODE are configured"
    return False, "configure with setx if delivery email is needed"

CHECKS = [
    ("Python", check_python, False),
    ("Node.js", check_node, False),
    ("FFmpeg", check_ffmpeg, False),
    ("ffprobe", check_ffprobe, False),
    ("edge-tts", check_edge_tts, False),
    ("hyperframes", check_hyperframes, False),
    ("QQ email credentials", check_qq_email, True),
]

def main() -> int:
    json_mode = "--json" in sys.argv
    results = []
    for name, fn, optional in CHECKS:
        ok, detail = fn()
        status = "OK" if ok else ("WARN" if optional else "MISSING")
        results.append({"name": name, "status": status, "detail": detail})

    if json_mode:
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            print(f"[{r['status']:>7}] {r['name']:<24} {r['detail']}")

    missing = [r for r in results if r["status"] == "MISSING"]
    if missing:
        print(f"\n{len(missing)} required component(s) missing.")
        return 1
    print("\nAll required components found.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
