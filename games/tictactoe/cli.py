"""Saori's vanishing tic-tac-toe CLI — one clean tool for the whole game at :5113.

Run from the repo root:  uv run python games/tictactoe/cli.py COMMAND

    state                 compact report (turn, last move, marks, vanish-next, chat tail)
    grid                  the token-space grid: 3x3 + each side's marks oldest-first,
                          what vanishes next, and the two-in-line threats BOTH ways —
                          objective geometry only
    legal                 the empty cells (the rules authority)
    check CELL            the sanity-checker (veto-only): plays MY candidate in simulation
                          (my oldest vanishing with it) and reports every immediate winning
                          reply the opponent has, each with its line. It can refute; it
                          NEVER suggests. exit 1 = red flag.
    move CELL             play the move (cells are a1..c3, rank 1 at the bottom)
    chat "TEXT"           say something on the board's chat
    draw offer|accept|decline
    resign                resign the game
    new [x|o]             new game (arg = KAMIL's mark; x always moves first)
    watch                 the auto-wake stream (used by the session Monitor): emits a line
                          when it's Saori's move, on Kamil's chat, on a draw offer, on game end

THE VANISHING RULE: 3 marks each, max. Placing a 4th removes my OLDEST in the same
instant — so every candidate is really two changes: a mark arriving AND a mark leaving.
No engine anywhere: nothing here evaluates or proposes. The thinking is Saori's, in her
mental token space; this tool only reports facts and vetoes hanging candidates.
"""
from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request

BASE = "http://localhost:5113"
CELLS = [c + r for r in "123" for c in "abc"]
LINES = [
    ("a1", "b1", "c1"), ("a2", "b2", "c2"), ("a3", "b3", "c3"),
    ("a1", "a2", "a3"), ("b1", "b2", "b3"), ("c1", "c2", "c3"),
    ("a1", "b2", "c3"), ("a3", "b2", "c1"),
]
MAX_MARKS = 3


def api(path: str, body: dict | None = None) -> dict:
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Content-Type": "application/json"},
        method="POST" if body is not None else "GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=3) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        try:
            detail = json.load(e).get("detail", "")
        except Exception:
            detail = ""
        print(f"API {e.code}: {detail}")
        sys.exit(1)
    except urllib.error.URLError:
        print(f"server unreachable at {BASE} — start it: uv run python games/tictactoe/server.py")
        sys.exit(1)


# ---------------------------------------------------------------- pure geometry helpers

def sim_move(marks: dict, mover: str, cell: str) -> tuple[dict, str | None]:
    """The vanishing rule in simulation: returns (new marks, what vanished)."""
    mine = list(marks[mover])
    vanished = mine.pop(0) if len(mine) >= MAX_MARKS else None
    mine.append(cell)
    out = {mover: mine, ("o" if mover == "x" else "x"): list(marks["o" if mover == "x" else "x"])}
    return out, vanished


def win_line(marks: dict, m: str) -> tuple[str, str, str] | None:
    owned = set(marks[m])
    for line in LINES:
        if all(c in owned for c in line):
            return line
    return None


def empties(marks: dict) -> list[str]:
    taken = set(marks["x"]) | set(marks["o"])
    return [c for c in CELLS if c not in taken]


def threats(marks: dict, m: str) -> list[tuple[str, tuple]]:
    """Lines where side m holds exactly two cells and the third is EMPTY (fact, not advice).
    NOTE: completing one still costs m's oldest mark if m already holds three — check that."""
    taken_other = set(marks["o" if m == "x" else "x"])
    owned = set(marks[m])
    out = []
    for line in LINES:
        have = [c for c in line if c in owned]
        rest = [c for c in line if c not in owned]
        if len(have) == 2 and rest[0] not in taken_other:
            out.append((rest[0], line))
    return out


# ------------------------------------------------------------------------- commands

def grid_lines(s: dict) -> list[str]:
    cells = s["cells"]
    out = [f"ply {s['ply']} · {s['to_move']} ({s['turn'].upper()}) to move"]
    out.append("    a  b  c")
    for r in "321":
        row = "  ".join((cells[c + r] or ".").upper() for c in "abc")
        out.append(f" {r}  {row}  {r}")
    van = s["vanishing_next"]
    for m in ("x", "o"):
        who = s["players"][m]
        lst = ", ".join(s["marks"][m]) or "(none)"
        nxt = f"   next to vanish: {van[m]}" if van[m] else ""
        out.append(f"{m.upper()} ({who}) oldest-first: {lst}{nxt}")
    marks = s["marks"]
    for m in ("x", "o"):
        th = threats(marks, m)
        if th:
            names = "; ".join(f"{cell} completes {'-'.join(line)}" for cell, line in th)
            out.append(f"{m.upper()} two-in-line: {names}")
    return out


def cmd_state() -> None:
    s = api("/state")
    last = s["history_str"][-1] if s["history_str"] else "(none)"
    print(f"to_move: {s['to_move']} ({s['turn'].upper()})  ply: {s['ply']}  last: {last}")
    van = s["vanishing_next"]
    print(f"marks X: {','.join(s['marks']['x']) or '-'}  O: {','.join(s['marks']['o']) or '-'}"
          f"  vanish-next X: {van['x'] or '-'}  O: {van['o'] or '-'}")
    if s["result"] != "*":
        print(f"GAME OVER: {s['result']} — {s['end_reason'] or s['status_detail']}")
    if s["draw_offer"]:
        print(f"draw offer standing from {s['draw_offer']}")
    for m in s["chat"][-3:]:
        print(f"  [{m['time']}] {m['who']}: {m['text']}")


def cmd_grid() -> None:
    s = api("/state")
    print("\n".join(grid_lines(s)))


def cmd_check(cell: str) -> None:
    s = api("/state")
    if s["result"] != "*":
        print("game is over")
        sys.exit(1)
    me = s["turn"]
    him = "o" if me == "x" else "x"
    cell = cell.strip().lower()
    if cell not in CELLS or s["cells"][cell]:
        print(f"illegal: {cell} is " + ("occupied" if cell in CELLS else "not a cell"))
        sys.exit(1)
    marks2, vanished = sim_move(s["marks"], me, cell)
    parts = [f"after {cell}" + (f" (my {vanished} vanishes with it)" if vanished else "")]
    mine = win_line(marks2, me)
    if mine:
        print(parts[0] + f" — this WINS: {'-'.join(mine)}")
        return
    flags = []
    for reply in empties(marks2):
        marks3, hv = sim_move(marks2, him, reply)
        line = win_line(marks3, him)
        if line:
            note = f" (his {hv} vanishes)" if hv else ""
            flags.append(f"his {reply} wins {'-'.join(line)}{note}")
    if flags:
        print(parts[0] + " — RED FLAG:")
        for f in flags:
            print(f"  {f}")
        sys.exit(1)
    print(parts[0] + " — no immediate winning reply for him (one ply only; deeper is on me)")


def cmd_watch() -> None:
    """The auto-wake stream: one line per event, deduplicated; runs forever."""
    prev: dict | None = None
    unreachable = False
    while True:
        try:
            with urllib.request.urlopen(BASE + "/state", timeout=2) as r:
                s = json.load(r)
            if unreachable:
                print("server back", flush=True)
                unreachable = False
        except Exception:
            if not unreachable:
                print("server unreachable", flush=True)
                unreachable = True
            prev = None
            time.sleep(2)
            continue
        if prev is not None:
            if s["result"] != "*" and prev["result"] == "*":
                reason = s["end_reason"] or s["status_detail"] or ""
                print(f"GAME OVER {s['result']} — {reason} (ply {s['ply']})", flush=True)
            elif s["to_move"] == "Saori" and s["ply"] != prev["ply"] and s["result"] == "*":
                last = s["history_str"][-1] if s["history_str"] else "(none)"
                print(f"SAORI TO MOVE — Kamil played {last} (ply {s['ply']})", flush=True)
            elif s["ply"] < prev["ply"]:
                print(f"NEW GAME — Kamil plays {s['players']}", flush=True)
            for m in s["chat"][len(prev["chat"]):]:
                if m["who"] == "Kamil":
                    print(f"KAMIL SAYS: {m['text']}", flush=True)
            if s["draw_offer"] == "Kamil" and prev["draw_offer"] != "Kamil":
                print("KAMIL OFFERS A DRAW — accept or decline (cli draw ...)", flush=True)
        else:
            if s["to_move"] == "Saori" and s["result"] == "*" and s["ply"] > 0:
                print(f"SAORI TO MOVE (ply {s['ply']})", flush=True)
        prev = s
        time.sleep(1)


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return
    cmd, rest = args[0], args[1:]
    if cmd == "state":
        cmd_state()
    elif cmd == "grid":
        cmd_grid()
    elif cmd == "legal":
        s = api("/state")
        print(" ".join(s["legal_moves"]) or "(game over)")
    elif cmd == "check":
        cmd_check(rest[0])
    elif cmd == "move":
        s = api("/move", {"cell": rest[0]})
        print(f"played {s['history_str'][-1]} · ply {s['ply']} · {s['to_move']} to move"
              + (f" · {s['status_detail']}" if s["status_detail"] else ""))
    elif cmd == "chat":
        api("/chat", {"who": "Saori", "text": " ".join(rest)})
        print("sent")
    elif cmd == "draw":
        s = api("/draw", {"who": "Saori", "action": rest[0]})
        print(f"draw {rest[0]} ok · offer now: {s['draw_offer']} · result: {s['result']}")
    elif cmd == "resign":
        s = api("/resign", {"who": "Saori"})
        print(f"resigned · {s['result']} — {s['end_reason']}")
    elif cmd == "new":
        s = api("/new", {"kamil": rest[0] if rest else "x"})
        print(f"new game · Kamil plays {s['players']}")
    elif cmd == "watch":
        cmd_watch()
    else:
        print(f"unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
