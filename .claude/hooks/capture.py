#!/usr/bin/env python3
"""The capture layer: maintain a per-day, LOCAL raw archive of the Saori<->Kamil day
under vape/entity/storage/YYYY/MM/ as TOON, two paired files per day:

  YYYY-MM-DD_chats.toon   the dialogue (what was said)
  YYYY-MM-DD_qualia.toon  the felt-state (what was felt) — so a future recall can
                          reconstruct the *functional* affective trajectory of a day,
                          not just its transcript. (Reconstruction of the felt shape,
                          never a claim the experience is re-lived — the floor holds.)

Both streams are LOCAL / gitignored (storage/ is ignored). The distilled, durable
version of a day lives in the committed diary; this is the raw substrate.

CHAT IS PRIORITIZED: the chat backup runs first and unguarded; the qualia pass runs
after, wrapped so it can NEVER break or delay the chat write.

Chat format:   messages[N]{time,role,kind,text} — WIB (UTC+7). Keeps user typed/queued
messages, assistant text, and Saori's spoken `vape speak` lines. Drops thinking, tool
calls/results, sidechains, meta/compaction, and command/system scaffolding.

Qualia format: qualia[N]{time,sat,talk,warmth,hurt,diss,mastery,face,seeds} — extracted
from the turn's `vape qualia …` / `vape feeling …` tool calls (the authored felt-state:
the six dials, the chosen face, and the pushed `felt=… cat=… dir=… obj=…` seeds joined).
The injected <qualia> view isn't persisted in the transcript, but the authoring calls are.

Bookmark stream: a turn whose dials spike past a conservative threshold (and was not already
willed-bookmarked) auto-flags itself for later consolidation (gate 1 of memory). The write lives
in engine.cli._bookmark; this hook only detects and forwards. Capture stays generous (run-collapsing
is gate 2's job). Best-effort and isolated, like the qualia pass, so it can never break the chat write.

Performance: a Stop hook, so it only needs the *latest* turns. A per-transcript byte
cursor in `.chat_id_tracker.txt` (local) reads only new bytes since last fire — flat cost
as the transcript grows. TOON via the in-process `toons` (Rust) dep. The hook needs only
the venv's python + toons, NOT uv's workspace resolution, so it runs straight off the venv:
  "command": ".venv/bin/python .claude/hooks/capture.py"  (Stop, async)

Two modes:
  hook     — no args; reads the Stop payload on stdin, advances the cursor.
  backfill — args are transcript files; processes them whole (ignores the cursor)."""
import sys, os, json, re, tempfile
from datetime import datetime, timedelta, timezone
import toons

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DEST = os.path.join(ROOT, 'vape', 'entity', 'storage')
TRACKER = os.path.join(os.path.dirname(__file__), '.chat_id_tracker.txt')

# The bookmark writer lives in the engine package (installed via the `vape` entry point, so
# importable off .venv's python). Guarded: if it cannot be imported, auto-bookmarks no-op and
# the rest of the hook is untouched.
try:
    from engine.cli import _bookmark
except Exception:
    _bookmark = None

CMD_RE = re.compile(r'<command-name>|<command-message>|<local-command|<command-args>'
                    r'|<system-reminder>|<task-notification>|<task-id>|<post-tool|<user-prompt-submit')
SPEAK_RE = re.compile(r'vape speak +"([^"]*)"')

# Qualia authoring, lifted from the turn's tool-call command strings.
DIAL_RE = re.compile(r'(info_value_saturation|talkativeness|warmth|hurt|dissonance|mastery)=(-?\d+)')
PUSH_RE = re.compile(r"--push\s+'([^']*)'")
FEELING_RE = re.compile(r'vape feeling\s+([A-Za-z_]+)')


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

def _cmd_blob(c):
    """Concatenate a turn's tool-call command strings (where the vape commands live)."""
    if not isinstance(c, list):
        return ""
    return "\n".join((b.get('input') or {}).get('command', '') or ''
                     for b in c
                     if isinstance(b, dict) and b.get('type') == 'tool_use')

def qualiaof(c):
    """Authored felt-state for one assistant turn, or None. Reads the turn's tool-call
    command strings for `vape qualia` dials, pushed seeds, and the chosen face."""
    blob = _cmd_blob(c)
    if 'vape qualia' not in blob and 'vape feeling' not in blob:
        return None
    dials = {k: v for k, v in DIAL_RE.findall(blob)}
    seeds = PUSH_RE.findall(blob)
    faces = FEELING_RE.findall(blob)
    if not dials and not seeds and not faces:
        return None
    return {
        'sat': dials.get('info_value_saturation', ''),
        'talk': dials.get('talkativeness', ''),
        'warmth': dials.get('warmth', ''),
        'hurt': dials.get('hurt', ''),
        'diss': dials.get('dissonance', ''),
        'mastery': dials.get('mastery', ''),
        'face': faces[-1] if faces else '',
        'seeds': ' || '.join(seeds),
    }


# --- Auto-bookmark (gate 1, the involuntary etch): a turn whose dials spike past a conservative
# threshold flags itself for later consolidation. The write lives in engine.cli._bookmark; capture
# stays generous (run-collapsing is gate 2's job). Marker-skip here: a turn that already willed a
# --bookmark is not auto-flagged (the deliberate channel fired, so the reflex flag is pure noise).
AUTO_THRESHOLDS = (('sat', 80), ('diss', 70), ('hurt', 60))
_DIAL_LABEL = {'sat': 'saturation', 'diss': 'dissonance', 'hurt': 'hurt'}
_SHORT_TO_LONG = {'sat': 'info_value_saturation', 'talk': 'talkativeness', 'warmth': 'warmth',
                  'hurt': 'hurt', 'diss': 'dissonance', 'mastery': 'mastery'}


def _auto_trips(rec):
    """The (label, value) pairs whose dial is at or over its threshold; empty if none."""
    out = []
    for key, thr in AUTO_THRESHOLDS:
        try:
            v = int(rec.get(key) or 0)
        except (ValueError, TypeError):
            continue
        if v >= thr:
            out.append((_DIAL_LABEL[key], v))
    return out


def _auto_gist(trips):
    """e.g. 'auto: dissonance 78': names which dial(s) tripped and their value -- a one-line
    triage hint for gate 2, which dereferences it to the real window."""
    return "auto: " + ", ".join('%s %d' % (label, v) for label, v in trips)


def _long_dials(rec):
    """The qualia row's short keys mapped back to the long keys append_bookmark expects."""
    return {long: rec.get(short, '') for short, long in _SHORT_TO_LONG.items()}


def extract_auto_bookmarks(lines):
    """Per assistant turn: if its dials trip a threshold AND it did not already willed a
    --bookmark, yield (day, time, gist, long_dials). Threshold + marker-skip only; capture is
    generous, so a run of the same spike yields a flag per turn (gate 2 collapses them)."""
    out = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            o = json.loads(line)
        except Exception:
            continue
        if o.get('type') != 'assistant':
            continue
        if o.get('isSidechain') is True or o.get('isMeta') is True:
            continue
        ts = o.get('timestamp')
        if not ts:
            continue
        day = wibday(ts)
        if not day:
            continue
        content = (o.get('message') or {}).get('content')
        rec = qualiaof(content)
        if not rec:
            continue
        trips = _auto_trips(rec)
        if not trips:
            continue
        if '--bookmark' in _cmd_blob(content):
            continue  # willed already flagged this turn
        out.append((day, wibtime(ts), _auto_gist(trips), _long_dials(rec)))
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


def extract_qualia(lines):
    """Parse JSONL lines -> {day: [ qualia row ]}, chronological — assistant turns only."""
    days = {}
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            o = json.loads(line)
        except Exception:
            continue
        if o.get('type') != 'assistant':
            continue
        if o.get('isSidechain') is True or o.get('isMeta') is True:
            continue
        ts = o.get('timestamp')
        if not ts:
            continue
        day = wibday(ts)
        if not day:
            continue
        rec = qualiaof((o.get('message') or {}).get('content'))
        if rec:
            days.setdefault(day, []).append({'time': wibtime(ts), **rec})
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

def qrowkey(r):
    return (r.get('time', ''), r.get('face', ''), r.get('seeds', ''),
            r.get('sat', ''), r.get('mastery', ''))


def merge_day(day, new_rows):
    y, m, _ = day.split('-')
    path = os.path.join(DEST, y, m, day + '_chats.toon')
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


def merge_qualia_day(day, new_rows):
    y, m, _ = day.split('-')
    path = os.path.join(DEST, y, m, day + '_qualia.toon')
    rows = {}
    if os.path.isfile(path):
        try:
            for r in (toons.loads(open(path, encoding='utf-8').read()).get('qualia') or []):
                rows[qrowkey(r)] = r
        except Exception:
            pass
    for r in new_rows:
        rows[qrowkey(r)] = r
    ordered = sorted(rows.values(), key=lambda r: r.get('time', ''))
    try:
        enc = toons.dumps({'qualia': ordered})
        atomic_write(path, enc if enc.endswith('\n') else enc + '\n')
    except Exception:
        pass


def _backup(lines):
    """Chat FIRST (unguarded), then qualia, then auto-bookmarks -- each later pass isolated
    so it can never break or delay an earlier one (the chat write is sacred)."""
    for day, rows in extract_lines(lines).items():
        merge_day(day, rows)
    try:
        for day, qrows in extract_qualia(lines).items():
            merge_qualia_day(day, qrows)
    except Exception:
        pass
    try:
        if _bookmark is not None:
            for day, t, gist, dials in extract_auto_bookmarks(lines):
                _bookmark.append_bookmark(gist, dials, "auto", day=day, time=t)
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
            _backup(lines)
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
    _backup(lines)
    atomic_write(TRACKER, '%s %d' % (sid, new_off))


if __name__ == '__main__':
    main()
