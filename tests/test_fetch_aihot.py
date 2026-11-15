"""Tests for the AIHOT v1 fetcher. No test performs network I/O."""
from __future__ import annotations

import gzip
import importlib.util
import json
import subprocess
import sys
import urllib.error
import urllib.parse
from pathlib import Path
from unittest.mock import MagicMock, patch

REPO = Path(__file__).resolve().parents[1]
FETCH = REPO / "skills" / "tryworld-topics" / "scripts" / "fetch_aihot.py"


def load_module():
    spec = importlib.util.spec_from_file_location("fetch_aihot", str(FETCH))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _ok_response(
    payload: dict | list | None = None,
    *,
    body: bytes | None = None,
    headers: dict[str, str] | None = None,
):
    if body is None:
        body = json.dumps(payload if payload is not None else {"items": []}).encode(
            "utf-8"
        )
    response = MagicMock()
    response.read.return_value = body
    response.headers = headers or {}
    response.__enter__ = lambda self: self
    response.__exit__ = lambda self, *args: None
    return response


def _http_error(code: int, *, retry_after: str | None = None):
    headers = {}
    if retry_after is not None:
        headers["Retry-After"] = retry_after
    return urllib.error.HTTPError(
        "https://aihot.news/api/v1/test",
        code,
        "error",
        headers,
        None,
    )


def _request_headers(request) -> dict[str, str]:
    return {key.lower(): value for key, value in request.header_items()}


class TestImportAndCli:
    def test_imports_without_third_party(self):
        module = load_module()
        assert module.BASE == "https://aihot.news"
        assert callable(module.fetch_json)

    def test_help_exposes_v1_defaults(self):
        result = subprocess.run(
            [sys.executable, "-X", "utf8", str(FETCH), "--help"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        assert result.returncode == 0
        assert "--base-url" in result.stdout
        assert "https://aihot.news" in result.stdout
        assert "--sync-selected" in result.stdout
        assert "--take" in result.stdout

    def test_interval_below_sixty_is_rejected(self):
        result = subprocess.run(
            [
                sys.executable,
                "-X",
                "utf8",
                str(FETCH),
                "--interval",
                "30",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        assert result.returncode != 0
        assert "at least 60" in result.stderr

    def test_interval_sixty_parses(self):
        module = load_module()
        args = module.build_parser().parse_args(["--interval", "60"])
        assert args.interval == 60


class TestFieldMapping:
    def test_v1_fields_reach_report(self):
        module = load_module()
        daily = {
            "schemaVersion": 1,
            "report": {
                "date": "2026-11-15",
                "lead": {
                    "title": "日报头条",
                    "leadParagraph": "日报导语",
                },
                "sections": [
                    {
                        "label": "模型",
                        "items": [
                            {
                                "title": "日报里的模型新闻",
                                "source": {"name": "日报来源"},
                                "links": {
                                    "original": "https://example.com/daily-original",
                                    "aihot": "https://aihot.news/stories/daily",
                                },
                            }
                        ],
                    }
                ],
                "flashes": [
                    {
                        "title": "快讯标题",
                        "source": {"name": "快讯来源"},
                        "links": {"original": "https://example.com/flash"},
                    }
                ],
            },
        }
        items = {
            "items": [
                {
                    "title": "中文标题",
                    "originalTitle": "English title",
                    "source": {"name": "Nested source"},
                    "links": {
                        "original": "https://example.com/original",
                        "aihot": "https://aihot.news/stories/abc",
                    },
                    "publishedAt": "2026-11-15T01:00:00Z",
                    "discoveredAt": "2026-11-15T01:01:00Z",
                    "category": "ai-models",
                    "score": 88,
                    "selected": True,
                    "summary": "摘要",
                    "reason": "推荐理由",
                }
            ]
        }

        report = module.build_report(daily, items, 7)

        assert "lead: 日报头条" in report
        assert "日报里的模型新闻 | 日报来源" in report
        assert "快讯标题 | 快讯来源" in report
        assert "originalTitle: English title" in report
        assert "https://example.com/daily-original" in report
        assert "https://example.com/original" in report
        assert "https://aihot.news/stories/abc" in report
        assert "Nested source" in report
        assert "score: 88" in report
        assert "selected: True" in report
        assert "reason: 推荐理由" in report

    def test_legacy_fields_are_read_only_fallbacks(self):
        module = load_module()
        old = {
            "title": "旧字段文章",
            "title_en": "Legacy English",
            "source": "Legacy source",
            "url": "https://example.com/legacy",
            "permalink": "https://aihot.news/stories/legacy",
        }
        assert module.get_original_title(old) == "Legacy English"
        assert module.get_source_name(old) == "Legacy source"
        assert module.get_original_link(old) == "https://example.com/legacy"
        assert module.get_aihot_link(old) == "https://aihot.news/stories/legacy"


class TestDefaultFetch:
    def test_default_uses_v1_daily_and_windowed_items(self, tmp_path, monkeypatch):
        module = load_module()
        seen: list[str] = []

        def fake_fetch(url, retries=3, **kwargs):
            seen.append(url)
            if "/api/v1/dailies/latest" in url:
                return {"schemaVersion": 1, "report": {"lead": {"title": "今日"}}}
            return {"schemaVersion": 1, "items": []}

        monkeypatch.setattr(module, "fetch_json", fake_fetch)
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "fetch_aihot.py",
                "--base-url",
                "https://mirror.example.com/",
                "--out",
                str(tmp_path / "aihot"),
            ],
        )
        assert module.main() == 0
        assert seen[0] == "https://mirror.example.com/api/v1/dailies/latest"
        assert seen[1].startswith("https://mirror.example.com/api/v1/items?")
        query = urllib.parse.parse_qs(urllib.parse.urlsplit(seen[1]).query)
        assert query["mode"] == ["selected"]
        assert query["window"] == ["7d"]
        assert query["limit"] == ["100"]
        assert (tmp_path / "aihot" / "daily.json").exists()
        assert (tmp_path / "aihot" / "items.json").exists()
        assert "selected" in (tmp_path / "aihot" / "report.txt").read_text(
            encoding="utf-8"
        )

    def test_days_and_take_are_compatibility_aliases(self, tmp_path, monkeypatch):
        module = load_module()
        seen: list[str] = []

        def fake_fetch(url, retries=3, **kwargs):
            seen.append(url)
            return {"schemaVersion": 1, "items": []}

        monkeypatch.setattr(module, "fetch_json", fake_fetch)
        assert (
            module.main(
                [
                    "--days",
                    "1",
                    "--take",
                    "5",
                    "--out",
                    str(tmp_path),
                ]
            )
            == 0
        )
        query = urllib.parse.parse_qs(urllib.parse.urlsplit(seen[-1]).query)
        assert query["window"] == ["24h"]
        assert query["limit"] == ["5"]


class TestHttp:
    def test_gzip_response_is_decompressed(self):
        module = load_module()
        payload = {"schemaVersion": 1, "items": [{"id": "gzip"}]}
        body = gzip.compress(json.dumps(payload).encode("utf-8"))
        response = _ok_response(body=body, headers={"Content-Encoding": "gzip"})
        with patch("urllib.request.urlopen", return_value=response):
            assert module.fetch_json("https://aihot.news/api/v1/items") == payload

    def test_etag_is_sent_and_304_uses_cached_body(self, tmp_path):
        module = load_module()
        cache = module.HttpCache(tmp_path / "http-cache.json")
        payload = {"schemaVersion": 1, "items": [{"id": "cached"}]}
        first = _ok_response(payload, headers={"ETag": '"v1"'})
        second = _http_error(304)
        with patch(
            "urllib.request.urlopen", side_effect=[first, second]
        ) as urlopen:
            assert module.fetch_json(
                "https://aihot.news/api/v1/items?mode=selected",
                cache=cache,
            ) == payload
            assert module.fetch_json(
                "https://aihot.news/api/v1/items?mode=selected",
                cache=cache,
            ) == payload

        requests = [call.args[0] for call in urlopen.call_args_list]
        assert _request_headers(requests[0])["accept-encoding"] == "gzip"
        assert "if-none-match" not in _request_headers(requests[0])
        assert _request_headers(requests[1])["if-none-match"] == '"v1"'
        saved = json.loads((tmp_path / "http-cache.json").read_text(encoding="utf-8"))
        assert saved["https://aihot.news/api/v1/items?mode=selected"]["etag"] == '"v1"'

    def test_429_honours_retry_after(self):
        module = load_module()
        first = _http_error(429, retry_after="0.25")
        second = _ok_response({"items": []})
        with patch.object(module.time, "sleep") as sleep_mock, patch(
            "urllib.request.urlopen", side_effect=[first, second]
        ):
            assert module.fetch_json(
                "https://aihot.news/api/v1/items", retries=2
            ) == {"items": []}
        sleep_mock.assert_called_once_with(0.25)

    def test_503_is_retried(self):
        module = load_module()
        with patch.object(module.time, "sleep"), patch(
            "urllib.request.urlopen",
            side_effect=[_http_error(503), _ok_response({"items": []})],
        ):
            assert module.fetch_json(
                "https://aihot.news/api/v1/items", retries=2
            ) == {"items": []}

    def test_non_retryable_error_raises_immediately(self):
        module = load_module()
        with patch.object(module.time, "sleep") as sleep_mock, patch(
            "urllib.request.urlopen", side_effect=_http_error(404)
        ) as urlopen:
            try:
                module.fetch_json("https://aihot.news/api/v1/missing")
                raised = False
            except urllib.error.HTTPError:
                raised = True
        assert raised
        assert urlopen.call_count == 1
        assert not sleep_mock.called


class TestSelectedSync:
    def test_snapshot_merges_pages_and_keeps_first_cursor(
        self, tmp_path, monkeypatch
    ):
        module = load_module()
        calls: list[tuple[str, dict]] = []

        def fake_fetch(url, retries=3, **kwargs):
            calls.append((url, kwargs))
            query = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)
            if "page" not in query:
                return {
                    "schemaVersion": 1,
                    "asOf": "2026-11-15T00:00:00Z",
                    "cursor": "first-cursor",
                    "hasMore": True,
                    "nextPage": "page-2",
                    "items": [{"id": "a", "title": "A"}],
                }
            return {
                "schemaVersion": 1,
                "asOf": "2026-11-15T00:00:00Z",
                "cursor": "first-cursor",
                "hasMore": False,
                "nextPage": None,
                "items": [{"id": "b", "title": "B"}],
            }

        monkeypatch.setattr(module, "fetch_json", fake_fetch)
        client = module.AihotClient(module.BASE, None)
        state = module.sync_snapshot(client, tmp_path / "selected.json")

        assert state["cursor"] == "first-cursor"
        assert [item["id"] for item in state["items"]] == ["a", "b"]
        assert calls[0][1]["send_etag"] is False
        assert calls[1][1]["send_etag"] is True
        assert json.loads((tmp_path / "selected.json").read_text(encoding="utf-8"))[
            "count"
        ] == 2

    def test_changes_apply_upsert_and_remove(self, tmp_path, monkeypatch):
        module = load_module()
        state = {
            "version": 1,
            "schemaVersion": 1,
            "base_url": module.BASE,
            "asOf": "2026-11-15T00:00:00Z",
            "cursor": "old",
            "items": [{"id": "keep", "title": "keep"}, {"id": "gone", "title": "gone"}],
        }
        calls = []

        def fake_fetch(url, retries=3, **kwargs):
            calls.append(url)
            return {
                "schemaVersion": 1,
                "cursor": "new",
                "hasMore": False,
                "changes": [
                    {"op": "upsert", "item": {"id": "new", "title": "new"}},
                    {"op": "upsert", "item": {"id": "keep", "title": "updated"}},
                    {"op": "remove", "id": "gone"},
                ],
            }

        monkeypatch.setattr(module, "fetch_json", fake_fetch)
        client = module.AihotClient(module.BASE, None)
        result = module.sync_changes(client, state, tmp_path / "selected.json")

        assert result["cursor"] == "new"
        assert {item["id"]: item["title"] for item in result["items"]} == {
            "keep": "updated",
            "new": "new",
        }
        assert "cursor=old" in calls[0]

    def test_409_rebootstraps_from_snapshot(self, tmp_path, monkeypatch):
        module = load_module()
        state_path = tmp_path / "selected.json"
        state_path.write_text(
            json.dumps(
                {
                    "version": 1,
                    "schemaVersion": 1,
                    "base_url": module.BASE,
                    "cursor": "stale",
                    "asOf": "2026-11-01T00:00:00Z",
                    "items": [],
                }
            ),
            encoding="utf-8",
        )
        calls: list[str] = []

        def fake_fetch(url, retries=3, **kwargs):
            calls.append(url)
            if "/selected/changes" in url:
                raise _http_error(409)
            return {
                "schemaVersion": 1,
                "asOf": "2026-11-15T00:00:00Z",
                "cursor": "fresh",
                "hasMore": False,
                "nextPage": None,
                "items": [{"id": "fresh-item"}],
            }

        monkeypatch.setattr(module, "fetch_json", fake_fetch)
        client = module.AihotClient(module.BASE, None)
        result = module.sync_selected(client, state_path)

        assert result["cursor"] == "fresh"
        assert result["items"][0]["id"] == "fresh-item"
        assert any("/selected/changes" in url for url in calls)
        assert any("/selected/snapshot" in url for url in calls)

    def test_old_base_url_state_is_not_reused(self, tmp_path, monkeypatch):
        module = load_module()
        state_path = tmp_path / "selected.json"
        state_path.write_text(
            json.dumps(
                {
                    "version": 1,
                    "schemaVersion": 1,
                    "base_url": "https://old.example.com",
                    "cursor": "old-cursor",
                    "asOf": "2026-11-01T00:00:00Z",
                    "items": [{"id": "old"}],
                }
            ),
            encoding="utf-8",
        )
        seen: list[str] = []

        def fake_fetch(url, retries=3, **kwargs):
            seen.append(url)
            return {
                "schemaVersion": 1,
                "asOf": "2026-11-15T00:00:00Z",
                "cursor": "new-cursor",
                "hasMore": False,
                "nextPage": None,
                "items": [{"id": "new"}],
            }

        monkeypatch.setattr(module, "fetch_json", fake_fetch)
        client = module.AihotClient(module.BASE, None)
        result = module.sync_selected(client, state_path)

        assert seen and "/selected/snapshot" in seen[0]
        assert result["cursor"] == "new-cursor"
        assert [item["id"] for item in result["items"]] == ["new"]

    def test_unversioned_legacy_state_is_not_reused(self, tmp_path, monkeypatch):
        module = load_module()
        state_path = tmp_path / "selected.json"
        state_path.write_text(
            json.dumps(
                {
                    "cursor": "legacy-cursor",
                    "asOf": "2026-11-01T00:00:00Z",
                    "items": [{"id": "legacy"}],
                }
            ),
            encoding="utf-8",
        )
        seen: list[str] = []

        def fake_fetch(url, retries=3, **kwargs):
            seen.append(url)
            return {
                "schemaVersion": 1,
                "asOf": "2026-11-15T00:00:00Z",
                "cursor": "fresh",
                "hasMore": False,
                "nextPage": None,
                "items": [{"id": "fresh"}],
            }

        monkeypatch.setattr(module, "fetch_json", fake_fetch)
        client = module.AihotClient(module.BASE, None)
        result = module.sync_selected(client, state_path)

        assert "/selected/snapshot" in seen[0]
        assert result["cursor"] == "fresh"
        assert [item["id"] for item in result["items"]] == ["fresh"]
