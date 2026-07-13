#!/usr/bin/env -S uv run --quiet
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "opencv-python-headless>=4.10,<5",
#   "numpy>=1.26",
# ]
# ///
"""perceive.py — the inverse of render_state.py: pixels -> structure.

Where render_state.py turns exact state into an image to LOOK at, this turns an
image back into structure to CHECK. Its output is a HYPOTHESIS about the image,
never ground truth — verify it (--verify on `grid`, or overlay + look).

Subcommands (every one writes PNG artifacts for the eyes AND JSON for exact
checks, and prints every output path on stdout):

  info    IMG                       size, color count, route suggestion
  edges   IMG                       auto-threshold Canny edge map
  shapes  IMG                       contours -> polygons/circles, labeled overlay
  objects IMG                       color blobs (connected components), overlay
  grid    IMG [--verify]            reconstruct a cell grid as render_state JSON
  crop    IMG --box x,y,w,h         zoomed crop (machine eyes read zoomed better)
  crop    IMG --tiles RxC           split a big screenshot into overlapping tiles
  imgdiff A B                       what changed between two same-size images

Run with uv so the dependencies self-install (isolated, cached after first run):
  uv run .claude/skills/addon-vision-and-spatial/tools/perceive.py info shot.png
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def die(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(2)


def load_bgr(path):
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:
        die(f"cannot read image: {path}")
    h, w = img.shape[:2]
    print(f"image: {w}x{h}  ({os.path.abspath(path)})")
    return img


def stroke_for(img):
    """Overlay strokes must survive downscaled viewing of big screenshots."""
    return max(2, min(img.shape[:2]) // 400)


def out_path(args, stem, suffix, ext=".png"):
    base = os.path.abspath(args.outdir) if args.outdir else tempfile.gettempdir()
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, f"{stem}_{suffix}{ext}")


def stem_of(path):
    return os.path.splitext(os.path.basename(path))[0]


def save(path, img, label="PNG"):
    cv2.imwrite(path, img)
    print(f"{label} -> {path}")


def write_json(path, obj, label="JSON"):
    with open(path, "w") as f:
        json.dump(obj, f, indent=1)
    print(f"{label} -> {path}")


def hex_of_bgr(bgr):
    b, g, r = int(bgr[0]), int(bgr[1]), int(bgr[2])
    return f"#{r:02x}{g:02x}{b:02x}"


def auto_canny(gray, sigma=0.33):
    v = float(np.median(gray))
    lo = int(max(0, (1.0 - sigma) * v))
    hi = int(min(255, (1.0 + sigma) * v))
    if hi <= lo:
        lo, hi = 50, 150
    return cv2.Canny(gray, lo, hi)


def put_label(img, text, x, y):
    """Index label readable on any background: black outline, green fill.
    Scales with image size so labels survive downscaled viewing."""
    fs = max(0.5, min(1.6, min(img.shape[:2]) / 700))
    for thick, color in ((max(3, int(3 * fs)), (0, 0, 0)), (max(1, int(1.4 * fs)), (80, 255, 80))):
        cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, fs, color, thick, cv2.LINE_AA)


# ---------------------------------------------------------------- info

def unique_colors(img, cap=4096):
    h, w = img.shape[:2]
    step = max(1, int((h * w / 200_000) ** 0.5))
    sample = img[::step, ::step].reshape(-1, 3)
    colors = np.unique(sample, axis=0)
    return len(colors) if len(colors) < cap else cap


def cmd_info(args):
    img = load_bgr(args.image)
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ncolors = unique_colors(img)
    edge_density = float(auto_canny(gray).mean() / 255.0)
    xb, yb, conf = estimate_lattice(img)
    print(f"size: {w}x{h}  unique_colors(sampled): {ncolors}"
          f"{'+' if ncolors >= 4096 else ''}  edge_density: {edge_density:.3f}")
    lattice = "none found"
    if conf > 0 and len(xb) > 1 and len(yb) > 1:
        pitch = min((xb[-1] - xb[0]) / (len(xb) - 1), (yb[-1] - yb[0]) / (len(yb) - 1))
        if pitch >= 6 and conf >= 0.55:
            lattice = (f"{len(yb) - 1}x{len(xb) - 1} cells, ~{pitch:.0f}px pitch, "
                       f"confidence {conf:.2f}")
        else:
            lattice = "none (periodicity is texture-fine or weak — not a board)"
    print(f"lattice: {lattice}")
    if ncolors < 256:
        route = "synthetic/screen-like -> grid (if lattice holds), objects, shapes"
    else:
        route = "natural-photo-like -> edges/shapes for structure, crop for detail, detect.py for object classes"
    print(f"route: {route}")


# ---------------------------------------------------------------- edges

def cmd_edges(args):
    img = load_bgr(args.image)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = auto_canny(gray, args.sigma)
    save(out_path(args, stem_of(args.image), "edges"), edges, "EDGES")
    overlay = (img * 0.35).astype(np.uint8)
    overlay[edges > 0] = (80, 255, 80)
    save(out_path(args, stem_of(args.image), "edges_overlay"), overlay, "OVERLAY")
    print(f"edge_density: {edges.mean() / 255.0:.3f}")


# ---------------------------------------------------------------- shapes

def classify_shape(approx, contour):
    v = len(approx)
    area = cv2.contourArea(contour)
    peri = cv2.arcLength(contour, True)
    circ = 4 * np.pi * area / (peri * peri) if peri > 0 else 0
    if v == 3:
        return "triangle"
    if v == 4:
        x, y, w, h = cv2.boundingRect(approx)
        return "square" if 0.9 <= w / max(1, h) <= 1.1 else "rectangle"
    if v <= 6:
        return f"polygon-{v}"
    return "circle" if circ >= 0.80 else f"blob-{v}v"


def cmd_shapes(args):
    img = load_bgr(args.image)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = auto_canny(gray, args.sigma)
    edges = cv2.dilate(edges, np.ones((3, 3), np.uint8))
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    min_area = args.min_area or max(16, img.shape[0] * img.shape[1] // 20_000)
    shapes, overlay = [], img.copy()
    for c in contours:
        if cv2.contourArea(c) < min_area:
            continue
        approx = cv2.approxPolyDP(c, 0.02 * cv2.arcLength(c, True), True)
        x, y, w, h = cv2.boundingRect(c)
        m = cv2.moments(c)
        cx = int(m["m10"] / m["m00"]) if m["m00"] else x + w // 2
        cy = int(m["m01"] / m["m00"]) if m["m00"] else y + h // 2
        i = len(shapes)
        shapes.append({"id": i, "shape": classify_shape(approx, c),
                       "vertices": len(approx), "bbox": [x, y, w, h],
                       "centroid": [cx, cy], "area": int(cv2.contourArea(c))})
        cv2.drawContours(overlay, [c], -1, (80, 255, 80), stroke_for(overlay))
        put_label(overlay, str(i), x, max(12, y - 4))
    shapes.sort(key=lambda s: -s["area"])
    save(out_path(args, stem_of(args.image), "shapes"), overlay, "OVERLAY")
    write_json(out_path(args, stem_of(args.image), "shapes", ".json"), shapes)
    print(f"shapes: {len(shapes)}")
    for s in shapes[:12]:
        print(f"  #{s['id']} {s['shape']} bbox={s['bbox']} area={s['area']}")
    if len(shapes) > 12:
        print(f"  ... {len(shapes) - 12} more in the JSON")


# ---------------------------------------------------------------- objects

def border_mode_color(q):
    border = np.concatenate([q[0], q[-1], q[:, 0], q[:, -1]])
    colors, counts = np.unique(border, axis=0, return_counts=True)
    return colors[counts.argmax()]


def cmd_objects(args):
    img = load_bgr(args.image)
    step = args.qstep
    q = (img.astype(np.int32) // step) * step + step // 2
    q = q.astype(np.uint8)
    bg = border_mode_color(q)
    colors, counts = np.unique(q.reshape(-1, 3), axis=0, return_counts=True)
    min_area = args.min_area or max(12, img.shape[0] * img.shape[1] // 50_000)
    keep = [(c, n) for c, n in zip(colors, counts)
            if n >= min_area and not np.array_equal(c, bg)]
    keep.sort(key=lambda t: -t[1])
    if len(keep) > 40:
        print(f"note: {len(keep)} candidate colors; keeping the 40 largest "
              f"(natural photo? prefer edges/shapes or detect.py)")
        keep = keep[:40]
    blobs, overlay = [], img.copy()
    for color, _ in keep:
        mask = np.all(q == color, axis=2).astype(np.uint8)
        n, _, stats, cents = cv2.connectedComponentsWithStats(mask, 8)
        for i in range(1, n):
            x, y, w, h, area = stats[i]
            if area < min_area:
                continue
            region = img[y:y + h, x:x + w]
            blobs.append({"id": 0, "color": hex_of_bgr(np.median(region.reshape(-1, 3), axis=0)),
                          "bbox": [int(x), int(y), int(w), int(h)],
                          "centroid": [int(cents[i][0]), int(cents[i][1])], "area": int(area)})
    blobs.sort(key=lambda b: -b["area"])
    if len(blobs) > args.max_blobs:
        print(f"note: {len(blobs)} blobs, keeping largest {args.max_blobs}")
        blobs = blobs[:args.max_blobs]
    for i, b in enumerate(blobs):
        b["id"] = i
        x, y, w, h = b["bbox"]
        cv2.rectangle(overlay, (x, y), (x + w, y + h), (80, 255, 80), stroke_for(overlay))
        put_label(overlay, str(i), x, max(12, y - 4))
    save(out_path(args, stem_of(args.image), "objects"), overlay, "OVERLAY")
    write_json(out_path(args, stem_of(args.image), "objects", ".json"),
               {"background": hex_of_bgr(bg), "blobs": blobs})
    print(f"background: {hex_of_bgr(bg)}  blobs: {len(blobs)}")
    for b in blobs[:12]:
        print(f"  #{b['id']} {b['color']} bbox={b['bbox']} area={b['area']}")
    if len(blobs) > 12:
        print(f"  ... {len(blobs) - 12} more in the JSON")


# ---------------------------------------------------------------- grid

def content_box(img, tol=8):
    """Trim near-uniform margins (solid borders, letterboxing)."""
    bg = border_mode_color(img)
    diff = np.abs(img.astype(np.int32) - bg.astype(np.int32)).max(axis=2)
    ys, xs = np.where(diff > tol)
    if len(xs) == 0:
        return 0, 0, img.shape[1], img.shape[0]
    return int(xs.min()), int(ys.min()), int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)


def peaks_1d(profile, min_dist):
    thr = profile.mean() + profile.std()
    idx = []
    for i in range(1, len(profile) - 1):
        if profile[i] >= thr and profile[i] >= profile[i - 1] and profile[i] >= profile[i + 1]:
            if idx and i - idx[-1] < min_dist:
                if profile[i] > profile[idx[-1]]:
                    idx[-1] = i
            else:
                idx.append(i)
    return idx


def lattice_1d(profile, span):
    """Gridline positions along one axis -> (boundaries, confidence)."""
    if span < 8:
        return None, 0.0
    p = cv2.GaussianBlur(profile.astype(np.float32).reshape(-1, 1), (1, 5), 0).ravel()
    idx = peaks_1d(p, min_dist=3)
    # a thick gridline band puts a peak on EACH edge; merge near-pairs to its center
    groups = []
    for i in idx:
        if groups and i - groups[-1][-1] <= 5:
            groups[-1].append(i)
        else:
            groups.append([i])
    idx = [int(round(sum(g) / len(g))) for g in groups]
    if len(idx) >= 3:
        d = np.diff(idx)
        pitch = float(np.median(d))
        if pitch >= 3:
            reg = 1.0 - float(np.std(d)) / pitch
            if reg > 0.55:
                # snap to arithmetic progression covering the span
                start = idx[0]
                n = max(1, round((idx[-1] - idx[0]) / pitch))
                pitch = (idx[-1] - idx[0]) / n
                bounds = [start + k * pitch for k in range(n + 1)]
                # extend outward if cells continue past outermost gridlines
                while bounds[0] - pitch >= -pitch * 0.3:
                    bounds.insert(0, bounds[0] - pitch)
                while bounds[-1] + pitch <= span - 1 + pitch * 0.3:
                    bounds.append(bounds[-1] + pitch)
                bounds = [b for b in bounds if -2 <= b <= span + 1]
                return [max(0.0, min(float(span), b)) for b in bounds], max(0.0, min(1.0, reg))
    # autocorrelation fallback: find the dominant period
    pc = p - p.mean()
    if len(pc) < 16:
        return None, 0.0
    ac = np.correlate(pc, pc, "full")[len(pc) - 1:]
    lo = 4
    hi = max(lo + 1, len(pc) // 2)
    if hi <= lo:
        return None, 0.0
    lag = int(np.argmax(ac[lo:hi])) + lo
    if ac[lag] <= 0 or ac[0] <= 0:
        return None, 0.0
    conf = float(ac[lag] / ac[0]) * 0.8  # discount: period found, phase less sure
    phase = int(np.argmax(p[:lag])) if lag > 0 else 0
    bounds = list(np.arange(phase, span + 1, lag, dtype=float))
    if len(bounds) < 2:
        return None, 0.0
    return bounds, max(0.0, min(1.0, conf))


def estimate_lattice(img, box=None):
    """-> (x_bounds, y_bounds, confidence); bounds in full-image coordinates."""
    if box:
        x0, y0, bw, bh = box
    else:
        x0, y0, bw, bh = content_box(img)
    roi = img[y0:y0 + bh, x0:x0 + bw]
    if roi.size == 0:
        return [], [], 0.0
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    gx = np.abs(cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)).sum(axis=0)
    gy = np.abs(cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)).sum(axis=1)
    xb, cx = lattice_1d(gx, bw)
    yb, cy = lattice_1d(gy, bh)
    if not xb or not yb or len(xb) < 2 or len(yb) < 2:
        return [], [], 0.0
    return [x0 + b for b in xb], [y0 + b for b in yb], min(cx, cy)


def sample_grid(img, xb, yb, inset=0.25):
    """Median color of each cell's central region -> (rows of BGR tuples,
    list of [r,c] 'content cells' whose interior varies — a piece standing on
    a square, an icon on a tile: there the dominant color is the FLOOR only."""
    cells, hot = [], []
    for r in range(len(yb) - 1):
        row = []
        for c in range(len(xb) - 1):
            x0, x1 = xb[c], xb[c + 1]
            y0, y1 = yb[r], yb[r + 1]
            dx, dy = (x1 - x0) * inset, (y1 - y0) * inset
            xa, xz = int(round(x0 + dx)), int(round(x1 - dx))
            ya, yz = int(round(y0 + dy)), int(round(y1 - dy))
            xz, yz = max(xa + 1, xz), max(ya + 1, yz)
            region = img[ya:yz, xa:xz].reshape(-1, 3)
            row.append(tuple(int(v) for v in np.median(region, axis=0)))
            if float(region.std(axis=0).max()) > 28:
                hot.append([r, c])
        cells.append(row)
    return cells, hot


def colors_to_ids(cells, tol=12):
    """Cluster near-identical cell colors -> int grid + id->hex palette.
    ids ordered by frequency (0 = most common, usually background)."""
    flat = [c for row in cells for c in row]
    freq = {}
    for c in flat:
        freq[c] = freq.get(c, 0) + 1
    clusters = []  # (representative, count)
    for color, n in sorted(freq.items(), key=lambda t: -t[1]):
        for i, (rep, cnt) in enumerate(clusters):
            if max(abs(a - b) for a, b in zip(color, rep)) <= tol:
                clusters[i] = (rep, cnt + n)
                break
        else:
            clusters.append((color, n))
    clusters.sort(key=lambda t: -t[1])
    def id_of(color):
        for i, (rep, _) in enumerate(clusters):
            if max(abs(a - b) for a, b in zip(color, rep)) <= tol:
                return i
        return 0
    grid = [[id_of(c) for c in row] for row in cells]
    palette = {str(i): hex_of_bgr(rep) for i, (rep, _) in enumerate(clusters)}
    return grid, palette


def canon(grid):
    """Rename values by first appearance so two id-permuted grids compare equal."""
    m, out = {}, []
    for row in grid:
        r = []
        for v in row:
            if v not in m:
                m[v] = len(m)
            r.append(m[v])
        out.append(r)
    return out


def perceive_grid(img, args, box=None):
    if box is None:
        box = find_board_quad(img)  # stage 1: find the board, then divide it
    if args.rows and args.cols:
        x0, y0, bw, bh = box or content_box(img)
        xb = list(np.linspace(x0, x0 + bw, args.cols + 1))
        yb = list(np.linspace(y0, y0 + bh, args.rows + 1))
        conf = 1.0  # user-asserted dimensions: the reliable path
    else:
        xb, yb, conf = estimate_lattice(img, box)
        if conf < 0.55 or len(xb) < 2 or len(yb) < 2:
            die("lattice confidence too low — not a regular grid, or too much "
                "chrome around it. Pass --rows R --cols C when you know the "
                "board (the reliable path), and/or --box x,y,w,h to isolate it.")
    cells, hot = sample_grid(img, xb, yb)
    grid, palette = colors_to_ids(cells, tol=args.tol)
    if not (args.rows and args.cols):
        # a photo will happily fake a lattice; three independent smells refuse it
        problems = []
        pitch = min((xb[-1] - xb[0]) / max(1, len(xb) - 1),
                    (yb[-1] - yb[0]) / max(1, len(yb) - 1))
        if pitch < 6:
            problems.append(f"cell pitch {pitch:.1f}px — too fine to be a real board")
        if len(palette) > 24:
            problems.append(f"{len(palette)} colors after merging — photo-like, not a flat grid")
        if problems:
            die("this doesn't perceive as a regular grid: " + "; ".join(problems)
                + ". If it IS a grid, pass --rows R --cols C (and --box); "
                "otherwise use edges/shapes/objects/crop instead.")
    return grid, palette, xb, yb, conf, hot


def cmd_grid(args):
    img = load_bgr(args.image)
    box = parse_box(args.box, img.shape) if args.box else None
    grid, palette, xb, yb, conf, hot = perceive_grid(img, args, box)
    rows, cols = len(grid), len(grid[0]) if grid else 0
    state = {"grid": grid, "palette": palette,
             "meta": {"source": os.path.abspath(args.image), "rows": rows, "cols": cols,
                      "confidence": round(conf, 3), "content_cells": hot,
                      "cell_px": [round((xb[-1] - xb[0]) / max(1, cols), 1),
                                  round((yb[-1] - yb[0]) / max(1, rows), 1)]}}
    jpath = out_path(args, stem_of(args.image), "grid", ".json")
    write_json(jpath, state, "STATE")
    print(f"grid: {rows}x{cols}  confidence: {conf:.2f}")
    print("palette: " + "  ".join(f"{k}={v}" for k, v in palette.items()))
    if hot:
        print(f"content cells (interior detail; dominant color = floor only): "
              f"{len(hot)} -> {hot[:8]}{'...' if len(hot) > 8 else ''}  "
              f"(crop them to see what stands on the floor)")
    # the fidelity check: the detected lattice drawn ON THE SOURCE — look here
    lat = img.copy()
    t = stroke_for(lat)
    y0i, y1i = int(round(yb[0])), int(round(yb[-1]))
    x0i, x1i = int(round(xb[0])), int(round(xb[-1]))
    for b in xb:
        cv2.line(lat, (int(round(b)), y0i), (int(round(b)), y1i), (80, 255, 80), t)
    for b in yb:
        cv2.line(lat, (x0i, int(round(b))), (x1i, int(round(b))), (80, 255, 80), t)
    save(out_path(args, stem_of(args.image), "grid_lattice"), lat, "LATTICE OVERLAY")
    print("  ^ LOOK at the overlay: do the green lines sit on the real cell "
          "boundaries? A shifted lattice self-verifies but is still wrong.")
    # and the reconstruction, to compare against the source by eye
    render = os.path.join(HERE, "render_state.py")
    rpath = out_path(args, stem_of(args.image), "grid_view")
    r = subprocess.run([sys.executable, render, jpath, "--no-coords", "-o", rpath],
                       capture_output=True, text=True)
    if r.returncode == 0:
        print(f"RECONSTRUCTION -> {rpath}   (LOOK at this next to the source image)")
    else:
        print(f"note: preview render failed: {r.stderr.strip()[:200]}")
    if args.verify:
        if r.returncode != 0:
            die("cannot verify: preview render failed")
        grid2, _, _, _, _, _ = perceive_grid(load_bgr(rpath), args, None)
        a, b = canon(grid), canon(grid2)
        if a == b:
            print("VERIFY: OK — re-perceiving the reconstruction reproduces the same grid")
        else:
            mism = [(r_, c_) for r_ in range(min(len(a), len(b)))
                    for c_ in range(min(len(a[0]), len(b[0]))) if a[r_][c_] != b[r_][c_]]
            print(f"VERIFY: MISMATCH — dims {len(a)}x{len(a[0])} vs {len(b)}x{len(b[0])}, "
                  f"{len(mism)} differing cells: {mism[:10]}")
            print("the reconstruction is unstable — treat the state JSON as suspect")


# ---------------------------------------------------------------- crop

def parse_box(s, shape):
    """x,y,w,h — plain ints are pixels; values all <= 1.0 are fractions of the
    image (the safe form when coordinates were read off a downscaled view)."""
    try:
        vals = [float(v) for v in s.split(",")]
        assert len(vals) == 4
    except (ValueError, AssertionError):
        die(f"--box wants x,y,w,h (pixels, or 0-1 fractions), got: {s}")
    H, W = shape[:2]
    if all(v <= 1.0 for v in vals):
        x, y, w, h = vals[0] * W, vals[1] * H, vals[2] * W, vals[3] * H
    else:
        x, y, w, h = vals
    return int(round(x)), int(round(y)), int(round(w)), int(round(h))


def find_board_quad(img):
    """Largest rectangle-ish high-contrast region -> (x,y,w,h), or None.
    Stage 1 of grid perception: find the board, then divide it."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.dilate(auto_canny(gray), np.ones((3, 3), np.uint8))
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    H, W = img.shape[:2]
    best = None
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if w * h < 0.15 * W * H:
            continue
        if cv2.contourArea(c) / max(1, w * h) < 0.75:  # not rectangle-ish
            continue
        if best is None or w * h > best[2] * best[3]:
            best = (x, y, w, h)
    return best


def cmd_crop(args):
    img = load_bgr(args.image)
    H, W = img.shape[:2]
    if args.tiles:
        try:
            rt, ct = (int(v) for v in args.tiles.lower().split("x"))
        except ValueError:
            die(f"--tiles wants RxC, e.g. 2x3, got: {args.tiles}")
        oh, ow = int(H / rt * 0.1), int(W / ct * 0.1)  # 10% overlap
        for r in range(rt):
            for c in range(ct):
                y0 = max(0, H * r // rt - oh)
                y1 = min(H, H * (r + 1) // rt + oh)
                x0 = max(0, W * c // ct - ow)
                x1 = min(W, W * (c + 1) // ct + ow)
                save(out_path(args, stem_of(args.image), f"tile_r{r}c{c}"),
                     img[y0:y1, x0:x1], f"TILE r{r}c{c} (x{x0} y{y0})")
        return
    if not args.box:
        die("crop needs --box x,y,w,h or --tiles RxC")
    x, y, w, h = parse_box(args.box, img.shape)
    x, y = max(0, x), max(0, y)
    region = img[y:min(H, y + h), x:min(W, x + w)]
    if region.size == 0:
        die(f"--box {args.box} is outside the {W}x{H} image")
    scale = args.scale or max(1, min(16, 700 // max(region.shape[0], region.shape[1])))
    zoomed = cv2.resize(region, None, fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST)
    save(out_path(args, stem_of(args.image), f"crop_{x}_{y}"), zoomed, f"CROP x{scale}")


# ---------------------------------------------------------------- imgdiff

def cmd_imgdiff(args):
    a, b = load_bgr(args.image), load_bgr(args.image_b)
    if a.shape != b.shape:
        die(f"images differ in size: {a.shape[1]}x{a.shape[0]} vs {b.shape[1]}x{b.shape[0]} "
            "— diff needs same-size captures")
    d = cv2.absdiff(a, b).max(axis=2)
    d = cv2.GaussianBlur(d, (3, 3), 0)
    _, mask = cv2.threshold(d, args.thr, 255, cv2.THRESH_BINARY)
    # open kills 1px anti-aliasing/cursor jitter before dilate merges real regions
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    mask = cv2.dilate(mask, np.ones((5, 5), np.uint8))
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    min_area = args.min_area or 8
    regions, overlay = [], b.copy()
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if w * h < min_area:
            continue
        regions.append({"id": len(regions), "bbox": [x, y, w, h]})
        cv2.rectangle(overlay, (x, y), (x + w, y + h), (80, 255, 80), stroke_for(overlay))
        put_label(overlay, str(len(regions) - 1), x, max(12, y - 4))
    pct = 100.0 * float((mask > 0).sum()) / mask.size
    save(out_path(args, stem_of(args.image_b), "diff"), overlay, "OVERLAY")
    write_json(out_path(args, stem_of(args.image_b), "diff", ".json"),
               {"changed_pct": round(pct, 3), "regions": regions})
    print(f"changed: {pct:.2f}% of pixels, {len(regions)} regions")
    for reg in regions[:12]:
        print(f"  #{reg['id']} bbox={reg['bbox']}")
    # zoomed crops of the changed spots — a thin box on a big screenshot
    # disappears when the image is viewed downscaled; these don't
    H, W = b.shape[:2]
    for reg in regions[:8]:
        x, y, w, h = reg["bbox"]
        pad = 12
        crop = b[max(0, y - pad):min(H, y + h + pad), max(0, x - pad):min(W, x + w + pad)]
        sc = max(1, min(8, 400 // max(1, crop.shape[0], crop.shape[1])))
        if sc > 1:
            crop = cv2.resize(crop, None, fx=sc, fy=sc, interpolation=cv2.INTER_NEAREST)
        save(out_path(args, stem_of(args.image_b), f"diffregion{reg['id']}"),
             crop, f"REGION {reg['id']} zoom")


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--outdir", help="directory for outputs (default: system temp)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("info", help="size, colors, route suggestion")
    p.add_argument("image")

    p = sub.add_parser("edges", help="auto-threshold Canny edge map")
    p.add_argument("image")
    p.add_argument("--sigma", type=float, default=0.33)

    p = sub.add_parser("shapes", help="contour polygons/circles + overlay")
    p.add_argument("image")
    p.add_argument("--sigma", type=float, default=0.33)
    p.add_argument("--min-area", type=int, dest="min_area")

    p = sub.add_parser("objects", help="color blobs + overlay")
    p.add_argument("image")
    p.add_argument("--qstep", type=int, default=24, help="color quantization step")
    p.add_argument("--min-area", type=int, dest="min_area")
    p.add_argument("--max-blobs", type=int, default=200, dest="max_blobs")

    p = sub.add_parser("grid", help="reconstruct a cell grid -> render_state JSON")
    p.add_argument("image")
    p.add_argument("--box", help="x,y,w,h holding the grid (pixels, or 0-1 fractions)")
    p.add_argument("--rows", type=int, help="assert row count (with --cols)")
    p.add_argument("--cols", type=int, help="assert column count (with --rows)")
    p.add_argument("--tol", type=int, default=12, help="color-merge tolerance")
    p.add_argument("--verify", action="store_true",
                   help="re-perceive the reconstruction; report mismatches")

    p = sub.add_parser("crop", help="zoomed crop or tiles for close reading")
    p.add_argument("image")
    p.add_argument("--box", help="x,y,w,h (pixels, or 0-1 fractions of the image)")
    p.add_argument("--scale", type=int, help="zoom factor (default: auto)")
    p.add_argument("--tiles", help="RxC overlapping tiles of the whole image")

    p = sub.add_parser("imgdiff", help="changed regions between two images")
    p.add_argument("image")
    p.add_argument("image_b")
    p.add_argument("--thr", type=int, default=25)
    p.add_argument("--min-area", type=int, dest="min_area")

    args = ap.parse_args()
    {"info": cmd_info, "edges": cmd_edges, "shapes": cmd_shapes,
     "objects": cmd_objects, "grid": cmd_grid, "crop": cmd_crop,
     "imgdiff": cmd_imgdiff}[args.cmd](args)


if __name__ == "__main__":
    main()
