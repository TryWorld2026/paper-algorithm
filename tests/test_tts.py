"""Tests for tts_yunxi.py (import and pure functions only)."""
import importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TTS = REPO / "skills" / "tryworld-paper" / "scripts" / "tts_yunxi.py"


def load_module():
    spec = importlib.util.spec_from_file_location("tts_yunxi", str(TTS))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TestImport:
    def test_imports_without_edge_tts(self):
        m = load_module()
        assert hasattr(m, "SENTENCE_END")
        assert hasattr(m, "_get_edge_tts")
        assert hasattr(m, "VOICE_PRESETS")

    def test_voice_presets(self):
        m = load_module()
        expected = {"yunxi", "xiaoxiao", "xiaoyi", "yunjian", "yunyang", "yunxia", "xiaobei", "xiaoni"}
        assert expected <= set(m.VOICE_PRESETS.keys())


class TestPureFunctions:
    def test_normalize_paragraph(self):
        m = load_module()
        r = m.normalize_paragraph("第一行\n第二行。")
        assert "第一行" in r and "第二行" in r

    def test_normalize_heading_returns_empty(self):
        m = load_module()
        r = m.normalize_paragraph("# 标题")
        assert r == ""

    def test_split_sentences(self):
        m = load_module()
        r = m.split_sentences("第一句。第二句！第三句？")
        assert len(r) == 3

    def test_build_segments_respects_max_chars(self):
        m = load_module()
        text = "。" * 100
        segments = m.build_segments([text], max_chars=50)
        for _, seg_text in segments:
            assert len(seg_text) <= 50

    def test_strip_markdown_exists(self):
        m = load_module()
        assert callable(m.strip_markdown)
        assert callable(m.normalize_paragraph)
        assert callable(m.split_sentences)
        assert callable(m.build_segments)

class TestCli:
    def test_tts_help(self):
        import subprocess
        import sys
        r = subprocess.run(
            [sys.executable, "-X", "utf8", str(TTS), "--help"],
            capture_output=True, text=True,
            encoding="utf-8", errors="replace",
        )
        assert r.returncode == 0
        assert "Chinese narration pipeline" in r.stdout
