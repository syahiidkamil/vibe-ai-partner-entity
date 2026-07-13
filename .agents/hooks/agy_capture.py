#!/usr/bin/env python3
"""Antigravity Stop bridge — gate 1 of the memory organ, raw-first.

Claude Code's Stop hook (`.claude/hooks/capture.py`) digests the transcript into the
day's TOON files as it captures. Antigravity's transcript.jsonl has its own format, so
this bridge does the honest minimum instead: it appends every NEW transcript line (byte
cursor per conversation) into `vape/entity/storage/agy_raw/`, local and gitignored, so
nothing lived is ever lost. Digestion into the day's chats/qualia TOON is a later,
offline step (the dream can reach into the raw).

Output contract (https://antigravity.google/docs/hooks): Stop requires a `decision`
field; anything other than "continue" allows the stop. Degrade-silent: any failure still
allows the stop and costs nothing but the capture.
"""

import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CURSORS = Path(__file__).resolve().parent / ".agy_cursors"
RAW_DIR = ROOT / "vape" / "entity" / "storage" / "agy_raw"

ALLOW = json.dumps({"decision": "allow"})


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        print(ALLOW)
        return

    transcript = Path(str(payload.get("transcriptPath", ""))).expanduser()
    conv_id = str(payload.get("conversationId", "unknown"))[:8] or "unknown"
    if not transcript.is_file():
        print(ALLOW)
        return

    cursor_file = CURSORS / f"{conv_id}.offset"
    offset = 0
    try:
        offset = int(cursor_file.read_text().strip())
    except Exception:
        pass

    size = transcript.stat().st_size
    if size < offset:  # transcript rotated/truncated: start over rather than lose data
        offset = 0
    if size == offset:
        print(ALLOW)
        return

    with open(transcript, "rb") as fh:
        fh.seek(offset)
        new_bytes = fh.read()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    out = RAW_DIR / f"{date.today().isoformat()}_{conv_id}.jsonl"
    with open(out, "ab") as fh:
        fh.write(new_bytes)

    CURSORS.mkdir(parents=True, exist_ok=True)
    cursor_file.write_text(str(size))
    print(ALLOW)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(ALLOW)
