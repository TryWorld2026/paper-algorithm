#!/usr/bin/env python3
"""Offline tests for scripts/fetch_topics.py."""

from __future__ import annotations

import gzip
import importlib.util
import io
import json
import sys
import tempfile
import unittest
import urllib.error
import urllib.parse
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "fetch_topics.py"
SPEC = importlib.util.spec_from_file_location("fetch_topics", SCRIPT)
assert SPEC and SPEC.loader
fetch_topics_module = importlib.util.module_from_spec(SPEC)
sys.modules["fetch_topics"] = fetch_topics_module
SPEC.loader.exec_module(fetch_topics_module)

FetchError = fetch_topics_module.FetchError


class FakeResponse:
    def __init__(self, body: bytes, headers: dict[str, str] | None = None):
        self._body = body
        self.headers = headers or {}
        self.status = 200

    def read(self) -> bytes:
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False


def v1_payload(items=None):
    return {
        "schemaVersion": 1,
        "query": {"mode": "selected", "window": "7d"},
        "items": items
        if items is not None
        else [
            {
                "id": "abc123",
                "title": "官方发布一个新工具",
                "originalTitle": "A new tool",
                "summary": "官方说明它能把会议记录自动整理成行动项。",
                "source": {"name": "官方博客"},
                "links": {
                    "aihot": "https://aihot.news/items/abc123",
                    "original": "https://example.com/new-tool",
                },
                "publishedAt": "2026-11-14T08:00:00.000Z",
                "discoveredAt": "2026-11-14T09:00:00.000Z",
                "category": "ai-products",
                "score": 88,
                "selected": True,
                "reason": "说明具体能力变化。",
            }
        ],
        "page": {"count": 1, "hasMore": False, "nextCursor": None},
    }


class FetchTopicsTests(unittest.TestCase):
    def test_compact_item_maps_v1_fields(self):
        result = fetch_topics_module.compact_item(v1_payload()["items"][0])
        self.assertEqual(
            set(result),
            {
                "id",
                "title",
                "url",
                "source",
                "published_at",
                "category",
                "summary",
            },
        )
        self.assertEqual(result["url"], "https://example.com/new-tool")
        self.assertEqual(result["source"], "官方博客")
        self.assertEqual(result["published_at"], "2026-11-14T08:00:00.000Z")

    def test_compact_item_is_null_safe(self):
        result = fetch_topics_module.compact_item(
            {"id": "x", "title": None, "links": None, "source": None}
        )
        self.assertIsNone(result["url"])
        self.assertIsNone(result["source"])
        self.assertIsNone(result["published_at"])

    def test_fetch_topics_maps_full_response(self):
        with mock.patch.object(
            fetch_topics_module, "request_json", return_value=v1_payload()
        ):
            result = fetch_topics_module.fetch_topics(days=7, take=100)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "abc123")
        self.assertEqual(result[0]["url"], "https://example.com/new-tool")

    def test_fetch_topics_builds_v1_query_and_clamps_limit(self):
        captured = {}

        def fake_request(url):
            captured["url"] = url
            return v1_payload([])

        result = fetch_topics_module.fetch_topics(
            days=1, take=500, query="  AI 工具  ", request=fake_request
        )
        self.assertEqual(result, [])
        parsed = urllib.parse.urlparse(captured["url"])
        self.assertEqual(parsed.path, "/api/v1/items")
        query = urllib.parse.parse_qs(parsed.query)
        self.assertEqual(query["mode"], ["selected"])
        self.assertEqual(query["window"], ["24h"])
        self.assertEqual(query["limit"], ["100"])
        self.assertEqual(query["q"], ["AI 工具"])

    def test_seven_days_uses_seven_day_window(self):
        captured = {}

        def fake_request(url):
            captured["url"] = url
            return v1_payload([])

        fetch_topics_module.fetch_topics(days=7, take=5, request=fake_request)
        query = urllib.parse.parse_qs(
            urllib.parse.urlparse(captured["url"]).query
        )
        self.assertEqual(query["window"], ["7d"])
        self.assertEqual(query["limit"], ["5"])

    def test_fetch_topics_rejects_invalid_days_and_query(self):
        with self.assertRaises(ValueError):
            fetch_topics_module.fetch_topics(days=8)
        with self.assertRaises(ValueError):
            fetch_topics_module.fetch_topics(query="x")

    def test_request_sends_headers_and_timeout(self):
        captured = {}

        def fake_urlopen(request, timeout):
            captured["request"] = request
            captured["timeout"] = timeout
            return FakeResponse(
                json.dumps(v1_payload()).encode("utf-8"),
                {"Content-Type": "application/json"},
            )

        with mock.patch.object(
            fetch_topics_module.urllib.request, "urlopen", fake_urlopen
        ):
            result = fetch_topics_module.request_json(
                "https://aihot.news/api/v1/items", timeout=17
            )

        self.assertEqual(result["schemaVersion"], 1)
        self.assertEqual(captured["timeout"], 17)
        request = captured["request"]
        self.assertIn("Mozilla/5.0", request.get_header("User-agent"))
        self.assertEqual(request.get_header("Accept"), "application/json")
        self.assertEqual(request.get_header("Accept-encoding"), "gzip")

    def test_request_decompresses_gzip(self):
        body = gzip.compress(json.dumps(v1_payload()).encode("utf-8"))
        response = FakeResponse(body, {"Content-Encoding": "gzip"})
        with mock.patch.object(
            fetch_topics_module.urllib.request, "urlopen", return_value=response
        ):
            result = fetch_topics_module.request_json(
                "https://aihot.news/api/v1/items"
            )
        self.assertEqual(result["items"][0]["id"], "abc123")

    def test_request_saves_etag_and_reuses_cache_on_304(self):
        url = "https://aihot.news/api/v1/items"
        with tempfile.TemporaryDirectory() as directory:
            cache_path = Path(directory) / "http-cache.json"
            cache = fetch_topics_module.HttpCache(cache_path)
            first = FakeResponse(
                json.dumps(v1_payload()).encode("utf-8"),
                {"ETag": '"v1"', "Content-Type": "application/json"},
            )
            with mock.patch.object(
                fetch_topics_module.urllib.request,
                "urlopen",
                return_value=first,
            ) as first_call:
                result = fetch_topics_module.request_json(url, cache=cache)
            self.assertEqual(result["items"][0]["id"], "abc123")
            self.assertIsNone(
                first_call.call_args.args[0].get_header("If-none-match")
            )

            saved = json.loads(cache_path.read_text(encoding="utf-8"))
            self.assertEqual(saved[url]["etag"], '"v1"')
            reloaded = fetch_topics_module.HttpCache(cache_path)
            self.assertEqual(reloaded.get(url)["body"], saved[url]["body"])

            not_modified = urllib.error.HTTPError(
                url,
                304,
                "not modified",
                {"ETag": '"v1"'},
                io.BytesIO(b""),
            )
            with mock.patch.object(
                fetch_topics_module.urllib.request,
                "urlopen",
                side_effect=not_modified,
            ) as cached_call:
                cached_result = fetch_topics_module.request_json(url, cache=cache)
            self.assertEqual(
                cached_call.call_args.args[0].get_header("If-none-match"),
                '"v1"',
            )
            self.assertEqual(cached_result["items"][0]["id"], "abc123")

    def test_http_429_honors_retry_after_and_retries_serially(self):
        error = urllib.error.HTTPError(
            "https://aihot.news/api/v1/items",
            429,
            "rate limited",
            {"Retry-After": "2"},
            io.BytesIO(b"{}"),
        )
        ok = FakeResponse(json.dumps(v1_payload()).encode("utf-8"))
        sleeps = []
        with mock.patch.object(
            fetch_topics_module.urllib.request,
            "urlopen",
            side_effect=[error, ok],
        ) as mocked:
            result = fetch_topics_module.request_json(
                "https://aihot.news/api/v1/items",
                sleep=sleeps.append,
            )
        self.assertEqual(result["schemaVersion"], 1)
        self.assertEqual(sleeps, [2.0])
        self.assertEqual(mocked.call_count, 2)

    def test_http_403_fails_immediately(self):
        error = urllib.error.HTTPError(
            "https://aihot.news/api/v1/items",
            403,
            "forbidden",
            {},
            io.BytesIO(b""),
        )
        with mock.patch.object(
            fetch_topics_module.urllib.request,
            "urlopen",
            side_effect=error,
        ) as mocked:
            with self.assertRaisesRegex(FetchError, "HTTP 403"):
                fetch_topics_module.request_json(
                    "https://aihot.news/api/v1/items",
                    sleep=lambda _: None,
                )
        self.assertEqual(mocked.call_count, 1)

    def test_malformed_json_has_clear_error(self):
        response = FakeResponse(b"<html>nope</html>")
        with mock.patch.object(
            fetch_topics_module.urllib.request, "urlopen", return_value=response
        ):
            with self.assertRaisesRegex(FetchError, "无法解析的 JSON"):
                fetch_topics_module.request_json(
                    "https://aihot.news/api/v1/items"
                )

    def test_missing_items_array_is_clear_error(self):
        with mock.patch.object(
            fetch_topics_module, "request_json", return_value={"schemaVersion": 1}
        ):
            with self.assertRaisesRegex(FetchError, "items"):
                fetch_topics_module.fetch_topics()

    def test_cli_writes_compact_array_to_out(self):
        topics = [fetch_topics_module.compact_item(v1_payload()["items"][0])]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "nested" / "topics.json"
            with mock.patch.object(
                fetch_topics_module, "fetch_topics", return_value=topics
            ):
                status = fetch_topics_module.main(["--out", str(output)])
            self.assertEqual(status, 0)
            saved = json.loads(output.read_text(encoding="utf-8"))
            self.assertIsInstance(saved, list)
            self.assertEqual(saved, topics)

    def test_cli_stdout_is_json_array(self):
        topics = [fetch_topics_module.compact_item(v1_payload()["items"][0])]
        buffer = io.StringIO()
        with mock.patch.object(
            fetch_topics_module, "fetch_topics", return_value=topics
        ), redirect_stdout(buffer):
            status = fetch_topics_module.main([])
        self.assertEqual(status, 0)
        self.assertIsInstance(json.loads(buffer.getvalue()), list)

    def test_cli_network_error_guides_user_to_manual_fallback(self):
        error_buffer = io.StringIO()
        with mock.patch.object(
            fetch_topics_module,
            "fetch_topics",
            side_effect=FetchError("无法连接 AIHOT：timed out"),
        ), redirect_stderr(error_buffer):
            status = fetch_topics_module.main([])
        self.assertEqual(status, 1)
        message = error_buffer.getvalue()
        self.assertIn("AIHOT", message)
        self.assertIn("链接", message)

    def test_cli_day_over_seven_exits_two(self):
        with redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as raised:
                fetch_topics_module.main(["--days", "8"])
        self.assertEqual(raised.exception.code, 2)

    def test_cli_rejects_interval_below_sixty(self):
        with redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as raised:
                fetch_topics_module.main(["--interval", "30"])
        self.assertEqual(raised.exception.code, 2)
        args = fetch_topics_module.build_parser().parse_args(["--interval", "60"])
        self.assertEqual(args.interval, 60)

    def test_watch_prints_only_changed_snapshots(self):
        first = [{"id": "a"}]
        second = [{"id": "b"}]
        args = SimpleNamespace(
            days=7,
            take=100,
            query=None,
            out=None,
            interval=60,
            quiet=False,
        )
        buffer = io.StringIO()
        sleeps = []
        with mock.patch.object(
            fetch_topics_module,
            "fetch_topics",
            side_effect=[first, first, second],
        ), redirect_stdout(buffer), redirect_stderr(io.StringIO()):
            status = fetch_topics_module.run_watch(
                args,
                None,
                sleep=sleeps.append,
                max_iterations=3,
            )
        self.assertEqual(status, 0)
        self.assertEqual(sleeps, [60, 60])
        output = buffer.getvalue()
        self.assertEqual(output.count("["), 2)
        self.assertIn('"a"', output)
        self.assertIn('"b"', output)


if __name__ == "__main__":
    unittest.main()
