"""Persistent ARC-AGI-3 play session. Keeps ONE env (one guid) alive, driven by a
command file, writing a rendered state file after each action. Externalize-the-state:
I read the rendered artifact, never a grid held in my head."""
import sys, os, time, json, pathlib, numpy as np

HERE = pathlib.Path(__file__).parent
GAME = sys.argv[1] if len(sys.argv) > 1 else "ls20-9607627b"
# Per-game runtime dir: state/log/frames live beside that game's solvers (modular),
# and .active_run at root tells arc_send.py where the live session writes.
RUN = HERE / "tools" / GAME.split("-")[0]
RUN.mkdir(parents=True, exist_ok=True)
(HERE / ".active_run").write_text(str(RUN.relative_to(HERE)))
CMD = RUN / "arc_cmd.txt"
STATE = RUN / "arc_state.txt"
LOG = RUN / "arc_log.jsonl"
FRAMES = RUN / "arc_frames.txt"

key = None
for envfile in (HERE / ".env", HERE.parents[1] / "vape" / ".env"):
    try:
        for line in envfile.read_text().splitlines():
            if line.startswith("ARC_API_KEY=") and line.split("=", 1)[1].strip():
                key = line.split("=", 1)[1].strip()
        if key:
            break
    except FileNotFoundError:
        continue

import arc_agi
from arcengine.enums import GameAction

# Mode (argv[2], default online). ONLINE: server-side sim, scorecard recorded at
# arcprize.org/scorecards/{id}, replay shareable, no game-source files (answer keys) on disk.
# NORMAL: downloads the game and simulates LOCALLY — scorecard local-only, never on the server
# (practice mode). OFFLINE: local-only with files already on disk, no key.
MODE = {"online": arc_agi.OperationMode.ONLINE, "normal": arc_agi.OperationMode.NORMAL,
        "offline": arc_agi.OperationMode.OFFLINE}[sys.argv[2] if len(sys.argv) > 2 else "online"]
arc = arc_agi.Arcade(arc_api_key=key,
                     operation_mode=MODE,
                     environments_dir=str(HERE / "environment_files"),
                     recordings_dir=str(HERE / "recordings"))
sc = arc.open_scorecard(tags=["vibe-ai-parnter-entity-saori-play"])
env = arc.make(GAME, scorecard_id=sc)

ACT = {"1": GameAction.ACTION1, "2": GameAction.ACTION2, "3": GameAction.ACTION3,
       "4": GameAction.ACTION4, "5": GameAction.ACTION5, "7": GameAction.ACTION7,
       "RESET": GameAction.RESET}

def grids(fr):
    f = getattr(fr, "frame", None)
    if f is None:
        f = getattr(fr, "_frame", None)
    if f is None:
        return []  # terminal/score frames can carry no grid; state still readable
    return [np.array(g) for g in f]

def render(a):
    w = a.shape[1]
    tens = "     " + "".join(str((c // 10) % 10) if c % 10 == 0 else " " for c in range(w))
    ones = "     " + "".join(str(c % 10) for c in range(w))
    out = [tens, ones]
    for r in range(a.shape[0]):
        row = "".join(format(int(v), "x") if 0 <= int(v) < 16 else "?" for v in a[r])
        out.append(f"{r:>3} | {row}")
    return "\n".join(out)

def features(a):
    """Exact-coordinate readout so I never parse the grid by eye (board-vision guard)."""
    lines = []
    # color counts
    vals, cnts = np.unique(a, return_counts=True)
    lines.append("colors: " + " ".join(f"{int(v)}:{int(c)}" for v, c in zip(vals, cnts)))
    # locate uncommon colors (candidates for player/markers/goal) by bbox
    for v in vals:
        c = int((a == v).sum())
        if c == 0 or c > 400:  # skip background/floor/wall (big areas)
            continue
        ys, xs = np.where(a == v)
        lines.append(f"  color {int(v):>2}: {c:>3} cells  rows[{ys.min()}-{ys.max()}] "
                     f"cols[{xs.min()}-{xs.max()}]")
    return "\n".join(lines)

def diff(prev, cur):
    if prev is None or prev.shape != cur.shape:
        return "(no prev / shape change)"
    ys, xs = np.where(prev != cur)
    if len(ys) == 0:
        return "NO CELLS CHANGED"
    changes = [(int(r), int(c), int(prev[r, c]), int(cur[r, c])) for r, c in zip(ys, xs)]
    r0, r1, c0, c1 = ys.min(), ys.max(), xs.min(), xs.max()
    head = f"{len(changes)} cells changed · bbox rows[{r0}-{r1}] cols[{c0}-{c1}]"
    detail = "; ".join(f"({r},{c}){o}->{n}" for r, c, o, n in changes[:40])
    if len(changes) > 40:
        detail += f" … (+{len(changes)-40} more)"
    return head + "\n  " + detail

seq = 0
action_count = 0
prev = None

def write_state(last_cmd, fr, nframes):
    global prev
    gs = grids(fr) if fr is not None else []
    cur = gs[-1] if gs else None
    if len(gs) > 1:  # animation: dump every frame + per-frame diff (the physics live here)
        out = [f"cmd={last_cmd} frames={len(gs)}"]
        for i, g in enumerate(gs):
            d = diff(gs[i - 1], g) if i > 0 else "(first)"
            out.append(f"--- frame {i} ---\nDIFF vs prev frame: {d}\n{render(g)}")
        FRAMES.write_text("\n".join(out))
    d = diff(prev, cur) if cur is not None else "(none)"
    lines = [
        f"seq={seq} last_cmd={last_cmd} action_count={action_count}",
        f"state={fr.state} levels_completed={fr.levels_completed}/{fr.win_levels} "
        f"available_actions={fr.available_actions} num_frames={nframes}",
        f"DIFF: {d}",
        "FEATURES (exact coords, code-computed — trust these over eyeballing):",
        features(cur) if cur is not None else "(none)",
        "GRID (last frame; rows down = y, cols right = x; cells are hex color ids):",
        render(cur) if cur is not None else "(NO GRID — terminal/score frame; do NOT reset blindly)",
    ]
    STATE.write_text("\n".join(lines))
    with open(LOG, "a") as f:
        f.write(json.dumps({"seq": seq, "cmd": last_cmd, "state": str(fr.state),
                            "levels": fr.levels_completed, "actions": action_count}) + "\n")
    if cur is not None:
        prev = cur

fr = env.reset()
write_state("RESET(init)", fr, len(grids(fr)))
CMD.write_text("")  # clear command file
consumed = 0

while True:
    time.sleep(0.15)
    if not CMD.exists():
        continue
    cmds = [l.strip() for l in CMD.read_text().splitlines() if l.strip()]
    while consumed < len(cmds):
        line = cmds[consumed]
        consumed += 1
        if line == "QUIT":
            arc.close_scorecard(sc)
            STATE.write_text(f"seq={seq+1} QUIT scorecard={sc}\n")
            sys.exit(0)
        try:
            parts = line.split()
            tok = parts[0].upper()
            reasoning = {"note": " ".join(parts[3:])} if len(parts) > 3 else None
            if tok == "6":
                x, y = int(parts[1]), int(parts[2])
                fr = env.step(GameAction.ACTION6, data={"x": x, "y": y}, reasoning=reasoning)
                action_count += 1
            elif tok in ACT:
                fr = env.step(ACT[tok], reasoning=reasoning)
                action_count += 1 if tok != "RESET" else 0
            else:
                seq += 1
                write_state(f"BAD_CMD:{line}", fr, 0)
                continue
            seq += 1
            write_state(line, fr, len(grids(fr)))
        except Exception as e:
            seq += 1
            STATE.write_text(f"seq={seq} ERROR on '{line}': {e}\n")
