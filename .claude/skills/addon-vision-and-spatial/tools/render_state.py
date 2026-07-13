#!/usr/bin/env python3
"""Render structured harness state (grids / boards / frames) to a PNG for visual
inspection. Pure standard library — no pip installs, runs on any Python 3.8+.

Built for machine vision consumers: high-contrast cells, thick gridlines, a hard
black border around every panel, and 0-based coordinate rulers (row down, column
right) drawn by default — because index-mapping and thin lines are exactly where
multimodal reads slip.

Input JSON shapes accepted:
  [[0,1],[2,3]]                       one 2D grid (ints, strings, floats, null)
  [[[...]],[[...]]]                   several grids -> side-by-side panels
  {"grid": [[...]]}                   one grid, wrapped
  {"grids": [...], "palette": {...},  several grids + optional value->"#rrggbb"
   "title": "..."}                    palette override and a title (printed)

Usage:
  python3 render_state.py STATE.json [-o OUT.png] [--cell N] [--gap N]
                          [--labels] [--no-coords] [--diff PREV.json]
                          [--palette JSON]
  echo '[[0,1],[1,0]]' | python3 render_state.py - -o /tmp/view.png

Prints the absolute PNG path and a value->color legend to stdout.
The image shows the gestalt; exact coordinates and counts stay in code.
"""

import argparse
import hashlib
import json
import os
import struct
import sys
import tempfile
import zlib

# 16 distinct default colors; ints 0-15 map here directly, everything else hashes.
PALETTE = [
    (0x00, 0x00, 0x00), (0x00, 0x74, 0xD9), (0xFF, 0x41, 0x36), (0x2E, 0xCC, 0x40),
    (0xFF, 0xDC, 0x00), (0xAA, 0xAA, 0xAA), (0xF0, 0x12, 0xBE), (0xFF, 0x85, 0x1B),
    (0x7F, 0xDB, 0xFF), (0x87, 0x0C, 0x25), (0xFF, 0xFF, 0xFF), (0x39, 0xCC, 0xCC),
    (0xB1, 0x0D, 0xC9), (0x01, 0xFF, 0x70), (0x85, 0x14, 0x4B), (0x3D, 0x99, 0x70),
]
BG = (0x7F, 0x7F, 0x7F)  # mid-grey background/gridlines: black AND white cells stay visible

# 3x5 bitmap font (rows top->bottom, 3 bits each, MSB = left) for labels/rulers.
FONT = {
    "0": [0b111, 0b101, 0b101, 0b101, 0b111],
    "1": [0b010, 0b110, 0b010, 0b010, 0b111],
    "2": [0b111, 0b001, 0b111, 0b100, 0b111],
    "3": [0b111, 0b001, 0b111, 0b001, 0b111],
    "4": [0b101, 0b101, 0b111, 0b001, 0b001],
    "5": [0b111, 0b100, 0b111, 0b001, 0b111],
    "6": [0b111, 0b100, 0b111, 0b101, 0b111],
    "7": [0b111, 0b001, 0b010, 0b010, 0b010],
    "8": [0b111, 0b101, 0b111, 0b101, 0b111],
    "9": [0b111, 0b101, 0b111, 0b001, 0b111],
    "-": [0b000, 0b000, 0b111, 0b000, 0b000],
    ".": [0b000, 0b000, 0b000, 0b000, 0b010],
}


class Canvas:
    def __init__(self, w, h, fill=BG):
        self.w, self.h = w, h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, fill)

    def fill_rect(self, x, y, w, h, rgb):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(rgb) * (x1 - x0)
        for yy in range(y0, y1):
            off = (yy * self.w + x0) * 3
            self.px[off:off + (x1 - x0) * 3] = row

    def ring(self, x, y, size, inset, thick, rgb):
        """Hollow square outline inside a cell (used for diff highlighting)."""
        s = size - 2 * inset
        if s <= 2 * thick:
            self.fill_rect(x + inset, y + inset, max(1, s), max(1, s), rgb)
            return
        self.fill_rect(x + inset, y + inset, s, thick, rgb)
        self.fill_rect(x + inset, y + inset + s - thick, s, thick, rgb)
        self.fill_rect(x + inset, y + inset, thick, s, rgb)
        self.fill_rect(x + inset + s - thick, y + inset, thick, s, rgb)

    def text(self, x, y, s, scale, rgb):
        cx = x
        for ch in s:
            glyph = FONT.get(ch)
            if glyph:
                for gy, bits in enumerate(glyph):
                    for gx in range(3):
                        if bits & (0b100 >> gx):
                            self.fill_rect(cx + gx * scale, y + gy * scale, scale, scale, rgb)
            cx += 4 * scale  # 3px glyph + 1px space


def text_shadow(cv, x, y, s, scale, fg=(255, 255, 255)):
    """Text readable on any background: black shadow under white glyphs."""
    cv.text(x + 1, y + 1, s, scale, (0, 0, 0))
    cv.text(x, y, s, scale, fg)


def text_width(s, scale):
    return 4 * scale * len(s) - scale if s else 0


def save_png(path, canvas):
    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))
    w, h = canvas.w, canvas.h
    raw = b"".join(b"\x00" + bytes(canvas.px[y * w * 3:(y + 1) * w * 3]) for y in range(h))
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n"
                + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
                + chunk(b"IDAT", zlib.compress(raw, 9))
                + chunk(b"IEND", b""))


def luminance(rgb):
    r, g, b = rgb
    return 0.299 * r + 0.587 * g + 0.114 * b


def color_for(value, palette_override):
    key = str(value)
    if key in palette_override:
        hexs = palette_override[key].lstrip("#")
        return tuple(int(hexs[i:i + 2], 16) for i in (0, 2, 4))
    if value is None:
        return BG
    if isinstance(value, bool):
        value = int(value)
    if isinstance(value, int) and 0 <= value < len(PALETTE):
        return PALETTE[value]
    d = hashlib.md5(key.encode()).digest()  # stable color for any other value
    r, g, b = d[0], d[1], d[2]
    if abs(luminance((r, g, b)) - luminance(BG)) < 40:  # keep it apart from the background
        b ^= 0x80
    return (r, g, b)


def normalize(data):
    """Return (grids, palette_override, title). Grids are lists of 2D row-lists."""
    palette, title = {}, None
    if isinstance(data, dict):
        palette = {str(k): v for k, v in (data.get("palette") or {}).items()}
        title = data.get("title")
        grids = data.get("grids") or data.get("frames")
        if grids is None and "grid" in data:
            grids = [data["grid"]]
        if grids is None:
            raise ValueError("dict input needs a 'grid', 'grids', or 'frames' key")
    elif isinstance(data, list) and data:
        is_3d = isinstance(data[0], list) and data[0] and isinstance(data[0][0], list)
        grids = data if is_3d else [data]
    else:
        raise ValueError("input must be a 2D grid, a list of grids, or a wrapping dict")
    out = []
    for g in grids:
        if not (isinstance(g, list) and g and isinstance(g[0], list)):
            raise ValueError("each grid must be a non-empty list of rows")
        width = max(len(r) for r in g)
        out.append([list(r) + [None] * (width - len(r)) for r in g])
    return out, palette, title


def render(grids, palette, cell, gap, labels, diff_grids, coords):
    margin, spacing, border = 10, 16, 2
    cscale = max(1, min(3, cell // 12)) if coords else 0
    ruler_h = (5 * cscale + 6) if coords else 0

    def ruler_w(g):
        return (text_width(str(len(g) - 1), cscale) + 6) if coords else 0

    panel_ws = [len(g[0]) * (cell + gap) + gap for g in grids]
    panel_hs = [len(g) * (cell + gap) + gap for g in grids]
    W = (2 * margin + sum(panel_ws) + sum(ruler_w(g) for g in grids)
         + 2 * border * len(grids) + spacing * (len(grids) - 1))
    H = 2 * margin + ruler_h + 2 * border + max(panel_hs)
    cv = Canvas(W, H)
    legend = {}

    ox = margin
    oy = margin + ruler_h + border
    for gi, g in enumerate(grids):
        h, w = len(g), len(g[0])
        pw, ph = panel_ws[gi], panel_hs[gi]
        ox += ruler_w(g) + border
        cv.fill_rect(ox - border, oy - border, pw + 2 * border, ph + 2 * border, (0, 0, 0))
        cv.fill_rect(ox, oy, pw, ph, BG)

        prev = diff_grids[gi] if diff_grids and gi < len(diff_grids) else None
        for y, row in enumerate(g):
            for x, v in enumerate(row):
                rgb = color_for(v, palette)
                legend.setdefault(str(v), rgb)
                px = ox + gap + x * (cell + gap)
                py = oy + gap + y * (cell + gap)
                cv.fill_rect(px, py, cell, cell, rgb)
                changed = (prev is not None
                           and (y >= len(prev) or x >= len(prev[y]) or prev[y][x] != v))
                if changed:
                    t = max(1, cell // 10)
                    cv.ring(px, py, cell, t, t, (255, 255, 255))
                    cv.ring(px, py, cell, 2 * t, t, (0, 0, 0))
                if labels and v is not None:
                    s = str(v)
                    if all(ch in FONT for ch in s):
                        scale = max(1, cell // 10)
                        tw = text_width(s, scale)
                        while tw > cell - 2 and scale > 1:
                            scale -= 1
                            tw = text_width(s, scale)
                        if tw <= cell - 2:
                            fg = (0, 0, 0) if luminance(rgb) > 128 else (255, 255, 255)
                            cv.text(px + (cell - tw) // 2, py + (cell - 5 * scale) // 2, s, scale, fg)

        if coords:  # 0-based rulers: columns across the top, rows down the left
            col_lw = text_width(str(w - 1), cscale)
            col_step = max(1, -(-(col_lw + 3) // (cell + gap)))
            for x in range(0, w, col_step):
                s = str(x)
                tx = ox + gap + x * (cell + gap) + (cell - text_width(s, cscale)) // 2
                text_shadow(cv, tx, oy - border - 5 * cscale - 3, s, cscale)
            row_step = max(1, -(-(5 * cscale + 3) // (cell + gap)))
            for y in range(0, h, row_step):
                s = str(y)
                tx = ox - border - text_width(s, cscale) - 3
                ty = oy + gap + y * (cell + gap) + (cell - 5 * cscale) // 2
                text_shadow(cv, tx, ty, s, cscale)

        ox += pw + border + spacing
    return cv, legend


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="path to JSON state, or '-' for stdin")
    ap.add_argument("-o", "--out", help="output PNG path (default: system temp dir)")
    ap.add_argument("--cell", type=int, help="cell size in px (default: auto)")
    ap.add_argument("--gap", type=int, help="gridline thickness (default: auto, >=2)")
    ap.add_argument("--labels", action="store_true", help="draw numeric values in cells")
    ap.add_argument("--no-coords", action="store_true", help="drop the row/col index rulers")
    ap.add_argument("--diff", help="previous-state JSON; changed cells get a ring")
    ap.add_argument("--palette", help='inline palette JSON, e.g. \'{"1":"#ff0000"}\'')
    args = ap.parse_args()

    raw = sys.stdin.read() if args.input == "-" else open(args.input).read()
    grids, palette, title = normalize(json.loads(raw))
    if args.palette:
        palette.update({str(k): v for k, v in json.loads(args.palette).items()})

    diff_grids = None
    if args.diff:
        diff_grids, _, _ = normalize(json.loads(open(args.diff).read()))

    if args.cell:
        cell = args.cell
    else:
        span = max(max(len(g) for g in grids), sum(len(g[0]) for g in grids))
        cell = max(6, min(48, 1100 // max(1, span)))
    gap = args.gap if args.gap is not None else max(2, cell // 10)

    cv, legend = render(grids, palette, cell, gap, args.labels, diff_grids,
                        coords=not args.no_coords)

    if args.out:
        out = os.path.abspath(args.out)
    else:
        stem = "state" if args.input == "-" else os.path.splitext(os.path.basename(args.input))[0]
        out = os.path.join(tempfile.gettempdir(), stem + "_view.png")
    save_png(out, cv)

    if title:
        print(f"title: {title}")
    sizes = " ".join(f"{len(g)}x{len(g[0])}" for g in grids)
    print(f"RENDERED -> {out}")
    print(f"panels={len(grids)} grids={sizes} cell={cell}px gap={gap}px image={cv.w}x{cv.h}")
    print("legend: " + "  ".join(
        f"{k}=#{r:02X}{g:02X}{b:02X}" for k, (r, g, b) in sorted(legend.items())))


if __name__ == "__main__":
    main()
