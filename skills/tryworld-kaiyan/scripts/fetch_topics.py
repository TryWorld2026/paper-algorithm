#!/usr/bin/env python3
"""Fetch recent selected AIHOT items for the tryworld-kaiyan skill.

Uses the public AIHOT v1 API. This module is intentionally standalone and
depends only on the Python standard library.
"""

from __future__ import annotations

import argparse
import email.utils
import gzip
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


BASE_URL = "https://aihot.news"
ITEMS_PATH = "/api/v1/items"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/130.0.0.0 Safari/537.36"
)
DEFAULT_TIMEOUT = 20
DEFAULT_ATTEMPTS = 3
MAX_RETRY_AFTER = 60
MIN_POLL_INTERVAL = 60
DEFAULT_CACHE_PATH = Path(__file__).resolve().parent.parent / "state" / "http-cache.json"


class FetchError(RuntimeError):
    """A user-actionable AIHOT fetch failure."""


def _header_value(headers: Any, name: str) -> str:
    if headers is None:
        return ""
    getter = getattr(headers, "get", None)
    if not callable(getter):
        return ""
    try:
        value = getter(name)
    except Exception:
        return ""
    return str(value).strip() if value is not None else ""


class HttpCache:
    """Small full-URL ETag/body cache stored beside the skill state."""

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
        self.entries[url] = {"etag": etag or "", "body": body}
        try:
            _write_json(self.path, self.entries)
        except OSError:
            pass

    def clear(self) -> None:
        self.entries = {}
        if self.path is not None:
            try:
                self.path.unlink(missing_ok=True)
            except OSError:
                pass


def _retry_after_seconds(headers: Any, default: float) -> float:
    value = headers.get("Retry-After") if headers is not None else None
    if not value:
        return default
    try:
        return min(max(float(str(value).strip()), 0.0), MAX_RETRY_AFTER)
    except (TypeError, ValueError):
        pass
    try:
        parsed = email.utils.parsedate_to_datetime(str(value))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        delta = (parsed - datetime.now(timezone.utc)).total_seconds()
        return min(max(delta, 0.0), MAX_RETRY_AFTER)
    except (TypeError, ValueError, OverflowError):
        return default


def _decode_body(raw: bytes, headers: Any) -> bytes:
    encoding = ""
    if headers is not None:
        encoding = str(headers.get("Content-Encoding", "")).strip().lower()
    if encoding == "gzip":
        try:
            return gzip.decompress(raw)
        except OSError as error:
            raise FetchError(f"AIHOT 返回的 gzip 内容无法解压：{error}") from error
    if encoding == "deflate":
        try:
            return zlib.decompress(raw)
        except zlib.error:
            try:
                return zlib.decompress(raw, -zlib.MAX_WBITS)
            except zlib.error as error:
                raise FetchError(f"AIHOT 返回的 deflate 内容无法解压：{error}") from error
    return raw


def request_json(
    url: str,
    *,
    timeout: int = DEFAULT_TIMEOUT,
    attempts: int = DEFAULT_ATTEMPTS,
    sleep: Callable[[float], None] = time.sleep,
    cache: HttpCache | None = None,
    send_etag: bool = True,
) -> dict[str, Any]:
    """Request one JSON object with gzip, ETag revalidation, and serial retries."""

    if attempts < 1:
        raise ValueError("attempts must be at least 1")

    last_error = "未知错误"
    for attempt in range(1, attempts + 1):
        cached = cache.get(url) if cache is not None else None
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
        }
        if send_etag and cached and cached.get("etag"):
            headers["If-None-Match"] = cached["etag"]
        request = urllib.request.Request(url, headers=headers, method="GET")
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                raw = response.read()
                body = _decode_body(raw, response.headers)
                etag = _header_value(response.headers, "ETag")
            try:
                text = body.decode("utf-8")
                parsed = json.loads(text)
            except (UnicodeDecodeError, json.JSONDecodeError) as error:
                raise FetchError(
                    "AIHOT 返回了无法解析的 JSON。请稍后重试，或直接提供一个选题或链接。"
                ) from error
            if not isinstance(parsed, dict):
                raise FetchError("AIHOT 返回的 JSON 顶层不是对象，接口可能已变化。")
            if cache is not None:
                cache.put(url, etag, text)
            return parsed
        except urllib.error.HTTPError as error:
            status = error.code
            if status == 304:
                if cached and cached.get("body"):
                    try:
                        return json.loads(cached["body"])
                    except json.JSONDecodeError as invalid:
                        raise FetchError(
                            "AIHOT 返回 304，但本地缓存已损坏。请删除缓存后重试。"
                        ) from invalid
                if send_etag and attempt < attempts:
                    send_etag = False
                    continue
                raise FetchError(
                    "AIHOT 返回 304，但本地没有可用的缓存。请删除缓存后重试。"
                ) from error
            if status == 403:
                raise FetchError(
                    "AIHOT 拒绝了这次请求（HTTP 403）。请检查网络、访问规则，"
                    "或直接提供一个选题或链接。"
                ) from error
            if status in (429, 503):
                delay = _retry_after_seconds(
                    error.headers, default=min(2.0 * attempt, 10.0)
                )
                last_error = f"HTTP {status}"
                if attempt < attempts:
                    sleep(delay)
                    continue
                raise FetchError(
                    f"AIHOT 暂时限流或不可用（{last_error}），已重试 {attempt} 次。"
                    "请稍后再试，或直接提供一个选题或链接。"
                ) from error
            if 500 <= status <= 599:
                last_error = f"HTTP {status}"
                if attempt < attempts:
                    sleep(min(2.0 * attempt, 10.0))
                    continue
                raise FetchError(
                    f"AIHOT 服务暂时异常（{last_error}），已重试 {attempt} 次。"
                    "请稍后再试，或直接提供一个选题或链接。"
                ) from error
            raise FetchError(
                f"AIHOT 请求失败（HTTP {status}）。"
                "请稍后再试，或直接提供一个选题或链接。"
            ) from error
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            last_error = str(error)
            if attempt < attempts:
                sleep(min(2.0 * attempt, 10.0))
                continue
            raise FetchError(
                f"无法连接 AIHOT：{last_error}。"
                "请检查网络或代理，也可以直接提供一个选题或链接。"
            ) from error
        except FetchError:
            raise

    raise FetchError(
        f"AIHOT 请求失败：{last_error}。请稍后再试，或直接提供一个选题或链接。"
    )


def _nested(item: dict[str, Any], *keys: str) -> Any:
    value: Any = item
    for key in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def compact_item(item: dict[str, Any]) -> dict[str, Any]:
    """Convert a v1 item into the skill's small, stable data shape."""

    return {
        "id": item.get("id"),
        "title": item.get("title"),
        "url": _nested(item, "links", "original"),
        "source": _nested(item, "source", "name"),
        "published_at": item.get("publishedAt"),
        "category": item.get("category"),
        "summary": item.get("summary"),
    }


def _build_url(days: int, take: int, query: str | None) -> str:
    window = "24h" if days <= 1 else "7d"
    params: dict[str, Any] = {
        "mode": "selected",
        "window": window,
        "limit": take,
    }
    if query:
        params["q"] = query
    return f"{BASE_URL}{ITEMS_PATH}?{urllib.parse.urlencode(params)}"


def fetch_topics(
    days: int = 7,
    take: int = 100,
    query: str | None = None,
    *,
    request: Callable[[str], dict[str, Any]] | None = None,
    cache: HttpCache | None = None,
) -> list[dict[str, Any]]:
    """Fetch and compact recent selected items without ranking them."""

    if days < 1 or days > 7:
        raise ValueError("days must be between 1 and 7")
    if take < 1:
        raise ValueError("take must be at least 1")
    take = min(take, 100)
    query = query.strip() if query else None
    if query is not None and not (2 <= len(query) <= 200):
        raise ValueError("query must contain 2 to 200 characters")

    url = _build_url(days, take, query)
    payload = request(url) if request is not None else request_json(url, cache=cache)
    items = payload.get("items")
    if not isinstance(items, list):
        raise FetchError("AIHOT 响应缺少 items 数组，接口可能已变化。")
    return [compact_item(item) for item in items if isinstance(item, dict)]


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        temporary.write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        os.replace(temporary, path)
    finally:
        try:
            if temporary.exists():
                temporary.unlink()
        except OSError:
            pass


def _output_topics(topics: list[dict[str, Any]], out: str | None) -> None:
    if out and out != "-":
        _write_json(Path(out).expanduser(), topics)
    else:
        print(json.dumps(topics, ensure_ascii=False, indent=2))


def run_watch(
    args: argparse.Namespace,
    cache: HttpCache | None,
    *,
    sleep: Callable[[float], None] = time.sleep,
    max_iterations: int | None = None,
) -> int:
    """Poll at the configured interval and emit only changed snapshots."""

    last_fingerprint: str | None = None
    iterations = 0
    while max_iterations is None or iterations < max_iterations:
        iterations += 1
        try:
            topics = fetch_topics(
                days=args.days,
                take=args.take,
                query=args.query,
                cache=cache,
            )
        except (FetchError, ValueError) as error:
            print(f"抓取失败：{error}", file=sys.stderr)
        else:
            fingerprint = json.dumps(topics, ensure_ascii=False, sort_keys=True)
            if fingerprint != last_fingerprint:
                _output_topics(topics, args.out)
                last_fingerprint = fingerprint
            elif not args.quiet:
                print(f"无变化，{args.interval} 秒后重试。", file=sys.stderr)
        if max_iterations is None or iterations < max_iterations:
            sleep(args.interval)
    return 0


def _positive_int(value: str) -> int:
    try:
        number = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("必须是整数") from error
    if number < 1:
        raise argparse.ArgumentTypeError("必须大于等于 1")
    return number


def _poll_interval(value: str) -> int:
    try:
        number = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("必须是整数") from error
    if number < MIN_POLL_INTERVAL:
        raise argparse.ArgumentTypeError(
            f"必须大于等于 {MIN_POLL_INTERVAL} 秒"
        )
    return number


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="拉取 AIHOT 最近精选条目，输出统一 JSON 数组"
    )
    parser.add_argument(
        "--days",
        type=_positive_int,
        default=7,
        help="时间窗口，1 表示 24 小时，2-7 表示 7 天（默认 7）",
    )
    parser.add_argument(
        "--take",
        type=_positive_int,
        default=100,
        help="最多返回多少条，1-100（默认 100）",
    )
    parser.add_argument("--query", help="可选关键词，长度 2-200")
    parser.add_argument("--out", help="写入指定 JSON 文件；默认输出到标准输出")
    parser.add_argument(
        "--cache",
        type=Path,
        default=DEFAULT_CACHE_PATH,
        help=f"ETag/304 缓存文件（默认：{DEFAULT_CACHE_PATH}）",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="禁用 ETag/304 缓存",
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="持续轮询；只有内容变化时才输出",
    )
    parser.add_argument(
        "--interval",
        type=_poll_interval,
        default=MIN_POLL_INTERVAL,
        help=f"轮询间隔秒数，最小 {MIN_POLL_INTERVAL}（默认 {MIN_POLL_INTERVAL}）",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="watch 模式下不打印无变化提示",
    )
    return parser


def _run_once(args: argparse.Namespace, cache: HttpCache | None) -> int:
    try:
        topics = fetch_topics(
            days=args.days,
            take=args.take,
            query=args.query,
            cache=cache,
        )
    except (FetchError, ValueError) as error:
        print(f"抓取失败：{error}", file=sys.stderr)
        print(
            "你仍然可以直接给我一个选题、链接或素材，我继续写稿。",
            file=sys.stderr,
        )
        return 1

    if args.out and args.out != "-":
        try:
            _write_json(Path(args.out).expanduser(), topics)
        except OSError as error:
            print(f"写入失败：{error}", file=sys.stderr)
            return 1
        return 0

    print(json.dumps(topics, ensure_ascii=False, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.days > 7:
        parser.error("--days 最大为 7")
    if args.query is not None and not (2 <= len(args.query.strip()) <= 200):
        parser.error("--query 长度必须在 2 到 200 个字符之间")

    cache = None if args.no_cache else HttpCache(Path(args.cache).expanduser())
    try:
        if args.watch:
            return run_watch(args, cache)
        return _run_once(args, cache)
    except KeyboardInterrupt:
        print("已停止轮询。", file=sys.stderr)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
