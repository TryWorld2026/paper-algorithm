#!/usr/bin/env python3
"""Step 01: Read script, load content theme, output draft.md for user confirmation."""
import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEFAULT_THEME = REPO / "skills" / "tryworld-paper" / "themes" / "content-default.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Step 01: Optimize script")
    parser.add_argument("--project-dir", type=Path, default=Path.cwd())
    parser.add_argument("--script", type=Path, required=True, help="Path to input script (.md/.txt)")
    parser.add_argument("--theme-content", type=Path, default=None, help="Path to content theme JSON (default: themes/content-default.json)")
    args = parser.parse_args()

    # Load content theme
    content_theme = args.theme_content if args.theme_content else DEFAULT_THEME
    theme = {}
    if content_theme.exists():
        theme = json.loads(content_theme.read_text(encoding="utf-8"))
        domain = theme.get("domain", "AI")
        audience = theme.get("audience", "")
        min_chars, max_chars = theme.get("standard_length_chars", [2500, 2800])
        print(f"Content theme: {content_theme.name}")
        print(f"Domain: {domain}")
        print(f"Audience: {audience}")
        print(f"Target length: {min_chars}-{max_chars} chars")
        print(f"Tone: {theme.get('tone', 'default')}")
    else:
        print(f"WARNING: content theme not found: {content_theme}, using defaults")

    # Read script
    if not args.script.exists():
        print(f"FAIL: script not found: {args.script}")
        return 1

    text = args.script.read_text(encoding="utf-8")
    han_count = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
    print(f"Input script: {args.script.name} ({han_count} hanzi)")

    # For now, pass through. In production, Agent would optimize here.
    work_dir = args.project_dir / "work"
    work_dir.mkdir(parents=True, exist_ok=True)
    draft = work_dir / "draft.md"
    draft.write_text(text, encoding="utf-8")
    print(f"Draft written to: {draft}")

    print("\nACTION REQUIRED: Review draft.md and confirm before proceeding to step 02.")
    print("This step does NOT auto-confirm. User must explicitly approve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
