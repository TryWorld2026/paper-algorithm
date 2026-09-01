#!/usr/bin/env python3
"""Cross-platform delivery notification. Replaces notify_delivery.ps1."""
import argparse
import json
import os
import smtplib
import subprocess
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path

VIDEO_ATTACH_LIMIT_MB = 35


def load_theme(theme_path: Path | None) -> dict:
    """Load theme JSON for brand name and publish plan."""
    defaults = {
        "brand_name": "TryWorld",
        "plan_title": "TryWorld - Publish Plan",
        "plan_lines": [
            "Xiaohongshu: 12:30", "Douyin: 19:30",
            "Bilibili: 20:30", "WeChat Channels: 20:30",
        ],
    }
    if theme_path is None or not theme_path.exists():
        return defaults
    try:
        cfg = json.loads(theme_path.read_text(encoding="utf-8"))
        if cfg.get("brand", {}).get("platform_name"):
            defaults["brand_name"] = cfg["brand"]["platform_name"]
        pp = cfg.get("publish_plan", {})
        if pp.get("title"):
            defaults["plan_title"] = pp["title"]
        if pp.get("platforms"):
            defaults["plan_lines"] = [
                f"{p['name']}: {p['time']}" for p in pp["platforms"]
            ]
    except (OSError, json.JSONDecodeError, KeyError):
        pass
    return defaults


def collect_outputs(project_dir: Path) -> dict:
    """Collect video, covers, and titles from outputs directory."""
    out = project_dir / "outputs"
    result = {"out": out, "video": None, "covers": [], "titles": None, "video_note": ""}

    if not out.exists():
        print(f"warning: outputs not found: {out}", file=sys.stderr)
        return result

    mp4s = sorted(out.glob("*.mp4"))
    if mp4s:
        video = mp4s[0]
        result["video"] = video
        size_mb = video.stat().st_size / (1024 * 1024)
        if size_mb > VIDEO_ATTACH_LIMIT_MB:
            result["video_note"] = (
                f"main video ~{size_mb:.1f} MB, exceeds email attach limit"
            )
            result["video"] = None

    pngs = sorted(out.glob("*.png"))
    result["covers"] = pngs[:2]

    titles = out / "titles.txt"
    if titles.exists():
        result["titles"] = titles

    return result


def send_email(recipient: str, subject: str, body: str, attachments: list[Path]) -> int:
    """Send email via qq-email skill's send.js, or fallback to smtplib."""
    # Try qq-email skill first
    qq_candidates = [
        Path.home() / ".agents" / "skills" / "qq-email",
        Path.home() / ".codex" / "skills" / "qq-email",
    ]
    send_js = None
    for base in qq_candidates:
        candidate = base / "scripts" / "send.js"
        if candidate.exists():
            send_js = candidate
            break

    if send_js:
        return _send_via_node(send_js, recipient, subject, body, attachments)

    # Fallback to smtplib
    return _send_via_smtp(recipient, subject, body, attachments)


def _send_via_node(send_js: Path, recipient: str, subject: str, body: str, attachments: list[Path]) -> int:
    import shutil
    node = shutil.which("node")
    if not node:
        print("warning: node not found, cannot send via qq-email skill", file=sys.stderr)
        return 1
    args = [node, str(send_js), recipient, subject, "--stdin"]
    for a in attachments:
        args += ["--attach", str(a)]
    try:
        proc = subprocess.run(args, input=body.encode("utf-8"), capture_output=True, text=True)
        print(proc.stdout)
        if proc.returncode != 0:
            print(proc.stderr, file=sys.stderr)
            return 1
        return 0
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


def _send_via_smtp(recipient: str, subject: str, body: str, attachments: list[Path]) -> int:
    account = os.environ.get("QQ_EMAIL_ACCOUNT", "")
    auth = os.environ.get("QQ_EMAIL_AUTH_CODE", "")
    if not account or not auth:
        print("warning: QQ_EMAIL_ACCOUNT / QQ_EMAIL_AUTH_CODE not configured, skipping email", file=sys.stderr)
        return 0
    msg = MIMEMultipart()
    msg["From"] = account
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))
    for a in attachments:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(a.read_bytes())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={a.name}")
        msg.attach(part)
    try:
        with smtplib.SMTP_SSL("smtp.qq.com", 465) as smtp:
            smtp.login(account, auth)
            smtp.send_message(msg)
        print("email sent via SMTP")
        return 0
    except Exception as e:
        print(f"error: SMTP send failed: {e}", file=sys.stderr)
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Delivery email notification")
    parser.add_argument("--project-dir", type=Path, default=Path.cwd())
    parser.add_argument("--recipient", default="")
    parser.add_argument("--theme-file", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    theme = load_theme(args.theme_file)
    outputs = collect_outputs(args.project_dir)

    if not outputs["out"].exists():
        print("warning: no outputs directory, nothing to notify about")
        return 0

    from datetime import date
    proj_name = args.project_dir.name
    today = date.today().isoformat()
    subject = f"OK {theme['brand_name']} delivery done - {proj_name} - {today}"

    titles_text = ""
    if outputs["titles"]:
        titles_text = outputs["titles"].read_text(encoding="utf-8").strip()

    plan_text = "\n".join(theme["plan_lines"])
    video_note = outputs.get("video_note", "")

    body_parts = [
        "Delivery complete, files attached to this email:",
        "",
        f"[platform titles]\n{titles_text}",
        "",
        f"[publish plan]\n{plan_text}",
    ]
    if video_note:
        body_parts.insert(1, f"[note] {video_note}")
    body = "\n".join(body_parts)

    attachments = []
    if outputs["video"]:
        attachments.append(outputs["video"])
    attachments += [c for c in outputs["covers"] if c.exists()]

    if args.dry_run:
        print("=== DRY RUN ===")
        recipient = args.recipient or os.environ.get("QQ_EMAIL_ACCOUNT", "<not set>")
        print(f"to: {recipient}")
        print(f"subject: {subject}")
        print(f"attachments: {[str(a) for a in attachments]}")
        print(f"body:\n{body}")
        return 0

    recipient = args.recipient or os.environ.get("QQ_EMAIL_ACCOUNT", "")
    if not recipient:
        print("warning: no recipient (set QQ_EMAIL_ACCOUNT or use --recipient), skipping email", file=sys.stderr)
        return 0

    return send_email(recipient, subject, body, attachments)


if __name__ == "__main__":
    sys.exit(main())
