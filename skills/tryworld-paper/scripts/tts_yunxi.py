#!/usr/bin/env python3
"""Synthesize Chinese narration via edge-tts (multi-voice, default 真·云希).

Usage:
  python tts_yunxi.py <script.txt> --out work/audio [--voice yunxi]
                       [--rate +8%] [--volume +0%] [--pitch +0Hz]
                       [--max-chars 700]

Voice presets (--voice takes a preset name or any full edge-tts voice id):
  yunxi     zh-CN-YunxiNeural              male, sunny (default, brand voice)
  xiaoxiao  zh-CN-XiaoxiaoNeural           female, warm
  xiaoyi    zh-CN-XiaoyiNeural             female, lively
  yunjian   zh-CN-YunjianNeural            male, passionate
  yunyang   zh-CN-YunyangNeural            male, news anchor
  yunxia    zh-CN-YunxiaNeural             male, youthful
  xiaobei   zh-CN-liaoning-XiaobeiNeural   female, Northeastern dialect
  xiaoni    zh-CN-shaanxi-XiaoniNeural     female, Shaanxi dialect

Input: UTF-8 text file. Blank-line separated paragraphs are preserved as
groups. Mid-sentence line breaks are joined (no artificial pause). Segments
are split ONLY at sentence endings (。！？…), so the narration never pauses or
stutters in the middle of a sentence.

Output:
  segment-XXX.mp3   one file per sentence group
  narration.mp3     concatenated full narration
  segments.json     per-segment start/duration + total (for timeline math)
  sentences.json    absolute sentence-level timings from edge-tts (caption sync)
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import edge_tts

SENTENCE_END = "。！？…!?"


def find_bin(name: str) -> Path | None:
    """Locate ffmpeg/ffprobe: PATH, env override, then common WinGet locations."""
    which = shutil.which(name)
    if which:
        return Path(which)
    env_dir = os.environ.get("HYPERFRAMES_FFMPEG_DIR") or os.environ.get("FFMPEG_BIN")
    if env_dir:
        candidate = Path(env_dir) / (name + ".exe")
        if candidate.exists():
            return candidate
    localappdata = os.environ.get("LOCALAPPDATA", "")
    winget = Path(localappdata) / "Microsoft" / "WinGet" / "Packages"
    if winget.exists():
        for sub in sorted(winget.glob("Gyan.FFmpeg*/ffmpeg-*/bin")):
            candidate = sub / (name + ".exe")
            if candidate.exists():
                return candidate
    return None


async def synth(
    text: str, out_path: Path, voice: str, rate: str, volume: str, pitch: str
) -> list[dict]:
    """Synthesize one segment; return sentence boundaries relative to this segment."""
    last_error: Exception | None = None
    for attempt in range(2):
        try:
            comm = edge_tts.Communicate(text, voice, rate=rate, volume=volume, pitch=pitch)
            sentences: list[dict] = []
            with open(out_path, "wb") as audio_file:
                async for chunk in comm.stream():
                    if chunk["type"] == "audio":
                        audio_file.write(chunk["data"])
                    elif chunk["type"] == "SentenceBoundary":
                        start_s = chunk["offset"] / 10_000_000
                        end_s = start_s + chunk["duration"] / 10_000_000
                        sentences.append(
                            {
                                "start": round(start_s, 3),
                                "end": round(end_s, 3),
                                "text": chunk["text"],
                            }
                        )
            if not out_path.exists() or out_path.stat().st_size == 0:
                raise RuntimeError("edge-tts produced empty audio")
            return sentences
        except Exception as exc:  # network hiccups are common; retry once
            last_error = exc
            await asyncio.sleep(1)
    raise RuntimeError(f"edge-tts failed for {out_path.name}: {last_error}")


def duration_seconds(path: Path, text: str) -> tuple[float, str]:
    """Return (duration, source). source is ffprobe, mutagen, or estimate."""
    ffprobe = find_bin("ffprobe")
    if ffprobe:
        try:
            result = subprocess.run(
                [
                    str(ffprobe), "-v", "error", "-show_entries", "format=duration",
                    "-of", "default=noprint_wrappers=1:nokey=1", str(path),
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            return round(float(result.stdout.strip()), 3), "ffprobe"
        except (subprocess.SubprocessError, ValueError):
            pass
    try:
        from mutagen.mp3 import MP3

        return round(float(MP3(str(path)).info.length), 3), "mutagen"
    except ImportError:
        pass
    except Exception:
        pass
    estimate = max(0.5, round(len(text) / 3.5, 3))
    print(f"warning: no ffprobe/mutagen, duration estimated for {path.name}", file=sys.stderr)
    return estimate, "estimate"


def concat_mp3(segments: list[Path], out_path: Path) -> bool:
    ffmpeg = find_bin("ffmpeg")
    if ffmpeg is None:
        print(
            "warning: ffmpeg not found, skipping narration.mp3 concat; "
            "use segment files individually or install FFmpeg",
            file=sys.stderr,
        )
        return False
    list_file = out_path.with_suffix(".list.txt")
    list_file.write_text(
        "".join(f"file '{s.resolve().as_posix()}'\n" for s in segments),
        encoding="utf-8",
    )
    subprocess.run(
        [
            str(ffmpeg), "-y", "-f", "concat", "-safe", "0", "-i", str(list_file),
            "-c", "copy", str(out_path),
        ],
        check=True,
        capture_output=True,
    )
    return True


MARKDOWN_PREFIX = re.compile(r"^\s*(#{1,6}\s*|[-*+]\s+|\d+[.、]\s*|>\s*)")


def strip_markdown(line: str) -> str | None:
    """Strip markdown artifacts; return None for structural heading lines (not spoken)."""
    if re.match(r"^\s*#{1,6}\s+", line):
        return None
    line = MARKDOWN_PREFIX.sub("", line)
    for token in ("**", "__", "`", "~~"):
        line = line.replace(token, "")
    return line.strip() or None


def normalize_paragraph(paragraph: str) -> str:
    """Strip markdown, join mid-sentence line breaks, ensure sentence-ending punctuation."""
    lines = [stripped for line in paragraph.split("\n") if (stripped := strip_markdown(line))]
    if not lines:
        return ""
    joined = lines[0]
    for line in lines[1:]:
        joined += line  # Chinese needs no space; removes mid-sentence line-break pauses
    joined = re.sub(r"\s+", " ", joined).strip()
    if joined and joined[-1] not in SENTENCE_END:
        joined += "。"
    return joined


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[。！？…!?])", text)
    return [part.strip() for part in parts if part.strip()]


def build_segments(paragraphs: list[str], max_chars: int) -> list[tuple[int, str]]:
    """Group sentences into segments; boundaries only at paragraph or sentence ends."""
    segments: list[tuple[int, str]] = []
    for paragraph_index, paragraph in enumerate(paragraphs, start=1):
        buffer = ""
        for sentence in split_sentences(paragraph):
            if buffer and len(buffer) + len(sentence) > max_chars:
                segments.append((paragraph_index, buffer))
                buffer = ""
            buffer += sentence
        if buffer:
            segments.append((paragraph_index, buffer))
    return segments


# 中文音色预设（实测于 edge-tts --list-voices，2026-08-28；--voice 也接受完整音色 id）
VOICE_PRESETS = {
    "yunxi": "zh-CN-YunxiNeural",  # 男 · 阳光（默认，试界品牌音色）
    "xiaoxiao": "zh-CN-XiaoxiaoNeural",  # 女 · 温暖（新闻/小说）
    "xiaoyi": "zh-CN-XiaoyiNeural",  # 女 · 活泼
    "yunjian": "zh-CN-YunjianNeural",  # 男 · 浑厚激情（体育/小说）
    "yunyang": "zh-CN-YunyangNeural",  # 男 · 新闻播报，专业沉稳
    "yunxia": "zh-CN-YunxiaNeural",  # 男 · 少年感
    "xiaobei": "zh-CN-liaoning-XiaobeiNeural",  # 女 · 东北方言
    "xiaoni": "zh-CN-shaanxi-XiaoniNeural",  # 女 · 陕西方言
}
DEFAULT_VOICE = "yunxi"


def main() -> int:
    parser = argparse.ArgumentParser(description="Chinese narration pipeline (default 真·云希, multi-voice)")
    parser.add_argument("script", type=Path, help="UTF-8 script file (.txt/.md)")
    parser.add_argument("--out", type=Path, default=Path("work/audio"), help="output directory")
    parser.add_argument(
        "--voice", default=None,
        help="voice preset (yunxi/xiaoxiao/xiaoyi/yunjian/yunyang/yunxia/xiaobei/xiaoni) "
             "or a full edge-tts voice id; overrides --theme",
    )
    parser.add_argument(
        "--theme", type=Path, default=None,
        help="theme JSON file; its voice.preset is used when --voice is omitted",
    )
    parser.add_argument("--rate", default="+8%", help="speech rate, e.g. +5% / +8% / +15%")
    parser.add_argument("--volume", default="+0%", help="volume, e.g. +0%")
    parser.add_argument("--pitch", default="+0Hz", help="pitch, e.g. +0Hz")
    parser.add_argument("--max-chars", type=int, default=700, help="max chars per segment")
    args = parser.parse_args()

    theme_preset = None
    if args.theme is not None:
        if not args.theme.exists():
            print(f"error: theme file not found: {args.theme}", file=sys.stderr)
            return 1
        try:
            cfg = json.loads(args.theme.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            print(f"error: cannot read theme file: {exc}", file=sys.stderr)
            return 1
        theme_voice = cfg.get("voice") or {}
        theme_preset = theme_voice.get("preset")
        engine = theme_voice.get("engine")
        if engine and engine != "edge-tts":
            print(
                f"warning: theme requests engine '{engine}' but this script only supports "
                "edge-tts; continuing with edge-tts.",
                file=sys.stderr,
            )

    voice_name = args.voice or theme_preset or DEFAULT_VOICE
    voice = VOICE_PRESETS.get(voice_name, voice_name)
    if "-" not in voice:
        print(
            f"error: unknown voice '{voice_name}'. Available presets: "
            f"{'/'.join(VOICE_PRESETS)}; or pass a full edge-tts voice id "
            "(e.g. zh-CN-XiaoxiaoNeural).",
            file=sys.stderr,
        )
        return 1
    print(f"voice: {voice}")

    if not args.script.exists():
        print(f"error: script file not found: {args.script}", file=sys.stderr)
        return 1

    args.out.mkdir(parents=True, exist_ok=True)
    raw_text = args.script.read_text(encoding="utf-8")
    paragraphs = [
        normalize_paragraph(p)
        for p in raw_text.replace("\r\n", "\n").split("\n\n")
        if p.strip()
    ]
    if not paragraphs:
        print("error: no paragraphs found (separate paragraphs with blank lines)", file=sys.stderr)
        return 1

    segments = build_segments(paragraphs, args.max_chars)
    segments_meta: list[dict] = []
    all_sentences: list[dict] = []
    mp3s: list[Path] = []
    offset = 0.0

    for segment_index, (paragraph_index, text) in enumerate(segments, start=1):
        mp3 = args.out / f"segment-{segment_index:03d}.mp3"
        print(f"[{segment_index}/{len(segments)}] synthesizing {len(text)} chars ...")
        sentences = asyncio.run(
            synth(text, mp3, voice, args.rate, args.volume, args.pitch)
        )
        duration, duration_source = duration_seconds(mp3, text)
        segments_meta.append(
            {
                "index": segment_index,
                "paragraph": paragraph_index,
                "file": mp3.name,
                "start": round(offset, 3),
                "duration": duration,
                "durationSource": duration_source,
                "text": text,
            }
        )
        for sentence in sentences:
            all_sentences.append(
                {
                    "segment": segment_index,
                    "start": round(sentence["start"] + offset, 3),
                    "end": round(sentence["end"] + offset, 3),
                    "text": sentence["text"],
                }
            )
        offset += duration
        mp3s.append(mp3)

    # edge-tts sentence boundaries can slightly overlap; clamp to avoid caption collisions.
    normalized_sentences: list[dict] = []
    last_end = 0.0
    for sentence in all_sentences:
        sentence["start"] = round(max(sentence["start"], last_end), 3)
        sentence["end"] = round(max(sentence["end"], sentence["start"]), 3)
        last_end = sentence["end"]
        normalized_sentences.append(sentence)

    narration = args.out / "narration.mp3"
    concatenated = concat_mp3(mp3s, narration)

    (args.out / "segments.json").write_text(
        json.dumps(
            {
                "segments": segments_meta,
                "totalDuration": round(offset, 3),
                "narrationConcat": concatenated,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (args.out / "sentences.json").write_text(
        json.dumps(
            {
                "sentences": normalized_sentences,
                "totalDuration": round(offset, 3),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(json.dumps(
        {
            "segments": len(segments_meta),
            "totalDuration": round(offset, 3),
            "narration": str(narration) if concatenated else None,
            "warning": None if concatenated else "ffmpeg not found; narration.mp3 not concatenated",
        },
        ensure_ascii=False,
    ))
    return 0


if __name__ == "__main__":
    sys.exit(main())
