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

    @property
    def players(self) -> dict:
        white = "Kamil" if self.kamil_color == "white" else "Saori"
        black = "Saori" if white == "Kamil" else "Kamil"
        return {"white": white, "black": black}

    def status(self) -> tuple[str, str]:
        b = self.board
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

    def save_pgn(self) -> None:
        MATCHES.mkdir(parents=True, exist_ok=True)
        game = chess.pgn.Game()
        game.headers["Event"] = "Kamil vs Saori"
        game.headers["Site"] = "localhost:5112 — the first board"
        game.headers["Date"] = f"{self.started:%Y.%m.%d}"
        game.headers["White"] = self.players["white"]
        game.headers["Black"] = self.players["black"]
        game.headers["Result"] = self.board.result(claim_draw=True)
        node = game
        replay = chess.Board()
        for san in self.san_history:
            move = replay.parse_san(san)
            replay.push(move)
            node = node.add_variation(move)
        self.pgn_path.write_text(str(game) + "\n")


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
        "result": b.result(claim_draw=True) if status in ("checkmate", "stalemate", "draw") else "*",
        "check_square": chess.square_name(b.king(b.turn)) if b.is_check() else None,
        "pgn_file": str(game.pgn_path.relative_to(HERE)),
    }


class MoveIn(BaseModel):
    move: str


class NewIn(BaseModel):
    kamil: str = "white"


class UndoIn(BaseModel):
    plies: int = 1


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
        if game.status()[0] in ("checkmate", "stalemate", "draw"):
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
        n = max(1, min(body.plies, len(game.board.move_stack)))
        for _ in range(n):
            game.board.pop()
            game.san_history.pop()
        game.save_pgn()
        return state_dict()


# Cburnett piece set (Wikimedia Commons, CC BY-SA 3.0) lives in pieces/
app.mount("/pieces", StaticFiles(directory=str(HERE / "pieces")), name="pieces")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=PORT)
