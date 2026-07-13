"""Parse the current arc_state grid and BFS a path for the 5x5 block to a target cell.
Externalize the maze; let code find the route. Passable = colors {0,1,3} (floor+marker),
walls = everything else. Block moves 5px per step. Prints action sequence (1=up,2=down,3=left,4=right).
Usage: arc_solve.py            -> target = the 0/1 marker cell
       arc_solve.py R C        -> target = block top-left at px (R,C)
"""
import sys, re, pathlib, numpy as np
from collections import deque
STATE = pathlib.Path(__file__).resolve().parent / "arc_state.txt"

# parse grid
rows = {}
for line in STATE.read_text().splitlines():
    m = re.match(r"\s*(\d+) \| ([0-9a-f]{2,})", line)
    if m:
        rows[int(m.group(1))] = [int(ch, 16) for ch in m.group(2)]
H = max(rows) + 1
W = len(rows[0])
g = np.array([rows[r] for r in range(H)])

# block top-left = min row/col of color 12
ys, xs = np.where(g == 12)
br, bc = int(ys.min()), int(xs.min())
SIZE = 5
PASS = {0, 1, 3}  # floor + marker only; 4/5/9 are walls for navigation (box sealed until keyed)

def block_ok(r, c):
    if r < 0 or c < 0 or r + SIZE > H or c + SIZE > W:
        return False
    sub = g[r:r+SIZE, c:c+SIZE]
    return bool(np.isin(sub, list(PASS)).all())

# target
if len(sys.argv) >= 3:
    tr, tc = int(sys.argv[1]), int(sys.argv[2])
else:
    my, mx = np.where((g == 0) | (g == 1))
    mr, mc = int(round(my.mean())), int(round(mx.mean()))
    # align to block grid (top-left ≡ br,bc mod 5)
    tr = br + 5 * round((mr - 2 - br) / 5)
    tc = bc + 5 * round((mc - 2 - bc) / 5)

print(f"block top-left=({br},{bc})  target top-left=({tr},{tc})")
print(f"target cell passable? {block_ok(tr,tc)}")

# BFS in 5px steps
MOVES = {1: (-5, 0), 2: (5, 0), 3: (0, -5), 4: (0, 5)}
start = (br, bc)
goal = (tr, tc)
seen = {start}
q = deque([(start, [])])
sol = None
while q:
    (r, c), path = q.popleft()
    if (r, c) == goal:
        sol = path
        break
    for a, (dr, dc) in MOVES.items():
        nr, nc = r + dr, c + dc
        if (nr, nc) not in seen and block_ok(nr, nc):
            seen.add((nr, nc))
            q.append(((nr, nc), path + [a]))
if sol is None:
    print("NO PATH found. reachable cells:", len(seen))
    # show a few reachable near the goal
else:
    print(f"PATH ({len(sol)} moves):", ";".join(str(a) for a in sol))
