"""Chess on localhost — Kamil in the browser, Saori through the API.

Run from the repo root:
    uv run python games/chess/server.py

Board UI:      http://localhost:5112/
State (JSON):  GET  /state
Board (text):  GET  /board.txt
Move:          POST /move   {"move": "e2e4" | "Nf3"}
New game:      POST /new    {"kamil": "white" | "black"}
Takeback:      POST /undo   {"plies": 1}

One live game at a time. Every move autosaves the PGN under matches/, so a
crash never loses a game. No engine anywhere: the black (or white) pieces are
moved by Saori's own reading of the position.
"""
from __future__ import annotations

import threading
from datetime import datetime
from pathlib import Path

import chess
import chess.pgn
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

HERE = Path(__file__).parent
MATCHES = HERE / "matches"
PORT = 5112

app = FastAPI(title="kamil-vs-saori-chess")
_lock = threading.Lock()


class Game:
    def __init__(self, kamil_color: str = "white"):
        self.board = chess.Board()
        self.san_history: list[str] = []
        self.kamil_color = kamil_color  # "white" | "black"
        self.started = datetime.now()
        self.pgn_path = MATCHES / f"{self.started:%Y-%m-%d_%H%M%S}.pgn"
        self.chat: list[dict] = []            # {"who","text","time"} — the in-game channel
        self.draw_offer: str | None = None    # who has a draw offer standing ("Kamil"/"Saori")
        self.override: tuple[str, str] | None = None  # (result, reason): resignation/agreed draw

    @property
    def players(self) -> dict:
        white = "Kamil" if self.kamil_color == "white" else "Saori"
        black = "Saori" if white == "Kamil" else "Kamil"
        return {"white": white, "black": black}

    def status(self) -> tuple[str, str]:
        b = self.board
        if self.override:
            return "over", self.override[1]
        if b.is_checkmate():
            winner = self.players["black" if b.turn == chess.WHITE else "white"]
            return "checkmate", f"Checkmate — {winner} wins"
        if b.is_stalemate():
            return "stalemate", "Draw — stalemate"
        if b.is_insufficient_material():
            return "draw", "Draw — insufficient material"
        if b.can_claim_threefold_repetition():
            return "draw", "Draw — threefold repetition"
        if b.can_claim_fifty_moves():
            return "draw", "Draw — fifty-move rule"
        if b.is_check():
            return "check", f"{self.players['white' if b.turn == chess.WHITE else 'black']} is in check"
        return "playing", ""

    def result(self) -> str:
        if self.override:
            return self.override[0]
        return self.board.result(claim_draw=True)

    # Pieces each side has CAPTURED (missing from the enemy's starting set) and
    # the material score — promotion can make a count negative; clamp to 0.
    _START = {chess.PAWN: 8, chess.KNIGHT: 2, chess.BISHOP: 2, chess.ROOK: 2, chess.QUEEN: 1}
    _VAL = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9}
    _SYM = {chess.PAWN: "p", chess.KNIGHT: "n", chess.BISHOP: "b", chess.ROOK: "r", chess.QUEEN: "q"}

    def captured(self) -> dict:
        out = {"by_white": [], "by_black": []}
        score = {"white": 0, "black": 0}
        for color, key in ((chess.BLACK, "by_white"), (chess.WHITE, "by_black")):
            for pt in (chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT, chess.PAWN):
                missing = max(0, self._START[pt] - len(self.board.pieces(pt, color)))
                out[key] += [self._SYM[pt]] * missing
                score["white" if color == chess.BLACK else "black"] += missing * self._VAL[pt]
        return {**out, "material": {**score, "diff": score["white"] - score["black"]}}

    def save_pgn(self) -> None:
        MATCHES.mkdir(parents=True, exist_ok=True)
        game = chess.pgn.Game()
        game.headers["Event"] = "Kamil vs Saori"
        game.headers["Site"] = "localhost:5112 — the first board"
        game.headers["Date"] = f"{self.started:%Y.%m.%d}"
        game.headers["White"] = self.players["white"]
        game.headers["Black"] = self.players["black"]
        game.headers["Result"] = self.result()
        if self.override:
            game.headers["Termination"] = self.override[1]
        node = game
        replay = chess.Board()
        for san in self.san_history:
            move = replay.parse_san(san)
            replay.push(move)
            node = node.add_variation(move)
        self.pgn_path.write_text(str(game) + "\n", encoding="utf-8")


game = Game()


def state_dict() -> dict:
    b = game.board
    status, detail = game.status()
    legal = []
    for mv in b.legal_moves:
        legal.append({"uci": mv.uci(), "san": b.san(mv)})
    last = b.peek().uci() if b.move_stack else None
    replay = chess.Board()
    fens = [replay.fen()]          # fens[k] = position after k plies (for history browsing)
    ucis = []
    for mv in b.move_stack:
        ucis.append(mv.uci())
        replay.push(mv)
        fens.append(replay.fen())
    return {
        "fens": fens,
        "history_uci": ucis,
        "fen": b.fen(),
        "turn": "white" if b.turn == chess.WHITE else "black",
        "to_move": game.players["white" if b.turn == chess.WHITE else "black"],
        "ply": len(b.move_stack),
        "players": game.players,
        "history_san": game.san_history,
        "legal_moves": legal,
        "last_move": last,
        "status": status,
        "status_detail": detail,
        "result": game.result() if status in ("checkmate", "stalemate", "draw", "over") else "*",
        "check_square": chess.square_name(b.king(b.turn)) if b.is_check() else None,
        "pgn_file": str(game.pgn_path.relative_to(HERE)),
        "captured": game.captured(),
        "chat": game.chat[-200:],
        "draw_offer": game.draw_offer,
        "end_reason": game.override[1] if game.override else None,
    }


class MoveIn(BaseModel):
    move: str


class NewIn(BaseModel):
    kamil: str = "white"


class UndoIn(BaseModel):
    plies: int = 1


class WhoIn(BaseModel):
    who: str  # "Kamil" | "Saori"


class DrawIn(BaseModel):
    who: str
    action: str  # offer | accept | decline


class ChatIn(BaseModel):
    who: str
    text: str


def _check_who(who: str) -> str:
    if who not in ("Kamil", "Saori"):
        raise HTTPException(400, "who must be 'Kamil' or 'Saori'")
    return who


GAME_OVER_STATES = ("checkmate", "stalemate", "draw", "over")


@app.get("/")
def index():
    return FileResponse(HERE / "index.html")


@app.get("/state")
def state():
    with _lock:
        return state_dict()


@app.get("/board.txt", response_class=PlainTextResponse)
def board_txt():
    with _lock:
        b = game.board
        status, detail = game.status()
        lines = [
            f"{game.players['white']} (White) vs {game.players['black']} (Black)",
            "",
            str(b),
            "",
            f"to move: {state_dict()['to_move']}  ply: {len(b.move_stack)}  {detail}",
            f"fen: {b.fen()}",
        ]
        return "\n".join(lines)


@app.post("/move")
def move(body: MoveIn):
    with _lock:
        b = game.board
        if game.status()[0] in GAME_OVER_STATES:
            raise HTTPException(409, "game is over — POST /new to start another")
        raw = body.move.strip()
        mv = None
        try:
            mv = chess.Move.from_uci(raw)
            if mv not in b.legal_moves:
                mv = None
        except ValueError:
            mv = None
        if mv is None:
            try:
                mv = b.parse_san(raw)
            except ValueError:
                raise HTTPException(400, f"illegal or unparseable move: {raw!r}")
        san = b.san(mv)
        b.push(mv)
        game.san_history.append(san)
        game.draw_offer = None  # making a move declines any standing offer
        game.save_pgn()
        return state_dict()


@app.post("/new")
def new_game(body: NewIn):
    global game
    if body.kamil not in ("white", "black"):
        raise HTTPException(400, "kamil must be 'white' or 'black'")
    with _lock:
        if game.san_history:
            game.save_pgn()  # finalize the old one where it stands
        game = Game(kamil_color=body.kamil)
        return state_dict()


@app.post("/undo")
def undo(body: UndoIn):
    with _lock:
        if not game.board.move_stack:
            raise HTTPException(400, "nothing to take back — the board is at the start")
        n = max(1, min(body.plies, len(game.board.move_stack)))
        for _ in range(n):
            game.board.pop()
            game.san_history.pop()
        game.override = None      # a takeback reopens a resigned/agreed game
        game.draw_offer = None
        game.save_pgn()
        return state_dict()


@app.post("/resign")
def resign(body: WhoIn):
    with _lock:
        who = _check_who(body.who)
        if game.status()[0] in GAME_OVER_STATES:
            raise HTTPException(409, "game is already over")
        result = "0-1" if game.players["white"] == who else "1-0"
        game.override = (result, f"{who} resigns")
        game.draw_offer = None
        game.save_pgn()
        return state_dict()


@app.post("/draw")
def draw(body: DrawIn):
    with _lock:
        who = _check_who(body.who)
        if game.status()[0] in GAME_OVER_STATES:
            raise HTTPException(409, "game is already over")
        if body.action == "offer":
            game.draw_offer = who
        elif body.action == "accept":
            if not game.draw_offer or game.draw_offer == who:
                raise HTTPException(409, "no draw offer from the other side to accept")
            game.override = ("1/2-1/2", "Draw agreed")
            game.draw_offer = None
            game.save_pgn()
        elif body.action == "decline":
            if not game.draw_offer or game.draw_offer == who:
                raise HTTPException(409, "no draw offer from the other side to decline")
            game.draw_offer = None
        else:
            raise HTTPException(400, "action must be offer, accept, or decline")
        return state_dict()


@app.post("/chat")
def chat(body: ChatIn):
    with _lock:
        who = _check_who(body.who)
        text = body.text.strip()
        if not text:
            raise HTTPException(400, "empty message")
        game.chat.append({"who": who, "text": text[:500], "time": f"{datetime.now():%H:%M}"})
        return state_dict()


# Cburnett piece set (Wikimedia Commons, CC BY-SA 3.0) lives in pieces/
app.mount("/pieces", StaticFiles(directory=str(HERE / "pieces")), name="pieces")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=PORT)
