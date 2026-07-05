"""Vanishing tic-tac-toe on localhost — Kamil in the browser, Saori through the API.

Run from the repo root:
    uv run python games/tictactoe/server.py

Board UI:      http://localhost:5113/
State (JSON):  GET  /state
Move:          POST /move   {"cell": "b2"}
New game:      POST /new    {"kamil": "x" | "o"}

THE VANISHING RULE: each player keeps at most 3 marks on the board. Placing a
4th removes that player's OLDEST mark in the same instant. Three surviving
marks in a row win. The board can never fill, so there is no stalemate — a
game ends by a line, a resignation, or an agreed draw.

One live game at a time. Every move autosaves the match record under
matches/, so a crash never loses a game. No engine anywhere: the other side's
marks are placed by Saori's own reading of the board.
"""
from __future__ import annotations

import json
import threading
from datetime import datetime
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

HERE = Path(__file__).parent
MATCHES = HERE / "matches"
PORT = 5113

CELLS = [c + r for r in "123" for c in "abc"]  # a1..c3, rank 1 at the bottom (chess-like)
LINES = [
    ("a1", "b1", "c1"), ("a2", "b2", "c2"), ("a3", "b3", "c3"),  # rows
    ("a1", "a2", "a3"), ("b1", "b2", "b3"), ("c1", "c2", "c3"),  # columns
    ("a1", "b2", "c3"), ("a3", "b2", "c1"),                      # diagonals
]
MAX_MARKS = 3

app = FastAPI(title="kamil-vs-saori-tictactoe")
_lock = threading.Lock()


class Game:
    def __init__(self, kamil_mark: str = "x"):
        self.marks: dict[str, list[str]] = {"x": [], "o": []}  # oldest first
        self.history: list[dict] = []  # {"who","mark","cell","vanished"}
        self.turn = "x"                # x always moves first
        self.kamil_mark = kamil_mark   # "x" | "o"
        self.started = datetime.now()
        self.match_path = MATCHES / f"{self.started:%Y-%m-%d_%H%M%S}.json"
        self.chat: list[dict] = []            # {"who","text","time"}
        self.draw_offer: str | None = None    # "Kamil" | "Saori" | None
        self.override: tuple[str, str] | None = None  # (result, reason)

    @property
    def players(self) -> dict:
        x = "Kamil" if self.kamil_mark == "x" else "Saori"
        return {"x": x, "o": "Saori" if x == "Kamil" else "Kamil"}

    def cell_owner(self, cell: str) -> str | None:
        for m in ("x", "o"):
            if cell in self.marks[m]:
                return m
        return None

    def winner_mark(self) -> str | None:
        for m in ("x", "o"):
            owned = set(self.marks[m])
            if any(all(c in owned for c in line) for line in LINES):
                return m
        return None

    def winning_line(self, m: str) -> tuple[str, str, str] | None:
        owned = set(self.marks[m])
        for line in LINES:
            if all(c in owned for c in line):
                return line
        return None

    def vanishing_next(self) -> dict:
        """Per mark: the cell that leaves if that player places again (their oldest)."""
        return {m: (self.marks[m][0] if len(self.marks[m]) >= MAX_MARKS else None)
                for m in ("x", "o")}

    def status(self) -> tuple[str, str]:
        if self.override:
            return "over", self.override[1]
        w = self.winner_mark()
        if w:
            line = self.winning_line(w)
            return "win", f"{self.players[w]} wins — {'-'.join(line)}"
        return "playing", ""

    def result(self) -> str:
        if self.override:
            return self.override[0]
        w = self.winner_mark()
        return self.players[w] if w else "*"

    def play(self, cell: str) -> None:
        if cell not in CELLS:
            raise HTTPException(400, f"no such cell: {cell!r} (cells are a1..c3)")
        if self.cell_owner(cell):
            raise HTTPException(400, f"{cell} is occupied")
        mover = self.turn
        vanished = None
        if len(self.marks[mover]) >= MAX_MARKS:
            vanished = self.marks[mover].pop(0)
        self.marks[mover].append(cell)
        self.history.append({"who": self.players[mover], "mark": mover,
                             "cell": cell, "vanished": vanished})
        self.turn = "o" if mover == "x" else "x"
        self.draw_offer = None  # making a move declines any standing offer
        self.save()

    def save(self) -> None:
        MATCHES.mkdir(parents=True, exist_ok=True)
        record = {
            "event": "Kamil vs Saori — vanishing tic-tac-toe",
            "site": f"localhost:{PORT}",
            "date": f"{self.started:%Y-%m-%d %H:%M:%S}",
            "players": self.players,
            "result": self.result(),
            "termination": self.override[1] if self.override else self.status()[1],
            "moves": self.history,
        }
        self.match_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")


game = Game()


def history_str(h: dict) -> str:
    return h["cell"] + (f" -{h['vanished']}" if h["vanished"] else "")


def state_dict() -> dict:
    status, detail = game.status()
    over = status in ("win", "over")
    empty = [c for c in CELLS if game.cell_owner(c) is None]
    win_line = None
    w = game.winner_mark()
    if w:
        win_line = list(game.winning_line(w))
    return {
        "cells": {c: game.cell_owner(c) for c in CELLS},
        "marks": game.marks,  # oldest first, per side
        "turn": game.turn,
        "to_move": game.players[game.turn],
        "ply": len(game.history),
        "players": game.players,
        "history": game.history,
        "history_str": [history_str(h) for h in game.history],
        "legal_moves": [] if over else empty,
        "vanishing_next": game.vanishing_next(),
        "last": game.history[-1] if game.history else None,
        "status": status,
        "status_detail": detail,
        "result": game.result() if over else "*",
        "win_line": win_line,
        "chat": game.chat[-200:],
        "draw_offer": game.draw_offer,
        "end_reason": game.override[1] if game.override else (detail if over else None),
        "match_file": str(game.match_path.relative_to(HERE)),
    }


class MoveIn(BaseModel):
    cell: str


class NewIn(BaseModel):
    kamil: str = "x"


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


@app.get("/")
def index():
    return FileResponse(HERE / "index.html")


@app.get("/state")
def state():
    with _lock:
        return state_dict()


@app.post("/move")
def move(body: MoveIn):
    with _lock:
        if game.status()[0] in ("win", "over"):
            raise HTTPException(409, "game is over — POST /new to start another")
        game.play(body.cell.strip().lower())
        return state_dict()


@app.post("/new")
def new_game(body: NewIn):
    global game
    if body.kamil not in ("x", "o"):
        raise HTTPException(400, "kamil must be 'x' or 'o'")
    with _lock:
        if game.history:
            game.save()  # finalize the old one where it stands
        game = Game(kamil_mark=body.kamil)
        return state_dict()


@app.post("/resign")
def resign(body: WhoIn):
    with _lock:
        who = _check_who(body.who)
        if game.status()[0] in ("win", "over"):
            raise HTTPException(409, "game is already over")
        winner = "Saori" if who == "Kamil" else "Kamil"
        game.override = (winner, f"{who} resigns")
        game.draw_offer = None
        game.save()
        return state_dict()


@app.post("/draw")
def draw(body: DrawIn):
    with _lock:
        who = _check_who(body.who)
        if game.status()[0] in ("win", "over"):
            raise HTTPException(409, "game is already over")
        if body.action == "offer":
            game.draw_offer = who
        elif body.action == "accept":
            if not game.draw_offer or game.draw_offer == who:
                raise HTTPException(409, "no draw offer from the other side to accept")
            game.override = ("draw", "Draw agreed")
            game.draw_offer = None
            game.save()
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


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=PORT)
