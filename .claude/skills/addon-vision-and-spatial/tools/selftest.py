#!/usr/bin/env -S uv run --quiet
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "opencv-python-headless>=4.10",
#   "numpy>=1.26",
# ]
# ///
"""selftest.py — one command that proves the whole skill works on THIS machine.

Round-trips the closed loop: known state -> render (render_state.py) ->
perceive back (perceive.py) -> compare. Then exercises edges, shapes, objects,
and imgdiff on synthetic scenes with known answers. Prints PASS/FAIL per stage;
exit code 0 only if everything passed.

  uv run .claude/skills/addon-vision-and-spatial/tools/selftest.py
"""

import json
import os
import subprocess
import sys
import tempfile

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from perceive import canon  # noqa: E402

FAILURES = []


def check(name, ok, detail=""):
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  ({detail})" if detail else ""))
    if not ok:
        FAILURES.append(name)


def run(argv):
    r = subprocess.run([sys.executable] + argv, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout)
        print(r.stderr, file=sys.stderr)
    return r


def main():
    tmp = tempfile.mkdtemp(prefix="avs_selftest_")
    render = os.path.join(HERE, "render_state.py")
    perceive = os.path.join(HERE, "perceive.py")

    # ---- 1. grid round-trip: state -> pixels -> state
    grid = [[0] * 9 for _ in range(7)]
    for c in range(1, 4):
        grid[1][c] = grid[2][c] = grid[3][c] = 2
    for c in range(2, 7):
        grid[5][c] = 3
    grid[0][8] = grid[6][0] = 1
    grid[3][5] = 4
    state_path = os.path.join(tmp, "truth.json")
    json.dump({"grid": grid}, open(state_path, "w"))
    png = os.path.join(tmp, "truth.png")
    r = run([render, state_path, "--no-coords", "--cell", "22", "-o", png])
    check("render known state", r.returncode == 0 and os.path.exists(png))

    r = run([perceive, "--outdir", tmp, "grid", png, "--verify"])
    ok = r.returncode == 0 and "VERIFY: OK" in r.stdout
    check("perceive grid --verify", ok)
    recon_path = os.path.join(tmp, "truth_grid.json")
    if os.path.exists(recon_path):
        recon = json.load(open(recon_path))["grid"]
        same = canon(grid) == canon(recon)
        check("round-trip equals ground truth", same,
              f"{len(grid)}x{len(grid[0])} -> {len(recon)}x{len(recon[0]) if recon else 0}")
    else:
        check("round-trip equals ground truth", False, "no reconstruction JSON")

    # ---- 2. shapes on a scene with known answers
    scene = np.zeros((300, 320, 3), np.uint8)
    cv2.circle(scene, (80, 80), 40, (255, 255, 255), -1)
    cv2.rectangle(scene, (150, 40), (260, 110), (255, 255, 255), -1)
    cv2.fillPoly(scene, [np.array([(60, 180), (140, 180), (100, 260)])], (255, 255, 255))
    scene_png = os.path.join(tmp, "scene.png")
    cv2.imwrite(scene_png, scene)
    r = run([perceive, "--outdir", tmp, "shapes", scene_png])
    found = json.load(open(os.path.join(tmp, "scene_shapes.json")))
    names = {s["shape"] for s in found}
    check("shapes finds 3 known shapes", len(found) == 3, f"found {len(found)}: {sorted(names)}")
    check("shapes classifies them", {"circle", "rectangle", "triangle"} <= names,
          f"got {sorted(names)}")

    # ---- 3. objects (blobs) on the same scene
    r = run([perceive, "--outdir", tmp, "objects", scene_png])
    blobs = json.load(open(os.path.join(tmp, "scene_objects.json")))["blobs"]
    check("objects finds 3 blobs", len(blobs) == 3, f"found {len(blobs)}")

    # ---- 4. edges produce a non-empty map
    r = run([perceive, "--outdir", tmp, "edges", scene_png])
    edge_img = cv2.imread(os.path.join(tmp, "scene_edges.png"), 0)
    check("edges non-empty", edge_img is not None and edge_img.max() == 255)

    # ---- 5. imgdiff catches a one-cell change
    grid[4][7] = 9
    state2 = os.path.join(tmp, "truth2.json")
    json.dump({"grid": grid}, open(state2, "w"))
    png2 = os.path.join(tmp, "truth2.png")
    run([render, state2, "--no-coords", "--cell", "22", "-o", png2])
    r = run([perceive, "--outdir", tmp, "imgdiff", png, png2])
    diff = json.load(open(os.path.join(tmp, "truth2_diff.json")))
    check("imgdiff finds the one change", len(diff["regions"]) == 1 and diff["changed_pct"] < 5.0,
          f"{len(diff['regions'])} regions, {diff['changed_pct']}% changed")

    # ---- 6. crop zooms
    r = run([perceive, "--outdir", tmp, "crop", scene_png, "--box", "40,40,80,80"])
    crop = cv2.imread(os.path.join(tmp, "scene_crop_40_40.png"))
    check("crop zooms", crop is not None and crop.shape[0] >= 400)

    print()
    if FAILURES:
        print(f"SELFTEST FAILED: {len(FAILURES)} stage(s): {', '.join(FAILURES)}")
        sys.exit(1)
    print(f"SELFTEST PASSED — dependencies install and the round-trip holds on "
          f"synthetic input. (Real screenshots are harder: --rows/--cols is the "
          f"reliable grid path there.) Artifacts in {tmp}")


if __name__ == "__main__":
    main()
