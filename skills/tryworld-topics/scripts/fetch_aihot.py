#!/usr/bin/env python3
"""Fetch AIHOT v1 data and build a UTF-8 topic-material report."""
from __future__ import annotations

import argparse
import gzip
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

BASE = "https://aihot.news"
UA = "Mozilla/5.0 (compatible; paper-algorithm/1.1)"
SCHEMA_VERSION = 1
STATE_VERSION = 1
MIN_POLL_INTERVAL = 60
SNAPSHOT_PAGE_SIZE = 500
CHANGES_PAGE_SIZE = 100


def _header_value(response: Any, name: str) -> str | None:
    """Read a response header from urllib's HTTPMessage or a test double."""
    headers = getattr(response, "headers", None)
    if headers is None:
        return None
    for attr in ("get", "getheader"):
        getter = getattr(headers, attr, None)
        if not callable(getter):
            continue
        try:
            value = getter(name)
        except Exception:
            continue
        if isinstance(value, str):
            return value
    return None


def _decode_response_body(response: Any) -> str:
    """Read a response body and decompress gzip payloads."""
    raw = response.read()
    if not isinstance(raw, (bytes, bytearray)):
        raw = bytes(raw)
    encoding = (_header_value(response, "Content-Encoding") or "").lower()
    if "gzip" in encoding or raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return raw.decode("utf-8-sig")


def _retry_wait(value: str | None, attempt: int) -> float:
    """Parse Retry-After, falling back to a small serial backoff."""
    fallback = float(attempt * 2)
    if not value:
        return fallback
    try:
        return max(0.0, min(float(value), 300.0))
    except ValueError:
        pass
    try:
        retry_at = parsedate_to_datetime(value)
        now = time.time()
        return max(0.0, min(retry_at.timestamp() - now, 300.0))
    except (TypeError, ValueError, OverflowError):
        return fallback


class HttpCache:
    """Small full-URL ETag/body cache stored beside the fetched output."""

    def __init__(self, path: Path | None):
        self.path = path
        self.entries: dict[str, dict[str, str]] = {}
        self._load()

    def _load(self) -> None:
        if self.path is None or not self.path.exists():
            return
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        if isinstance(raw, dict) and isinstance(raw.get("entries"), dict):
            raw = raw["entries"]
        if not isinstance(raw, dict):
            return
        for url, entry in raw.items():
            if not isinstance(url, str) or not isinstance(entry, dict):
                continue
            body = entry.get("body")
            etag = entry.get("etag", "")
            if isinstance(body, str):
                self.entries[url] = {
                    "etag": etag if isinstance(etag, str) else "",
                    "body": body,
                }

    def get(self, url: str) -> dict[str, str] | None:
        entry = self.entries.get(url)
        return entry if isinstance(entry, dict) else None

    def put(self, url: str, etag: str, body: str) -> None:
        if self.path is None:
            return
        self.entries[url] = {"etag": etag, "body": body}
        self.save()

    def save(self) -> None:
        if self.path is None:
            return
        _write_json(self.path, self.entries)

    def clear(self) -> None:
        self.entries = {}
        if self.path is not None:
            try:
                self.path.unlink(missing_ok=True)
            except OSError:
                pass


def _write_json(path: Path, payload: Any) -> None:
    """Write JSON atomically so a crash cannot leave a half-written mirror."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    os.replace(tmp, path)


def fetch_json(
    url: str,
    retries: int = 3,
    *,
    cache: HttpCache | None = None,
    send_etag: bool = True,
) -> dict | list:
    """Fetch JSON with gzip, ETag revalidation, and serial retry."""
    last_err: Exception | None = None
    for attempt in range(1, retries + 1):
        cached = cache.get(url) if cache is not None else None
        headers = {
            "User-Agent": UA,
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
        }
        if send_etag and cached and cached.get("etag"):
            headers["If-None-Match"] = cached["etag"]
        try:
            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request, timeout=30) as response:
                text = _decode_response_body(response)
                payload = json.loads(text)
                if cache is not None:
                    cache.put(url, _header_value(response, "ETag") or "", text)
                return payload
        except urllib.error.HTTPError as error:
            if error.code == 304:
                if cached and cached.get("body"):
                    return json.loads(cached["body"])
                raise
            retryable = error.code in (429, 500, 502, 503, 504)
            if retryable and attempt < retries:
                wait = _retry_wait(_header_value(error, "Retry-After"), attempt)
                print(
                    f"retry in {wait:g}s (HTTP {error.code})...",
                    file=sys.stderr,
                )
                time.sleep(wait)
                last_err = error
                continue
            raise
        except (urllib.error.URLError, json.JSONDecodeError):
            raise
    if last_err is not None:
        raise last_err
    raise RuntimeError("request failed without an exception")


def _normalize_base(base_url: str) -> str:
    return base_url.strip().rstrip("/")


def _endpoint(base_url: str, path: str, params: dict[str, Any] | None = None) -> str:
    url = f"{_normalize_base(base_url)}{path}"
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    return url


def _daily_report(payload: Any) -> dict[str, Any]:
    """Unwrap the v1 DailyResponse envelope, with a read-only compatibility fallback."""
    if not isinstance(payload, dict):
        return {}
    report = payload.get("report")
    if isinstance(report, dict):
        return report
    return payload


def _item_list(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if not isinstance(payload, dict):
        return []
    items = payload.get("items", [])
    if isinstance(items, list):
        return [item for item in items if isinstance(item, dict)]
    return []


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def get_source_name(item: Any) -> str:
    """Read source.name, falling back to legacy source/sourceName fields."""
    if not isinstance(item, dict):
        return ""
    source = item.get("source")
    if isinstance(source, dict):
        name = _text(source.get("name"))
        if name:
            return name
    elif isinstance(source, str):
        name = _text(source)
        if name:
            return name
    for key in ("sourceName", "source_name"):
        name = _text(item.get(key))
        if name:
            return name
    return ""


def get_original_title(item: Any) -> str:
    """Read originalTitle, falling back to the legacy title_en field."""
    if not isinstance(item, dict):
        return ""
    for key in ("originalTitle", "title_en"):
        title = _text(item.get(key))
        if title:
            return title
    return ""


def get_original_link(item: Any) -> str:
    """Read links.original, falling back to the legacy url field."""
    if not isinstance(item, dict):
        return ""
    links = item.get("links")
    if isinstance(links, dict):
        link = _text(links.get("original"))
        if link:
            return link
    return _text(item.get("url"))


def get_aihot_link(item: Any) -> str:
    """Read links.aihot, falling back to the legacy permalink field."""
    if not isinstance(item, dict):
        return ""
    links = item.get("links")
    if isinstance(links, dict):
        link = _text(links.get("aihot"))
        if link:
            return link
    return _text(item.get("permalink"))


def get_published_at(item: Any) -> str:
    if not isinstance(item, dict):
        return ""
    return _text(item.get("publishedAt")) or _text(item.get("published_at"))


def get_discovered_at(item: Any) -> str:
    if not isinstance(item, dict):
        return ""
    return _text(item.get("discoveredAt")) or _text(item.get("discovered_at"))


def _append_links(lines: list[str], item: dict[str, Any], indent: str = "  ") -> None:
    original = get_original_link(item)
    aihot = get_aihot_link(item)
    if original:
        lines.append(f"{indent}original: {original}")
    if aihot:
        lines.append(f"{indent}aihot: {aihot}")


def build_report(
    daily_payload: Any,
    items_payload: Any,
    days: int,
    fetched_at: str | None = None,
) -> str:
    """Build a human-readable report from v1 daily and item responses."""
    daily = _daily_report(daily_payload)
    item_list = _item_list(items_payload)
    window = window_for_days(days)
    stamp = fetched_at or time.strftime("%Y-%m-%d %H:%M")
    lines = [f"AIHOT topic material | fetch time: {stamp}"]
    lines.append(f"time window: {window} | selected items: {len(item_list)}")

    if daily:
        date = _text(daily.get("date"))
        if date:
            lines.append(f"latest daily: {date}")
        lead = daily.get("lead")
        if isinstance(lead, dict):
            lead_title = _text(lead.get("title"))
            lead_paragraph = _text(lead.get("leadParagraph"))
            if lead_title:
                lines.append(f"lead: {lead_title}")
            if lead_paragraph:
                lines.append(f"  {lead_paragraph}")
        sections = daily.get("sections", [])
        if isinstance(sections, list):
            for section in sections:
                if not isinstance(section, dict):
                    continue
                lines.append(f"[{_text(section.get('label'))}]")
                section_items = section.get("items", [])
                if not isinstance(section_items, list):
                    continue
                for item in section_items:
                    if not isinstance(item, dict):
                        continue
                    title = _text(item.get("title"))
                    source = get_source_name(item)
                    lines.append(f"  - {title} | {source}")
                    _append_links(lines, item, indent="    ")
        flashes = daily.get("flashes", [])
        if isinstance(flashes, list):
            for flash in flashes:
                if not isinstance(flash, dict):
                    continue
                title = _text(flash.get("title"))
                source = get_source_name(flash)
                lines.append(f"  flash: {title} | {source}")
                _append_links(lines, flash, indent="    ")

    lines.append("")
    lines.append(f"== selected items ({window}) ==")
    for item in item_list:
        category = _text(item.get("category"))
        title = _text(item.get("title"))
        source = get_source_name(item)
        lines.append(f"[{category}] {title} | {source}")
        original_title = get_original_title(item)
        if original_title:
            lines.append(f"  originalTitle: {original_title}")
        _append_links(lines, item)
        published_at = get_published_at(item)
        if published_at:
            lines.append(f"  publishedAt: {published_at}")
        discovered_at = get_discovered_at(item)
        if discovered_at:
            lines.append(f"  discoveredAt: {discovered_at}")
        score = item.get("score")
        if score is not None:
            lines.append(f"  score: {score}")
        selected = item.get("selected")
        if isinstance(selected, bool):
            lines.append(f"  selected: {selected}")
        summary = _text(item.get("summary"))
        if summary:
            lines.append(f"  summary: {summary}")
        reason = _text(item.get("reason"))
        if reason:
            lines.append(f"  reason: {reason}")

    return "\n".join(lines) + "\n"


def window_for_days(days: int) -> str:
    """Map the legacy --days switch to the only v1 rolling windows."""
    return "24h" if days <= 1 else "7d"


class AihotClient:
    def __init__(self, base_url: str, cache: HttpCache | None, retries: int = 3):
        self.base_url = _normalize_base(base_url)
        self.cache = cache
        self.retries = retries

    def get_json(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        *,
        send_etag: bool = True,
    ) -> dict | list:
        return fetch_json(
            _endpoint(self.base_url, path, params),
            retries=self.retries,
            cache=self.cache,
            send_etag=send_etag,
        )


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _state_is_compatible(state: Any, base_url: str) -> bool:
    if not isinstance(state, dict):
        return False
    if not _text(state.get("cursor")) or not isinstance(state.get("items"), list):
        return False
    version = state.get("schemaVersion", state.get("version"))
    if version != SCHEMA_VERSION:
        return False
    saved_base = _text(state.get("base_url"))
    return (
        bool(saved_base)
        and _normalize_base(saved_base) == _normalize_base(base_url)
    )


def _state_from_snapshot(
    base_url: str,
    as_of: str,
    cursor: str,
    items: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "version": STATE_VERSION,
        "schemaVersion": SCHEMA_VERSION,
        "base_url": _normalize_base(base_url),
        "asOf": as_of,
        "cursor": cursor,
        "count": len(items),
        "items": items,
    }


def sync_snapshot(
    client: AihotClient,
    state_path: Path,
) -> dict[str, Any]:
    """Fetch every snapshot page, keeping the first page's sync cursor."""
    page: str | None = None
    first: dict[str, Any] | None = None
    items_by_id: dict[str, dict[str, Any]] = {}
    while True:
        params: dict[str, Any] = {"limit": SNAPSHOT_PAGE_SIZE}
        if page:
            params["page"] = page
        payload = client.get_json(
            "/api/v1/selected/snapshot",
            params,
            send_etag=page is not None,
        )
        if not isinstance(payload, dict):
            raise RuntimeError("unexpected selected snapshot response")
        if first is None:
            first = payload
            if not _text(payload.get("cursor")):
                raise RuntimeError("selected snapshot did not return a cursor")
        page_items = payload.get("items", [])
        if not isinstance(page_items, list):
            raise RuntimeError("selected snapshot items is not a list")
        for item in page_items:
            if not isinstance(item, dict):
                continue
            item_id = _text(item.get("id"))
            if item_id:
                items_by_id[item_id] = item
        if not payload.get("hasMore"):
            break
        next_page = _text(payload.get("nextPage"))
        if not next_page:
            raise RuntimeError("selected snapshot hasMore without nextPage")
        page = next_page

    assert first is not None
    state = _state_from_snapshot(
        client.base_url,
        _text(first.get("asOf")),
        _text(first.get("cursor")),
        list(items_by_id.values()),
    )
    _write_json(state_path, state)
    return state


def _apply_changes(
    items_by_id: dict[str, dict[str, Any]],
    changes: Any,
) -> None:
    if not isinstance(changes, list):
        return
    for change in changes:
        if not isinstance(change, dict):
            continue
        op = _text(change.get("op"))
        if op == "remove":
            item_id = _text(change.get("id"))
            if item_id:
                items_by_id.pop(item_id, None)
        elif op == "upsert":
            item = change.get("item")
            if not isinstance(item, dict):
                continue
            item_id = _text(item.get("id"))
            if item_id:
                items_by_id[item_id] = item


def sync_changes(
    client: AihotClient,
    state: dict[str, Any],
    state_path: Path,
) -> dict[str, Any]:
    """Apply selected/changes pages and persist each applied page."""
    cursor = _text(state.get("cursor"))
    items_by_id = {
        _text(item.get("id")): item
        for item in state.get("items", [])
        if isinstance(item, dict) and _text(item.get("id"))
    }
    while True:
        payload = client.get_json(
            "/api/v1/selected/changes",
            {"cursor": cursor, "limit": CHANGES_PAGE_SIZE},
        )
        if not isinstance(payload, dict):
            raise RuntimeError("unexpected selected changes response")
        _apply_changes(items_by_id, payload.get("changes", []))
        next_cursor = _text(payload.get("cursor")) or cursor
        state = {
            **state,
            "version": STATE_VERSION,
            "schemaVersion": SCHEMA_VERSION,
            "base_url": _normalize_base(client.base_url),
            "cursor": next_cursor,
            "count": len(items_by_id),
            "items": list(items_by_id.values()),
        }
        _write_json(state_path, state)
        cursor = next_cursor
        if not payload.get("hasMore"):
            return state


def sync_selected(
    client: AihotClient,
    state_path: Path,
    *,
    rebaseline: bool = False,
) -> dict[str, Any]:
    """Keep the complete selected mirror current via snapshot + changes."""
    if rebaseline:
        try:
            state_path.unlink(missing_ok=True)
        except OSError:
            pass
    state = _load_json(state_path)
    if _state_is_compatible(state, client.base_url):
        try:
            return sync_changes(client, state, state_path)
        except urllib.error.HTTPError as error:
            if error.code != 409:
                raise
            print(
                "selected cursor requires a new snapshot (409 snapshot_required); "
                "re-baselining...",
                file=sys.stderr,
            )
    return sync_snapshot(client, state_path)


def fetch_default(
    client: AihotClient,
    out: Path,
    days: int,
    limit: int,
) -> int:
    """Fetch the latest daily plus the recent rolling window, then write a report."""
    daily_payload = None
    try:
        daily_payload = client.get_json("/api/v1/dailies/latest")
    except Exception as error:
        print(f"warning: daily fetch failed: {error}", file=sys.stderr)

    items_payload = None
    try:
        items_payload = client.get_json(
            "/api/v1/items",
            {
                "mode": "selected",
                "window": window_for_days(days),
                "limit": limit,
            },
        )
    except Exception as error:
        print(f"warning: items fetch failed: {error}", file=sys.stderr)

    if daily_payload is not None:
        _write_json(out / "daily.json", daily_payload)
    if items_payload is not None:
        _write_json(out / "items.json", items_payload)

    report = build_report(daily_payload, items_payload, days)
    report_path = out / "report.txt"
    report_path.write_text(report, encoding="utf-8")
    count = len(_item_list(items_payload))
    print(f"done | {report_path} | selected {count} items")
    return 0 if daily_payload is not None or items_payload is not None else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fetch AIHOT v1 topics")
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="compatibility window: <=1 maps to 24h, otherwise 7d (default: 7)",
    )
    parser.add_argument(
        "--limit",
        "--take",
        dest="limit",
        type=int,
        default=100,
        help="items page size, 1-100 (--take is a legacy alias; default: 100)",
    )
    parser.add_argument("--out", type=Path, default=Path("work/aihot"))
    parser.add_argument(
        "--base-url",
        default=BASE,
        help=f"AIHOT-compatible API base URL (default: {BASE})",
    )
    parser.add_argument(
        "--sync-selected",
        action="store_true",
        help="maintain the complete selected mirror via snapshot/changes",
    )
    parser.add_argument(
        "--rebaseline",
        action="store_true",
        help="discard selected.json and http-cache.json before fetching",
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="repeat the selected fetch until interrupted",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=MIN_POLL_INTERVAL,
        help=f"watch interval in seconds (minimum: {MIN_POLL_INTERVAL})",
    )
    return parser


def _run_once(
    client: AihotClient,
    args: argparse.Namespace,
    out: Path,
    state_path: Path,
) -> int:
    if args.sync_selected:
        state = sync_selected(
            client,
            state_path,
            rebaseline=args.rebaseline,
        )
        print(
            f"done | {state_path} | selected mirror {len(state.get('items', []))} items"
        )
        return 0
    return fetch_default(client, out, args.days, args.limit)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.interval < MIN_POLL_INTERVAL:
        parser.error(
            f"--interval must be at least {MIN_POLL_INTERVAL} seconds"
        )
    if args.days < 1:
        parser.error("--days must be at least 1")
    if not 1 <= args.limit <= 100:
        parser.error("--limit/--take must be between 1 and 100")

    base_url = _normalize_base(args.base_url)
    if not base_url:
        parser.error("--base-url cannot be empty")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    state_path = out / "selected.json"
    cache = HttpCache(out / "http-cache.json")
    if args.rebaseline:
        cache.clear()
        try:
            state_path.unlink(missing_ok=True)
        except OSError:
            pass

    client = AihotClient(base_url, cache)
    if not args.watch:
        return _run_once(client, args, out, state_path)

    while True:
        try:
            _run_once(client, args, out, state_path)
        except KeyboardInterrupt:
            print("stopped", file=sys.stderr)
            return 130
        print(f"watch: next fetch in {args.interval}s", file=sys.stderr)
        try:
            time.sleep(args.interval)
        except KeyboardInterrupt:
            print("stopped", file=sys.stderr)
            return 130


if __name__ == "__main__":
    sys.exit(main())
