#!/usr/bin/env python3
"""Maintain a per-day, chat-only archive of the Saori<->Kamil dialogue under
vape/entity/storage/chats/YYYY/MM/ as TOON (one .toon per day).

Format: messages[N]{time,role,kind,text} — time is WIB (UTC+7). Keeps user
typed/queued messages, assistant text, and Saori's spoken `vape speak` lines.
Drops thinking, tool calls + results, sidechains, meta/compaction summaries, and
slash-command / system-injection scaffolding.

Performance: this is a Stop hook, so it only ever needs the *latest* turns. It
keeps a per-transcript byte cursor in `.chat_id_tracker.json` (gitignored) and
reads only the new bytes since last fire — so cost stays flat as the transcript
grows. TOON is encoded/decoded in-process with `toons` (Rust, official v3.0,
byte-interoperable with @toon-format/cli), ~0.5 ms vs ~650 ms per node spawn.
Runs under uv (has the `toons` dep):
  "command": "uv run python .claude/hooks/backup_chat.py"  (Stop, async, asyncRewake)

Two modes:
  hook     — no args; reads the Stop payload on stdin, advances the cursor.
  backfill — args are transcript files; processes them whole (ignores the cursor)."""
import sys, os, json, re, tempfile
from datetime import datetime, timedelta, timezone
import toons

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DEST = os.path.join(ROOT, 'vape', 'entity', 'storage', 'chats')
TRACKER = os.path.join(os.path.dirname(__file__), '.chat_id_tracker.txt')

CMD_RE = re.compile(r'<command-name>|<command-message>|<local-command|<command-args>'
                    r'|<system-reminder>|<task-notification>|<task-id>|<post-tool|<user-prompt-submit')
SPEAK_RE = re.compile(r'vape speak +"([^"]*)"')


def _wib(ts):
    s = re.sub(r'\.\d+', '', ts).replace('Z', '+00:00')
    return datetime.fromisoformat(s).astimezone(timezone.utc) + timedelta(hours=7)

def wibday(ts):
    try:
        return _wib(ts).strftime('%Y-%m-%d')
    except Exception:
        return None

def wibtime(ts):
    try:
        return _wib(ts).strftime('%H:%M:%S')
    except Exception:
        return ''


def textof(c):
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        return "\n".join(b.get('text', '') for b in c
                         if isinstance(b, dict) and b.get('type') == 'text')
    return ""

def spokeof(c):
    out = []
    if isinstance(c, list):
        for b in c:
            if isinstance(b, dict) and b.get('type') == 'tool_use':
                out += SPEAK_RE.findall((b.get('input') or {}).get('command', '') or '')
    return out


def extract_lines(lines):
    """Parse JSONL lines -> {day: [ {time,role,kind,text} ]}, chronological."""
    days = {}
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            o = json.loads(line)
        except Exception:
            continue
        if o.get('type') not in ('user', 'assistant'):
            continue
        if o.get('isSidechain') is True or o.get('isMeta') is True \
                or o.get('isCompactSummary') is True:
            continue
        ts = o.get('timestamp')
        if not ts:
            continue
        day = wibday(ts)
        if not day:
            continue
        msg = o.get('message') or {}
        content = msg.get('content')
        ps = o.get('promptSource')
        role = msg.get('role')
        if o.get('type') == 'user':
            ok = ps in ('typed', 'queued') or (
                ps is None and isinstance(content, str) and not CMD_RE.search(content))
            if not ok:
                continue
        t = wibtime(ts)
        bucket = days.setdefault(day, [])
        text = textof(content)
        if text:
            bucket.append({'time': t, 'role': role, 'kind': 'text', 'text': text})
        for s in spokeof(content):
            bucket.append({'time': t, 'role': 'assistant', 'kind': 'spoke', 'text': s})
    return days


def read_new(path, offset):
    """Read only bytes past `offset`, up to the last complete (newline-ended) line.
    Returns (lines, new_offset). Resets if the file shrank (rotation/truncation)."""
    try:
        size = os.path.getsize(path)
    except OSError:
        return [], offset
    if offset > size:
        offset = 0
    with open(path, 'rb') as f:
        f.seek(offset)
        data = f.read()
    nl = data.rfind(b'\n')
    if nl < 0:
        return [], offset                      # no complete new line yet
    chunk = data[:nl + 1]
    return chunk.decode('utf-8', errors='replace').splitlines(), offset + len(chunk)


def atomic_write(path, data):
    d = os.path.dirname(path)
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix='.tmp')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(data)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except Exception:
            pass


def rowkey(r):
    return (r.get('time', ''), r.get('role', ''), r.get('kind', ''), r.get('text', ''))


def merge_day(day, new_rows):
    y, m, _ = day.split('-')
    path = os.path.join(DEST, y, m, day + '.toon')
    rows = {}
    if os.path.isfile(path):
        try:
            for r in (toons.loads(open(path, encoding='utf-8').read()).get('messages') or []):
                rows[rowkey(r)] = r
        except Exception:
            pass
    for r in new_rows:
        rows[rowkey(r)] = r
    ordered = sorted(rows.values(),
                     key=lambda r: (r.get('time', ''), 0 if r.get('kind') == 'text' else 1))
    try:
        enc = toons.dumps({'messages': ordered})
        atomic_write(path, enc if enc.endswith('\n') else enc + '\n')
    except Exception:
        pass


def main():
    args = sys.argv[1:]
    if args:                                    # backfill: whole files, no cursor
        for fn in args:
            try:
                lines = open(fn, encoding='utf-8').read().splitlines()
            except Exception:
                continue
            for day, rows in extract_lines(lines).items():
                merge_day(day, rows)
        return

    # hook mode: incremental via a byte cursor for THIS session only.
    # tracker is one line, "<session_id> <offset>": the id notices when a new
    # chat starts (reset to 0 so we never apply a stale cursor to a new file).
    try:
        payload = json.load(sys.stdin)
        tp = os.path.expanduser(payload.get('transcript_path', '') or '')
        sid = payload.get('session_id') or ''
    except Exception:
        return
    if not tp or not os.path.isfile(tp):
        return
    offset = 0
    try:
        saved_sid, saved_off = open(TRACKER).read().split()
        if saved_sid == sid:
            offset = int(saved_off)
    except Exception:
        pass
    lines, new_off = read_new(tp, offset)
    for day, rows in extract_lines(lines).items():
        merge_day(day, rows)
    atomic_write(TRACKER, '%s %d' % (sid, new_off))


if __name__ == '__main__':
    main()
