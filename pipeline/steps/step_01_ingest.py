#!/usr/bin/env python3
"""Step 01: Ingest the input script into work/draft.md (verbatim copy).

This step does NOT optimize the script. Optimization (traffic first-principles +
the seven-pass aliveness rewrite + script sanitising) is the agent's job, per
tryworld-koubo / tryworld-paper SKILL.md. The runner is a gate bookkeeper, not a
writer: it copies the input verbatim and binds the approval markers to that
exact content, so a later edit to draft.md invalidates any prior confirmation.
"""
import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEFAULT_THEME = REPO / "skills" / "tryworld-paper" / "themes" / "content-default.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Step 01: Ingest input script to draft.md (no optimization)")
    parser.add_argument("--project-dir", type=Path, default=Path.cwd())
    parser.add_argument("--script", type=Path, required=True, help="Path to input script (.md/.txt)")
    parser.add_argument("--theme-content", type=Path, default=None, help="Path to content theme JSON (default: themes/content-default.json)")
    args = parser.parse_args()

    # Load content theme
    content_theme = args.theme_content if args.theme_content else DEFAULT_THEME
    theme = {}
    if content_theme.exists():
        try:
            theme = json.loads(content_theme.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeError) as e:
            print(f"ERROR: cannot parse content theme JSON: {content_theme}")
            print(f"  Detail: {e}")
            print("  Please check the JSON syntax and fix, then re-run.")
            return 1
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

    # Verbatim ingest. Optimization belongs to the agent (SKILL.md workflow), not
    # to this step — draft.md is the exact text that the prose gate and the user
    # confirmation are bound to.
    work_dir = args.project_dir / "work"
    work_dir.mkdir(parents=True, exist_ok=True)
    draft = work_dir / "draft.md"
    draft.write_text(text, encoding="utf-8")
    # Any new draft invalidates all approvals and prose checks from the old draft.
    for marker_name in (".prose_pass", ".confirmed"):
        (work_dir / marker_name).unlink(missing_ok=True)
    print(f"Draft written to: {draft}")

    print("\nACTION REQUIRED: this is a verbatim copy of the input, NOT an optimized script.")
    print("Per tryworld-koubo / tryworld-paper SKILL.md, the agent must now optimize +")
    print("sanitise the script (traffic first-principles, seven-pass aliveness rewrite),")
    print("overwrite work/draft.md with the optimized text, then run step 02 (prose gate).")
    print("Step 03 blocks until the user confirms; this step does NOT auto-confirm.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
