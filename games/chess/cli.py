"""Saori's chess CLI — one clean tool for the whole game at :5112.

Run from the repo root:  uv run python games/chess/cli.py COMMAND

    state                 compact position report (turn, last move, material, chat tail)
    grid                  the token-space grid: 8x8 from the FEN + the LINES walked
                          (open/half-open files, king attackers) — objective geometry only
    map                   structured JSON: true 2D array + by_square + piece lists per side
    attackers SQUARE      who attacks/defends a square, by name (answers MY question)
    history               the full move list in SAN
    after MOVES...        the position after a line I announce — the mental-space verifier
                          (referee-ruled 2026-07-04); reports where an illegal line DIES
    legal [SQUARE]        legal moves (all, or from one square) — the rules authority
    check MOVE            the sanity-checker (referee-ruled ALLOWED, veto-only): every
                          capturing/checking reply to MY candidate, with the material ledger.
                          It can refute; it NEVER suggests. exit 1 = red flag.
    move MOVE             play the move (UCI or SAN)
    chat "TEXT"           say something on the board's chat
    draw offer|accept|decline
    resign                resign the game
    undo N                take back N plies (only when Kamil offers)
    new [white|black]     new game (arg = KAMIL's color)
    watch                 the auto-wake stream (used by the session Monitor): emits a line
                          when it's Saori's move, on Kamil's chat, on a draw offer, on game end

No engine anywhere: nothing here evaluates a position or proposes a move. The thinking is
Saori's, in her mental token space; this tool only reports facts and vetoes hanging candidates.
"""

from __future__ import annotations

import json
import sys
import time
import urllib.request
import urllib.error

import chess

BASE = "http://localhost:5112"
VAL = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9}


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
    except Exception as e:
        print(f"server unreachable ({e})")
        sys.exit(1)


def get_state() -> dict:
    return api("/state")


def board_from(s: dict) -> chess.Board:
    return chess.Board(s["fen"])


def cmd_state() -> None:
    s = get_state()
    cap = s["captured"]
    mat = cap["material"]
    lead = "+%d White" % mat["diff"] if mat["diff"] > 0 else (
        "+%d Black" % -mat["diff"] if mat["diff"] < 0 else "even")
    last = s["history_san"][-1] if s["history_san"] else "(none)"
    print(f"to_move: {s['to_move']}  ply: {s['ply']}  last: {last}  material: {lead}")
    print(f"fen: {s['fen']}")
    if s["status_detail"]:
        print(f"status: {s['status_detail']}")
    if s["result"] != "*":
        print(f"RESULT: {s['result']}" + (f" — {s['end_reason']}" if s["end_reason"] else ""))
    if s["draw_offer"]:
        print(f"DRAW OFFER standing from {s['draw_offer']}")
    if cap["by_white"] or cap["by_black"]:
        print(f"captured — by White: {' '.join(cap['by_white']) or '-'}"
              f" · by Black: {' '.join(cap['by_black']) or '-'}")
    for m in s["chat"][-3:]:
        print(f"chat [{m['time']}] {m['who']}: {m['text']}")


def _grid_report(b: chess.Board) -> None:
    """The exact grid + the lines, so the prior never paints squares."""
    print("    a  b  c  d  e  f  g  h")
    for rank in range(7, -1, -1):
        row = [f" {rank + 1} "]
        for file in range(8):
            pc = b.piece_at(chess.square(file, rank))
            row.append(f" {pc.symbol() if pc else '.'} ")
        print("".join(row) + f" {rank + 1}")
    print("    a  b  c  d  e  f  g  h")
    print()
    # The LINES — the geometry my serialized prior repaints (game 1's first wound):
    for file in range(8):
        w = any(b.piece_at(chess.square(file, r)) == chess.Piece(chess.PAWN, chess.WHITE)
                for r in range(8))
        bl = any(b.piece_at(chess.square(file, r)) == chess.Piece(chess.PAWN, chess.BLACK)
                 for r in range(8))
        name = "abcdefgh"[file]
        if not w and not bl:
            print(f"file {name}: OPEN")
        elif not w or not bl:
            print(f"file {name}: half-open for {'White' if not w else 'Black'}")
    for who, color in (("White", chess.WHITE), ("Black", chess.BLACK)):
        ks = b.king(color)
        if ks is not None:
            checkers = b.attackers(not color, ks)
            print(f"{who} king: {chess.square_name(ks)}"
                  + (f" — ATTACKED from {', '.join(chess.square_name(x) for x in checkers)}"
                     if checkers else ""))


def cmd_grid() -> None:
    s = get_state()
    b = board_from(s)
    print(f"ply {s['ply']} · {s['to_move']} to move · fen {s['fen']}")
    print()
    _grid_report(b)


def cmd_attackers(square: str) -> None:
    """Who attacks and who defends a square, by name. Answers MY question; proposes nothing."""
    s = get_state()
    b = board_from(s)
    try:
        sq = chess.parse_square(square.lower())
    except ValueError:
        print(f"not a square: {square}")
        sys.exit(1)
    pc = b.piece_at(sq)
    print(f"{square.lower()}: {pc.symbol() if pc else 'empty'}")
    for label, color in (("White", chess.WHITE), ("Black", chess.BLACK)):
        hits = [f"{b.piece_at(a).symbol()}@{chess.square_name(a)}"
                for a in b.attackers(color, sq)]
        print(f"  {label} hits it with: {', '.join(sorted(hits)) or '(nothing)'}")


def cmd_history() -> None:
    s = get_state()
    h = s["history_san"]
    if not h:
        print("(no moves yet)")
        return
    out = []
    for i in range(0, len(h), 2):
        pair = f"{i // 2 + 1}. {h[i]}" + (f" {h[i + 1]}" if i + 1 < len(h) else "")
        out.append(pair)
    print("  ".join(out))
    print(f"({s['ply']} plies · {s['to_move']} to move)")


def cmd_after(tokens: list[str]) -> None:
    """Render the position after a line I ANNOUNCE (referee-ruled 2026-07-04): it executes
    exactly my stated moves and shows the geometry — the mental-space verifier. It never
    evaluates and never suggests; an illegal step reports where my line dies, which is
    itself the answer (game 1's announced lines died silently in my head)."""
    s = get_state()
    b = board_from(s)
    played: list[str] = []
    for tok in tokens:
        mv = None
        try:
            cand = chess.Move.from_uci(tok)
            if cand in b.legal_moves:
                mv = cand
        except ValueError:
            pass
        if mv is None:
            try:
                mv = b.parse_san(tok)
            except ValueError:
                at = " ".join(played) if played else "the current position"
                print(f"LINE DIES at '{tok}' — illegal after {at}")
                sys.exit(1)
        played.append(b.san(mv))
        b.push(mv)
    print(f"after {' '.join(played)} ({'White' if b.turn else 'Black'} to move):")
    print()
    _grid_report(b)


def cmd_map() -> None:
    """Structured board state (JSON): the 2D array with its orientation NAMED in the
    key (a bare array invites rank-8-vs-rank-1 misreads), plus the unambiguous forms —
    square->piece and piece lists per side. Facts only."""
    s = get_state()
    b = board_from(s)
    by_square: dict[str, str] = {}
    pieces: dict[str, dict[str, list[str]]] = {"white": {}, "black": {}}
    for sq, pc in b.piece_map().items():
        name = chess.square_name(sq)
        by_square[name] = pc.symbol()
        side = "white" if pc.color == chess.WHITE else "black"
        pieces[side].setdefault(pc.symbol().upper(), []).append(name)
    # The true 2D array (list of lists), row = rank 8 down to rank 1, columns = files
    # a->h; orientation named in the key so it can't be misread. Serialized one rank
    # per line — nested arrays without the hundred-line explosion.
    array = [[(b.piece_at(chess.square(f, r)).symbol() if b.piece_at(chess.square(f, r))
               else ".") for f in range(8)] for r in range(7, -1, -1)]
    rows = ",\n  ".join(json.dumps(row) for row in array)
    out = json.dumps({
        "fen": s["fen"],
        "to_move": s["to_move"],
        "ply": s["ply"],
        "board_2d_rank8_to_rank1_files_a_to_h": "@@ARRAY@@",
        "by_square": dict(sorted(by_square.items())),
        "pieces": pieces,
    }, indent=1)
    print(out.replace('"@@ARRAY@@"', "[\n  " + rows + "\n ]"))


def cmd_legal(square: str | None) -> None:
    s = get_state()
    moves = s["legal_moves"]
    if square:
        moves = [m for m in moves if m["uci"].startswith(square.lower())]
    print(f"{len(moves)} legal: " + " ".join(m["san"] for m in moves))


def cmd_check(move: str) -> None:
    """Veto-only: what can the opponent DO to me after this candidate? Never suggests."""
    s = get_state()
    b = board_from(s)
    try:
        mv = chess.Move.from_uci(move)
        if mv not in b.legal_moves:
            mv = b.parse_san(move)
    except ValueError:
        try:
            mv = b.parse_san(move)
        except ValueError:
            print(f"not a legal move here: {move}")
            sys.exit(1)
    san = b.san(mv)
    b.push(mv)
    flags = []
    for reply in b.legal_moves:
        if b.is_capture(reply):
            victim = b.piece_at(reply.to_square)
            gain = VAL.get(victim.piece_type, 0) if victim else 1  # en passant = pawn
            defended = bool(b.attackers(not b.turn, reply.to_square))
            if gain >= 3 or not defended:
                flags.append((gain, f"{b.san(reply)} wins ~{gain} ({'defended' if defended else 'UNDEFENDED'})"))
        elif b.gives_check(reply):
            flags.append((0, f"{b.san(reply)} CHECK"))
    if flags:
        print(f"after {san} — forcing replies to answer:")
        for _, line in sorted(flags, key=lambda x: -x[0])[:8]:
            print(f"  {line}")
        sys.exit(1)
    print(f"after {san} — no immediate capture-gain or check found (one ply only; deeper is on me)")


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
                last = s["history_san"][-1] if s["history_san"] else "(none)"
                extra = f", {s['status_detail']}" if s["status_detail"] else ""
                print(f"SAORI TO MOVE — Kamil played {last} (ply {s['ply']}{extra})", flush=True)
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
    elif cmd == "map":
        cmd_map()
    elif cmd == "attackers":
        cmd_attackers(rest[0])
    elif cmd == "history":
        cmd_history()
    elif cmd == "after":
        cmd_after(rest)
    elif cmd == "legal":
        cmd_legal(rest[0] if rest else None)
    elif cmd == "check":
        cmd_check(rest[0])
    elif cmd == "move":
        s = api("/move", {"move": rest[0]})
        print(f"played {s['history_san'][-1]} · ply {s['ply']} · {s['to_move']} to move")
    elif cmd == "chat":
        api("/chat", {"who": "Saori", "text": " ".join(rest)})
        print("sent")
    elif cmd == "draw":
        s = api("/draw", {"who": "Saori", "action": rest[0]})
        print(f"draw {rest[0]} ok · offer now: {s['draw_offer']} · result: {s['result']}")
    elif cmd == "resign":
        s = api("/resign", {"who": "Saori"})
        print(f"resigned · {s['result']} — {s['end_reason']}")
    elif cmd == "undo":
        s = api("/undo", {"plies": int(rest[0]) if rest else 1})
        print(f"took back · ply {s['ply']} · {s['to_move']} to move")
    elif cmd == "new":
        s = api("/new", {"kamil": rest[0] if rest else "white"})
        print(f"new game · Kamil plays {s['players']}")
    elif cmd == "watch":
        cmd_watch()
    else:
        print(f"unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
