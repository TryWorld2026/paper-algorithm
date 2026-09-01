#!/usr/bin/env python3
"""交付核验硬门禁：verify_output.py --dir <outputs 目录>

逐项检查交付物完整性，任何一项不通过则 exit 1（不交付）。
检查项：主视频存在且有音轨、时长>0 且与字幕时间轴一致、双封面存在且尺寸正确、
titles.txt 非空、发布计划.txt 存在、字幕时间轴存在。
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path


def ffprobe(path: Path, args: list[str]) -> str:
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error", *args, "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
            capture_output=True, text=True,
        )
    except FileNotFoundError:
        print("error: ffprobe 不可用（请安装 FFmpeg 并加入 PATH），无法执行核验。")
        sys.exit(2)
    return r.stdout.strip() if r.returncode == 0 else ""


def main() -> int:
    ap = argparse.ArgumentParser(description="交付核验硬门禁")
    ap.add_argument("--dir", type=Path, default=Path("outputs"), help="outputs 目录")
    ap.add_argument("--video", type=Path, default=None, help="主视频路径（outputs 中有多个 mp4 时用于指定）")
    args = ap.parse_args()
    out = args.dir
    failures: list[str] = []

    def check(ok: bool, label: str, detail: str = "") -> None:
        mark = "PASS" if ok else "FAIL"
        print(f"[{mark}] {label}" + (f"  ({detail})" if detail else ""))
        if not ok:
            failures.append(label)

    # 1. 主视频唯一、有视频流与音轨
    videos = sorted(out.glob("*.mp4"))
    dur_f = 0.0
    video = args.video if args.video else (videos[0] if len(videos) == 1 else None)
    if video is None:
        if len(videos) > 1:
            check(False, "outputs 中恰好一个主视频 mp4",
                  f"发现 {len(videos)} 个：{'、'.join(v.name for v in videos)}；删除多余文件，或用 --video 指定主视频")
        else:
            check(False, "主视频 *.mp4 存在")
    else:
        if not video.exists():
            check(False, "主视频存在（--video 指定的文件不存在）", str(video))
        else:
            streams = ffprobe(video, ["-show_entries", "stream=codec_type"])
            has_video = "video" in streams
            has_audio = "audio" in streams
            check(has_video, "主视频含视频流")
            check(has_audio, "主视频含音轨", "配音缺失即静音成片，禁止交付")
            dur = ffprobe(video, ["-show_entries", "format=duration"])
            try:
                dur_f = float(dur)
            except ValueError:
                dur_f = 0.0
            check(dur_f > 1, "主视频时长 > 1s", f"{dur_f:.1f}s")

    # 2. 字幕时间轴与主视频时长一致（±1s）
    tl_candidates = [out / "字幕时间轴_sentences.json", out / "sentences.json"]
    tl = next((f for f in tl_candidates if f.exists()), tl_candidates[0])
    if tl.exists() and video:
        try:
            total = json.loads(tl.read_text(encoding="utf-8")).get("totalDuration", 0)
            check(abs(total - dur_f) <= 1.0, "时间轴与主视频时长对齐", f"{total:.1f}s vs {dur_f:.1f}s")
        except (ValueError, json.JSONDecodeError):
            failures.append("时间轴 JSON 无法解析")
            print("[FAIL] 时间轴 JSON 无法解析")
    else:
        check(tl.exists(), "字幕时间轴_sentences.json 存在")

    # 3. 双封面存在且尺寸正确（兼容文档约定 cover_* 与中文交付命名）
    cover_specs = [
        (("封面_横版4x3.png", "cover_4x3.png"), (1920, 1440), "横版封面"),
        (("封面_竖版3x4.png", "cover_3x4.png"), (1080, 1440), "竖版封面"),
    ]
    for names, size, label in cover_specs:
        f = next((out / name for name in names if (out / name).exists()), out / names[0])
        name = f.name
        if not f.exists():
            check(False, f"{name} 存在")
            continue
        dim = ffprobe(f, ["-select_streams", "v:0", "-show_entries", "stream=width,height"])
        nums = [int(x) for x in dim.split() if x.strip().isdigit()]
        ok = len(nums) >= 2 and (nums[0], nums[1]) == size
        check(ok, f"{name} 尺寸 {size[0]}x{size[1]}", "x".join(str(n) for n in nums[:2]))

    # 4. 标题与发布计划
    titles = out / "titles.txt"
    check(titles.exists() and titles.stat().st_size > 50, "titles.txt 存在且非空（3-5 个标题）")
    check((out / "发布计划.txt").exists(), "发布计划.txt 存在")

    print()
    if failures:
        print(f"核验未通过：{len(failures)} 项失败 → {', '.join(failures)}")
        print("不满足交付条件，禁止交付。")
        return 1
    print("核验全部通过，允许交付。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
