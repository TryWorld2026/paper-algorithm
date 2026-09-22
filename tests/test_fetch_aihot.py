"""Tests for fetch_aihot.py (import, CLI help, retry logic; no network)."""
import importlib.util
import subprocess
import sys
import urllib.error
from pathlib import Path
from unittest.mock import MagicMock, patch

REPO = Path(__file__).resolve().parents[1]
FETCH = REPO / "skills" / "tryworld-topics" / "scripts" / "fetch_aihot.py"


def load_module():
    spec = importlib.util.spec_from_file_location("fetch_aihot", str(FETCH))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _ok_response(payload: bytes = b'{"items": []}'):
    resp = MagicMock()
    resp.read.return_value = payload
    resp.__enter__ = lambda self: self
    resp.__exit__ = lambda self, *args: None
    return resp


def _http_error(code: int) -> urllib.error.HTTPError:
    return urllib.error.HTTPError("https://example.invalid/x", code, "err", None, None)


class TestImport:
    def test_imports_without_third_party(self):
        m = load_module()
        assert m.BASE == "https://aihot.virxact.com"
        assert callable(m.fetch_json)


class TestCli:
    def test_help_exposes_base_url(self):
        r = subprocess.run(
            [sys.executable, "-X", "utf8", str(FETCH), "--help"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        assert r.returncode == 0
        assert "--base-url" in r.stdout
        assert "https://aihot.virxact.com" in r.stdout


class TestFetchJsonRetry:
    def test_retries_on_429_then_succeeds(self):
        m = load_module()
        with patch.object(m.time, "sleep") as sleep_mock, \
             patch("urllib.request.urlopen", side_effect=[_http_error(429), _ok_response()]) as urlopen:
            result = m.fetch_json("https://example.invalid/x")
        assert result == {"items": []}
        assert urlopen.call_count == 2
        assert sleep_mock.called

    def test_retries_on_503_then_succeeds(self):
        m = load_module()
        with patch.object(m.time, "sleep"), \
             patch("urllib.request.urlopen", side_effect=[_http_error(503), _ok_response()]):
            assert m.fetch_json("https://example.invalid/x") == {"items": []}

    def test_non_retryable_http_error_raises_immediately(self):
        m = load_module()
        with patch.object(m.time, "sleep") as sleep_mock, \
             patch("urllib.request.urlopen", side_effect=_http_error(404)) as urlopen:
            try:
                m.fetch_json("https://example.invalid/x")
                raised = False
            except urllib.error.HTTPError:
                raised = True
        assert raised
        assert urlopen.call_count == 1
        assert not sleep_mock.called

    def test_url_error_raises_immediately(self):
        m = load_module()
        with patch.object(m.time, "sleep") as sleep_mock, \
             patch("urllib.request.urlopen", side_effect=urllib.error.URLError("dns down")):
            try:
                m.fetch_json("https://example.invalid/x")
                raised = False
            except urllib.error.URLError:
                raised = True
        assert raised
        assert not sleep_mock.called
