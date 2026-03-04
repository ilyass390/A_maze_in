from typing import Tuple, Set

# ── 42 pattern ────────────────────────────────────────────────
# Each (x, y) offset represents a logical cell that will be fully closed.
# '4': 3 wide x 5 tall   '2': 3 wide x 5 tall   (1 col gap between them)
PATTERN_42: Set[Tuple[int, int]] = (
    {(0,0), (2,0), (0,1), (2,1), (0,2), (1,2), (2,2), (2,3), (2,4)} |                     # '4'
    {(4,0), (5,0), (6,0), (6,1), (4,2), (5,2), (6,2), (4,3), (4,4), (5,4), (6,4)}         # '2'
)
PATTERN_W = max(x for x, _ in PATTERN_42) + 1
PATTERN_H = max(y for _, y in PATTERN_42) + 1


def find_42_position(cell_w: int, cell_h: int, entry_cell: Tuple[int, int], exit_cell: Tuple[int, int]) -> Tuple[int, int] | None:
    """
    Find a top-left anchor (in logical cell coords) where the 42 pattern fits
    without overlapping entry/exit and without touching the outer boundary.
    Returns None if no valid spot exists.
    """
    for sy in range(1, cell_h - PATTERN_H):
        for sx in range(1, cell_w - PATTERN_W):
            cells = {(sx + ox, sy + oy) for ox, oy in PATTERN_42}
            if entry_cell not in cells and exit_cell not in cells:
                return (sx, sy)
    return None


def stamp_42_on_grid(grid, anchor: Tuple[int, int]) -> None:
    """
    Stamp the 42 pattern onto the raw maze grid before the backtracker runs.
    Each logical cell (cx, cy) maps to grid position (cy*2+1, cx*2+1).
    Cells are marked as 0xF (fully closed / all walls).
    """
    ax, ay = anchor
    for ox, oy in PATTERN_42:
        gx = (ax + ox) * 2 + 1
        gy = (ay + oy) * 2 + 1
        grid[gy, gx] = 0xF
