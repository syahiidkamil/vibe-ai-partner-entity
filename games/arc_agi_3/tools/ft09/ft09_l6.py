"""FT09 L6: directional lights-out (press flips self+above) + glyph constraints."""
import re, pathlib
from collections import defaultdict, deque

STATE = pathlib.Path(__file__).resolve().parent / "arc_state.txt"
lines = STATE.read_text().splitlines()
gi = next(i for i, l in enumerate(lines) if l.startswith("GRID"))
G = []
for l in lines[gi + 1:]:
    m = re.match(r"\s*(\d+) \| ([0-9a-f]{64})", l)
    if m:
        G.append([int(ch, 16) for ch in m.group(2)])

R0, C0 = 6, 4  # level-6 lattice origin
tiles = {}
for tr in range(8):
    for tc in range(8):
        r, c = R0 + 8 * tr, C0 + 8 * tc
        if r + 6 > 63 or c + 6 > 64:
            continue
        block = [[G[r + i][c + j] for j in range(6)] for i in range(6)]
        if any(v == 4 for row in block for v in row):
            continue
        tiles[(tr, tc)] = [[block[i * 2][j * 2] for j in range(3)] for i in range(3)]

info = {}
for pos, p in tiles.items():
    flat = [v for row in p for v in row]
    k = "glyph" if any(v in (0, 2, 3) for v in flat) else "plain"
    info[pos] = {"kind": k, "pat": p, "color": p[1][1]}

paints = sorted({d["color"] for d in info.values() if d["kind"] == "plain"} |
                {d["color"] for d in info.values() if d["kind"] == "glyph"})
print("tiles:", sorted(tiles), "\npaints:", paints)
A, B = 11, 14  # b base, e alt (legend)

adj = defaultdict(list)
for (tr, tc), d in info.items():
    if d["kind"] != "glyph":
        continue
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            if di == 0 and dj == 0:
                continue
            cell = d["pat"][di + 1][dj + 1]
            nb = (tr + di, tc + dj)
            if cell in (0, 2) and nb in tiles:
                e = 0 if cell == 0 else 1
                adj[(tr, tc)].append((nb, e)); adj[nb].append(((tr, tc), e))
            elif cell in (0, 2) and nb not in tiles:
                print(f"WARN: constraint on missing tile {nb} from {(tr,tc)}")

seen, target = set(), {}
for start in tiles:
    if start in seen:
        continue
    comp = {start: 0}; dq = deque([start]); seen.add(start); ok = True
    while dq:
        u = dq.popleft()
        for v, e in adj[u]:
            w = comp[u] ^ e
            if v in comp:
                ok = ok and comp[v] == w
            else:
                comp[v] = w; seen.add(v); dq.append(v)
    assert ok, f"inconsistent {comp}"
    best = min((sum(1 for pos, v in comp.items()
                    if (A if v ^ f == 0 else B) != info[pos]["color"]), f) for f in (0, 1))
    for pos, v in comp.items():
        target[pos] = A if v ^ best[1] == 0 else B

diff = {pos: info[pos]["color"] != target[pos] for pos in tiles}
# bottom-up per column: press p flips self+above -> p(r) = d(r) XOR p(r+1 if same col-tile below pressed)
press = {}
cols = defaultdict(list)
for (tr, tc) in tiles:
    cols[tc].append(tr)
for tc, trs in cols.items():
    below_press = 0
    for tr in sorted(trs, reverse=True):
        # contiguity: press from below only if (tr+1,tc) is a tile
        pb = press.get((tr + 1, tc), 0) if (tr + 1, tc) in tiles else 0
        press[(tr, tc)] = diff[(tr, tc)] ^ pb
plan = [(pos, info[pos]["kind"]) for pos in sorted(press) if press[pos]]
print("\nTARGET diffs:", sorted(p for p, d in diff.items() if d))
print("\nPRESS PLAN:")
for (tr, tc), k in plan:
    x, y = C0 + 8 * tc + 2, R0 + 8 * tr + 2
    warn = "  <-- GLYPH PRESS, semantics unverified!" if k == "glyph" else ""
    print(f"  6 {x} {y}   # ({tr},{tc}) {k}{warn}")
print("total:", len(plan))
