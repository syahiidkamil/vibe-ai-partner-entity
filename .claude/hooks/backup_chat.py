#!/usr/bin/env python3
"""Maintain a per-day, chat-only archive of the Saori<->Kamil dialogue under
vape/entity/storage/chats/YYYY/MM/ as TOON (one .toon per day).

Format: messages[N]{time,role,kind,text} — time is WIB (UTC+7). Keeps user
typed/queued messages, assistant text, and Saori's spoken `vape speak` lines.
Drops thinking, tool calls + results, sidechains, meta/compaction summaries, and
slash-command / system-injection scaffolding.

TOON is encoded/decoded with the official @toon-format/cli (so it's always
spec-correct). The merge reads the existing day's .toon, unions the current
transcript's rows, dedups by content, sorts by time, and re-encodes — atomically.
node is located on PATH or under ~/.nvm/versions/node/*/bin. If node is truly
unreachable, the run is skipped (the .toon stays valid and catches up next run,
since each run re-reads the whole append-only transcript). Never raises.

Two modes:
  hook     — no args; reads the Stop payload on stdin, uses its transcript_path.
  backfill — args are transcript files; processes every June+ day they contain."""
import sys, os, json, re, glob, shutil, subprocess, tempfile
from datetime import datetime, timedelta, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DEST = os.path.join(ROOT, 'vape', 'entity', 'storage', 'chats')
FLOOR = '2026-06-01'   # don't archive pre-June (older transcripts predate promptSource / are noisy)

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


def extract(files):
    """-> {day: [ {time,role,kind,text} ]} in chronological order from these files."""
    days = {}
    for fn in files:
        try:
            with open(fn, encoding='utf-8') as fh:
                for line in fh:
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
                    if not day or day < FLOOR:
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
        except Exception:
            continue
    return days


def find_npx():
    p = shutil.which('npx')
    if p:
        return p
    c = sorted(glob.glob(os.path.expanduser('~/.nvm/versions/node/*/bin/npx')))
    return c[-1] if c else None


def toon(npx, flag, data):
    """Run the official CLI; flag is '--encode' or '--decode'. Returns stdout or None."""
    try:
        r = subprocess.run([npx, '-y', '@toon-format/cli', flag],
                           input=data, capture_output=True, text=True, timeout=120)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout
    except Exception:
        pass
    return None


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


def main():
    args = sys.argv[1:]
    if args:
        files = args
    else:
        try:
            payload = json.load(sys.stdin)
            tp = os.path.expanduser(payload.get('transcript_path', '') or '')
            files = [tp] if tp and os.path.isfile(tp) else []
        except Exception:
            files = []
    if not files:
        return

    npx = find_npx()
    if not npx:
        sys.stderr.write("backup-chat: node/npx not found — cannot read/write TOON, skipping run\n")
        return

    for day, new_rows in extract(files).items():
        y, m, _ = day.split('-')
        path = os.path.join(DEST, y, m, day + '.toon')
        rows = {}
        # existing day: decode and seed the merge
        if os.path.isfile(path):
            try:
                dec = toon(npx, '--decode', open(path, encoding='utf-8').read())
                if dec:
                    for r in (json.loads(dec).get('messages') or []):
                        rows[rowkey(r)] = r
            except Exception:
                pass
        for r in new_rows:
            rows[rowkey(r)] = r
        ordered = sorted(rows.values(), key=lambda r: (r.get('time', ''), 0 if r.get('kind') == 'text' else 1))
        enc = toon(npx, '--encode', json.dumps({'messages': ordered}, ensure_ascii=False))
        if enc:
            atomic_write(path, enc)


if __name__ == '__main__':
    main()
