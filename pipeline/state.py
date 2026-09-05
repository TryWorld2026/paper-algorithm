"""Helpers for binding pipeline gate markers to the exact draft contents."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


def draft_sha256(draft: Path) -> str:
    return hashlib.sha256(draft.read_bytes()).hexdigest()


def write_marker(marker: Path, draft: Path) -> None:
    marker.write_text(
        json.dumps({"draft_sha256": draft_sha256(draft)}, ensure_ascii=False),
        encoding="utf-8",
    )


def marker_matches_draft(marker: Path, draft: Path) -> bool:
    if not marker.is_file() or not draft.is_file():
        return False
    try:
        payload = json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return False
    return payload.get("draft_sha256") == draft_sha256(draft)
