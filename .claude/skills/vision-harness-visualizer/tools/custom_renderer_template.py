#!/usr/bin/env python3
"""TEMPLATE — a purpose-built renderer for a world the default grid tool can't draw
(entity maps, layouts, graphs, timelines, anything spatial that isn't a plain grid).

Copy this file next to render_state.py (or keep it here and import as shown), fill
in the layout section, and keep the contract identical to the default tool:

  1. read the EXACT state from a file/stdin — never from memory of it
  2. draw deterministically — same state, same pixels
  3. print the absolute PNG path on stdout so the caller can open and LOOK at it

Everything reusable (Canvas, save_png, PALETTE, color_for, luminance, the tiny
digit font) lives in render_state.py — no external dependencies anywhere.
"""

import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_state import BG, Canvas, color_for, luminance, save_png  # noqa: E402


def draw(state):
    """Lay the world out. Replace the example below with your world's geometry."""
    cv = Canvas(640, 400, fill=BG)

    # --- EXAMPLE: entities as colored boxes at (x, y, w, h) ------------------
    # for ent in state["entities"]:
    #     rgb = color_for(ent["kind"], {})
    #     cv.fill_rect(ent["x"], ent["y"], ent["w"], ent["h"], rgb)
    #
    # --- EXAMPLE: a link as a 2px straight line (axis-aligned) ---------------
    # cv.fill_rect(x0, y0, x1 - x0, 2, (255, 255, 255))
    #
    # --- EXAMPLE: mark a highlight the eye must not miss ---------------------
    # cv.ring(x, y, size, inset=2, thick=2, rgb=(255, 255, 255))
    # -------------------------------------------------------------------------

    return cv


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "-"
    raw = sys.stdin.read() if src == "-" else open(src).read()
    state = json.loads(raw)

    cv = draw(state)

    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        tempfile.gettempdir(), "custom_view.png")
    save_png(out, cv)
    print(f"RENDERED -> {os.path.abspath(out)}")


if __name__ == "__main__":
    main()
