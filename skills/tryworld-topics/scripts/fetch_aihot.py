#!/usr/bin/env python3
"""AIHOT topic fetcher. Cross-platform replacement for fetch_aihot.ps1."""
import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

BASE = "https://aihot.virxact.com"
UA = "Mozilla/5.0 (compatible; paper-algorithm/1.0)"

def fetch_json(url: str, retries: int = 3) -> dict | list:
    """Fetch JSON with retry on 429/5xx."""
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < retries:
                wait = attempt * 2
                print(f"retry in {wait}s (HTTP {e.code})...", file=sys.stderr)
                time.sleep(wait)
                last_err = e
            else:
                raise
        except (urllib.error.URLError, json.JSONDecodeError) as e:
            raise
    raise last_err  # unreachable but satisfies type checker


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch AIHOT topics")
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--take", type=int, default=100)
    parser.add_argument("--out", type=Path, default=Path("work/aihot"))
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)

    daily = None
    try:
        daily = fetch_json(f"{BASE}/api/public/daily")
    except Exception as e:
        print(f"warning: daily fetch failed: {e}", file=sys.stderr)

    since = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - args.days * 86400))
    items = None
    try:
        items = fetch_json(f"{BASE}/api/public/items?mode=selected&since={since}&take={args.take}")
    except Exception as e:
        print(f"warning: items fetch failed: {e}", file=sys.stderr)

    if daily:
        (args.out / "daily.json").write_text(
            json.dumps(daily, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    if items:
        (args.out / "items.json").write_text(
            json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    # Build report
    lines = [f"AIHOT topic material | fetch time: {time.strftime('%Y-%m-%d %H:%M')}"]
    item_list = []
    if items and isinstance(items, dict):
        item_list = items.get("items", [])
    lines.append(f"time window: last {args.days} days | selected items: {len(item_list)}")

    if daily and isinstance(daily, dict):
        if daily.get("date"):
            lines.append(f"latest daily: {daily['date']}")
        if daily.get("lead"):
            lines.append(f"lead: {daily['lead'].get('title', '')}")
        for sec in daily.get("sections", []):
            lines.append(f"[{sec.get('label', '')}]")
            for it in sec.get("items", []):
                lines.append(f"  - {it.get('title', '')} | {it.get('sourceName', '')}")
        for f in daily.get("flashes", []):
            lines.append(f"  flash: {f.get('title', '')}")

    lines.append("")
    lines.append(f"== selected items (last {args.days} days) ==")
    for it in item_list:
        cat = it.get("category", "")
        title = it.get("title", "")
        source = it.get("source", "")
        lines.append(f"[{cat}] {title} | {source}")

    report = args.out / "report.txt"
    report.write_text("\n".join(lines), encoding="utf-8")
    print(f"done | {report} | selected {len(item_list)} items")
    return 0


if __name__ == "__main__":
    sys.exit(main())
