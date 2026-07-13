"""Parse the current LF52 frame into peg-solitaire objects.

This reads only the online harness artifact. It deliberately knows nothing
about the environment implementation or level answers.
"""

from __future__ import annotations

import pathlib
import re
from collections import deque


STATE = pathlib.Path(__file__).resolve().parent / "arc_state.txt"


def read_grid() -> list[list[int]]:
    rows: dict[int, list[int]] = {}
    for line in STATE.read_text().splitlines():
        match = re.match(r"\s*(\d+) \| ([0-9a-f]{64})$", line)
        if match:
            rows[int(match.group(1))] = [int(char, 16) for char in match.group(2)]
    if sorted(rows) != list(range(64)):
        raise RuntimeError("current state does not contain one complete 64x64 grid")
    return [rows[row] for row in range(64)]


def fixed_holes(grid: list[list[int]]) -> list[tuple[int, int, bool]]:
    """Return (center_x2, center_y2, occupied), using doubled coordinates."""
    found = []
    tile_values = {1, 14}
    for top in range(61):
        for left in range(61):
            block = [grid[y][left : left + 4] for y in range(top, top + 4)]
            if not all(value in tile_values for row in block for value in row):
                continue
            # Exact 4x4 islands only; reject shifted windows within larger areas.
            boundary = []
            if top:
                boundary.extend(grid[top - 1][left : left + 4])
            if top + 4 < 64:
                boundary.extend(grid[top + 4][left : left + 4])
            if left:
                boundary.extend(grid[y][left - 1] for y in range(top, top + 4))
            if left + 4 < 64:
                boundary.extend(grid[y][left + 4] for y in range(top, top + 4))
            if any(value in tile_values for value in boundary):
                continue
            occupied = any(value == 14 for row in block for value in row)
            found.append((2 * left + 3, 2 * top + 3, occupied))
    return found


def carts(grid: list[list[int]]) -> list[tuple[int, int, bool]]:
    """Return cart (center_x2, center_y2, loaded), using doubled coordinates."""
    found = []
    for top in range(59):
        for left in range(59):
            outer = []
            inner = []
            for row in range(6):
                for col in range(6):
                    value = grid[top + row][left + col]
                    (outer if row in (0, 5) or col in (0, 5) else inner).append(value)
            if all(value == 11 for value in outer) and all(value in {12, 14} for value in inner):
                found.append((2 * left + 5, 2 * top + 5, 14 in inner))
    return found


def springs(grid: list[list[int]]) -> list[tuple[int, int]]:
    """Return reusable spring centers, using doubled coordinates."""
    found = []
    pattern = (
        (15, 15, 15, 15),
        (15, 0, 7, 15),
        (15, 7, 7, 15),
        (15, 15, 15, 15),
    )
    for top in range(61):
        for left in range(61):
            block = tuple(tuple(grid[y][left : left + 4]) for y in range(top, top + 4))
            if block != pattern:
                continue
            found.append((2 * left + 3, 2 * top + 3))
    return found


def paired_runs(grid: list[list[int]], horizontal: bool) -> list[tuple[int, int, int]]:
    """Find long two-cell-wide grey rail runs as (axis2, start2, end2)."""
    runs = []
    outer = 63
    for axis in range(outer):
        values = []
        for along in range(64):
            pair = (
                (grid[axis][along], grid[axis + 1][along])
                if horizontal
                else (grid[along][axis], grid[along][axis + 1])
            )
            values.append(pair == (5, 5))
        start = None
        for index, present in enumerate(values + [False]):
            if present and start is None:
                start = index
            elif not present and start is not None:
                if index - start >= 6:
                    runs.append((2 * axis + 1, 2 * start + 1, 2 * (index - 1) + 1))
                start = None
    # Adjacent axis scans describe the same 2-wide rail; keep maximal unique runs.
    return sorted(set(runs))


def fmt(point: tuple[int, int, bool]) -> str:
    x2, y2, occupied = point
    return f"({x2 / 2:g},{y2 / 2:g}) {'PEG' if occupied else 'empty'}"


def main() -> None:
    grid = read_grid()
    holes = fixed_holes(grid)
    mobile = carts(grid)
    spring_points = springs(grid)
    print(f"fixed holes: {len(holes)}")
    for point in sorted(holes, key=lambda item: (item[1], item[0])):
        print("  ", fmt(point))
    print(f"carts: {len(mobile)}")
    for point in sorted(mobile, key=lambda item: (item[1], item[0])):
        print("  ", fmt(point))
    print(f"springs: {len(spring_points)}")
    for x2, y2 in sorted(spring_points, key=lambda item: (item[1], item[0])):
        print(f"   ({x2 / 2:g},{y2 / 2:g})")
    print("horizontal grey runs (y, x0..x1):")
    for axis2, start2, end2 in paired_runs(grid, horizontal=True):
        print(f"  y={axis2 / 2:g} x={start2 / 2:g}..{end2 / 2:g}")
    print("vertical grey runs (x, y0..y1):")
    for axis2, start2, end2 in paired_runs(grid, horizontal=False):
        print(f"  x={axis2 / 2:g} y={start2 / 2:g}..{end2 / 2:g}")


if __name__ == "__main__":
    main()
