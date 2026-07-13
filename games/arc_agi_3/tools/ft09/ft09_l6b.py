"""FT09 L6 v2: plain tiles press self+above; glyphs inert. Component polarity
enumeration + per-column brute force over plain presses."""
import re, itertools, pathlib
from collections import defaultdict, deque

STATE = pathlib.Path(__file__).resolve().parent / "arc_state.txt"
lines = STATE.read_text().splitlines()
gi = next(i for i, l in enumerate(lines) if l.startswith("GRID"))
G = []
for l in lines[gi + 1:]:
    m = re.match(r"\s*(\d+) \| ([0-9a-f]{64})", l)
    if m:
        G.append([int(ch, 16) for ch in m.group(2)])

R0, C0 = 6, 4
tiles, info = {}, {}
for tr in range(8):
    for tc in range(8):
        r, c = R0 + 8 * tr, C0 + 8 * tc
        if r + 6 > 63 or c + 6 > 64:
            continue
        block = [[G[r + i][c + j] for j in range(6)] for i in range(6)]
        if any(v == 4 for row in block for v in row):
            continue
        p = [[block[i * 2][j * 2] for j in range(3)] for i in range(3)]
        tiles[(tr, tc)] = p
        flat = [v for row in p for v in row]
        info[(tr, tc)] = {"kind": "glyph" if any(v in (0, 2, 3) for v in flat) else "plain",
                          "color": p[1][1]}
A, B = 11, 14

adj = defaultdict(list)
for (tr, tc), d in info.items():
    if d["kind"] != "glyph":
        continue
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            if (di, dj) == (0, 0):
                continue
            cell = tiles[(tr, tc)][di + 1][dj + 1]
            nb = (tr + di, tc + dj)
            if cell in (0, 2) and nb in tiles:
                e = 0 if cell == 0 else 1
                adj[(tr, tc)].append((nb, e)); adj[nb].append(((tr, tc), e))

# components over constrained tiles
seen, comps = set(), []
for start in tiles:
    if start in seen or not adj[start]:
        continue
    comp = {start: 0}; dq = deque([start]); seen.add(start)
    while dq:
        u = dq.popleft()
        for v, e in adj[u]:
            w = comp[u] ^ e
            if v in comp:
                assert comp[v] == w, "inconsistent"
            else:
                comp[v] = w; seen.add(v); dq.append(v)
    comps.append(comp)
free = [pos for pos in tiles if pos not in seen]
print("components:", [sorted(c) for c in comps], "\nfree:", sorted(free))

cols = defaultdict(list)
for pos in tiles:
    cols[pos[1]].append(pos[0])

def solve(polarity):
    """polarity: tuple of flips per component -> full target; returns press set or None"""
    target = {}
    for comp, f in zip(comps, polarity):
        for pos, v in comp.items():
            target[pos] = A if (v ^ f) == 0 else B
    need = {pos: (target[pos] != info[pos]["color"]) if pos in target else None
            for pos in tiles}  # None = free
    presses = {}
    for tc, trs in cols.items():
        plains = [tr for tr in trs if info[(tr, tc)]["kind"] == "plain"]
        best = None
        for combo in itertools.product((0, 1), repeat=len(plains)):
            pr = dict(zip(plains, combo))
            ok = True
            for tr in trs:
                flip = pr.get(tr, 0) ^ (pr.get(tr + 1, 0) if (tr + 1, tc) in tiles else 0)
                want = need[(tr, tc)]
                if want is not None and flip != want:
                    ok = False; break
            if ok:
                cost = sum(combo)
                if best is None or cost < best[0]:
                    best = (cost, pr)
        if best is None:
            return None
        for tr, v in best[1].items():
            if v:
                presses[(tr, tc)] = 1
    return presses

best_plan = None
for polarity in itertools.product((0, 1), repeat=len(comps)):
    pl = solve(polarity)
    if pl is not None and (best_plan is None or len(pl) < len(best_plan)):
        best_plan = pl
assert best_plan is not None, "NO polarity feasible"
print("\nPRESS PLAN:")
for (tr, tc) in sorted(best_plan):
    print(f"  6 {C0 + 8 * tc + 2} {R0 + 8 * tr + 2}   # ({tr},{tc})")
print("total:", len(best_plan))
