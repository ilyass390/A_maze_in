import curses
import locale
from typing import List, Tuple, Optional, Set, Dict, Any
import numpy as np

locale.setlocale(locale.LC_ALL, '')


class Render_Maze:
    def __init__(
        self,
        maze: np.ndarray,
        entry: Tuple[int, int],
        exit_: Tuple[int, int],
        path: Optional[str] = None,
    ) -> None:
        self.maze: np.ndarray = maze
        self.entry: Tuple[int, int] = entry
        self.exit: Tuple[int, int] = exit_
        self.path: Optional[str] = path
        self.wall_color_index: int = 0
        self.wall_colors: List[int] = [
            curses.COLOR_WHITE,
            curses.COLOR_CYAN,
            curses.COLOR_GREEN,
            curses.COLOR_YELLOW,
            curses.COLOR_MAGENTA,
            curses.COLOR_RED,
            curses.COLOR_BLUE,
        ]
        self.disco_mode: bool = False
        self.disco_frame: int = 0
        self.player_mode: bool = False
        self.player_pos: Optional[Tuple[int, int]] = None
        self.player_won: bool = False

    def _disco_tick(self) -> None:
        self.disco_frame = (self.disco_frame + 1) % len(self.wall_colors)
        curses.init_pair(1, self.wall_colors[self.disco_frame], -1)

    def _move_player(self, key: int) -> None:
        if self.player_pos is None:
            return
        x: int
        y: int
        x, y = self.player_pos
        move_map: Dict[int, Tuple[int, int, int]] = {
            curses.KEY_UP:    (0, -1, 0),
            curses.KEY_RIGHT: (1,  0, 1),
            curses.KEY_DOWN:  (0,  1, 2),
            curses.KEY_LEFT:  (-1, 0, 3),
        }
        if key not in move_map:
            return
        dx: int
        dy: int
        wall_bit: int
        dx, dy, wall_bit = move_map[key]
        if not (self.maze[y, x] & (1 << wall_bit)):
            self.player_pos = (x + dx, y + dy)
            if self.player_pos == self.exit:
                self.player_won = True

    def _get_intersection_char(
        self,
        up: int,
        right: int,
        down: int,
        left: int,
    ) -> str:
        connections: Tuple[int, int, int, int] = (up, right, down, left)
        mapping: Dict[Tuple[int, int, int, int], str] = {
            (1, 1, 1, 1): "╬",
            (1, 1, 1, 0): "╠",
            (1, 0, 1, 1): "╣",
            (0, 1, 1, 1): "╦",
            (1, 1, 0, 1): "╩",
            (1, 0, 1, 0): "║",
            (0, 1, 0, 1): "═",
            (0, 1, 1, 0): "╔",
            (0, 0, 1, 1): "╗",
            (1, 1, 0, 0): "╚",
            (1, 0, 0, 1): "╝",
        }
        return mapping.get(connections, " ")

    def _set_wall_color(self) -> None:
        curses.init_pair(1, self.wall_colors[self.wall_color_index], -1)

    def _get_intersection_chars(self) -> Set[str]:
        return set("╬╠╣╦╩║═╔╗╚╝")

    def _path_to_coords(self, path_str: str) -> List[Tuple[int, int]]:
        direction_map: Dict[str, Tuple[int, int]] = {
            'N': (0, -1),
            'S': (0,  1),
            'E': (1,  0),
            'W': (-1, 0),
        }
        x: int
        y: int
        x, y = self.entry
        coords: List[Tuple[int, int]] = [(x, y)]
        for char in path_str:
            dx: int
            dy: int
            dx, dy = direction_map[char]
            x += dx
            y += dy
            coords.append((x, y))
        return coords

    def _init_colors(self) -> None:
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(8, 8, 8)
        curses.init_pair(1, curses.COLOR_WHITE, -1)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_GREEN)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_RED)
        curses.init_pair(4, curses.COLOR_CYAN, -1)
        curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_YELLOW)
        curses.init_pair(6, curses.COLOR_CYAN, -1)
        curses.init_pair(7, curses.COLOR_MAGENTA, -1)
        self._set_wall_color()

    def _build_display(self, maze: np.ndarray) -> List[List[str]]:
        height: int
        width: int
        height, width = maze.shape
        display: List[List[str]] = [
            [" " for _ in range(3 * width + 1)]
            for _ in range(2 * height + 1)
        ]

        for y in range(height):
            for x in range(width):
                cell: int = maze[y, x]
                base_y: int = 2 * y
                base_x: int = 3 * x

                display[base_y + 1][base_x + 1] = " "
                display[base_y + 1][base_x + 2] = " "

                if cell & 1:
                    display[base_y][base_x + 1] = "═"
                    display[base_y][base_x + 2] = "═"
                if cell & 4:
                    display[base_y + 2][base_x + 1] = "═"
                    display[base_y + 2][base_x + 2] = "═"
                if cell & 8:
                    display[base_y + 1][base_x] = "║"
                if cell & 2:
                    display[base_y + 1][base_x + 3] = "║"

        for y in range(0, 2 * height + 1, 2):
            for x in range(0, 3 * width + 1, 3):
                u: int
                d: int
                le: int
                r: int
                u = 1 if y > 0 and display[y - 1][x] == "║" else 0
                d = 1 if y < 2 * height and display[y + 1][x] == "║" else 0
                le = 1 if x > 0 and display[y][x - 1] == "═" else 0
                r = 1 if x < 3 * width and display[y][x + 1] == "═" else 0
                display[y][x] = self._get_intersection_char(u, r, d, le)

        return display

    def _draw_frame(
        self,
        stdscr: Any,
        maze: np.ndarray,
        head: Optional[Tuple[int, int]] = None,
        action_type: Optional[str] = None,
        path_sf: Optional[List[Tuple[int, int]]] = None,
    ) -> None:
        stdscr.clear()
        display: List[List[str]] = self._build_display(maze)
        height: int
        width: int
        height, width = maze.shape
        path_set: Set[Tuple[int, int]] = set(path_sf) if path_sf else set()

        for y in range(len(display)):
            for x in range(len(display[y])):
                char: str = display[y][x]
                cell_x: int = x // 3
                cell_y: int = y // 2
                is_wall: bool = (
                    char in self._get_intersection_chars()
                    or char in ("═", "║")
                )
                is_interior: bool = not is_wall
                is_head: bool = head is not None and (cell_x, cell_y) == head
                color: int

                if (is_interior and (cell_x, cell_y) == self.entry
                        and x % 3 != 0 and y % 2 != 0):
                    color = curses.color_pair(2)
                    char = " "
                elif (is_interior and (cell_x, cell_y) == self.exit
                        and x % 3 != 0 and y % 2 != 0):
                    color = curses.color_pair(3)
                    char = " "
                elif is_interior and is_head:
                    char = "▓"
                    color = curses.color_pair(4)
                elif (is_interior and self.player_pos
                        and (cell_x, cell_y) == self.player_pos
                        and y % 2 != 0 and x % 3 != 0):
                    char = "◉"
                    color = curses.color_pair(5)
                elif is_interior and (cell_x, cell_y) in path_set:
                    char = "*" if x % 3 == 1 else " "
                    color = curses.color_pair(7)
                elif is_wall:
                    color = curses.color_pair(1)
                elif (is_interior
                        and (cell_x, cell_y) in getattr(
                            self, 'pattern_coords', set()
                        )
                        and y % 2 != 0 and x % 3 != 0):
                    color = curses.color_pair(8)
                    char = " "
                elif char == " ":
                    continue
                else:
                    continue

                try:
                    stdscr.addstr(y, x, char, color)
                except curses.error:
                    pass

        menu_y: int = 2 * height + 2

        menu_items: List[Tuple[str, str]] = [
            ("  +/-", "speed"),
            ("space", "skip"),
            ("    p", "path"),
            ("    r", "new maze"),
            ("    q", "quit"),
            ("    c", "wall color"),
            ("    d", "disco mode"),
            ("    m", "play"),
        ]

        x_offset: int = 0
        for key, desc in menu_items:
            try:
                stdscr.addstr(
                    menu_y, x_offset, key,
                    curses.color_pair(6) | curses.A_BOLD,
                )
                stdscr.addstr(
                    menu_y, x_offset + len(key),
                    f" {desc}  ",
                    curses.color_pair(1),
                )
            except curses.error:
                pass
            x_offset += len(key) + len(desc) + 3
        stdscr.refresh()

    # ── animation ──────────────────

    def animate(self, actions: List[Dict[str, Any]]) -> bool:
        return curses.wrapper(self._animate_main, actions)

    def _draw_win(self, stdscr: Any) -> None:
        height: int
        height, _ = self.maze.shape
        msg: str = "  YOU SOLVED IT!  press r to regenerate or q to quit  "
        y: int = height + 3
        try:
            stdscr.addstr(y, 0, msg, curses.color_pair(2) | curses.A_BOLD)
            stdscr.refresh()
        except curses.error:
            pass

    def _animate_main(
        self,
        stdscr: Any,
        actions: List[Dict[str, Any]],
    ) -> bool:
        curses.curs_set(0)
        self._init_colors()

        height: int
        width: int
        height, width = self.maze.shape
        anim_maze: np.ndarray = np.full((height, width), 0xF, dtype=np.uint8)

        delay: int = 50
        current_head: Optional[Tuple[int, int]] = None
        stdscr.nodelay(True)

        self.pattern_coords: Set[Tuple[int, int]] = set()
        for action in actions:
            if action['type'] == 'pattern':
                self.pattern_coords.add(action['cell'])
        for action in actions:
            key: int = stdscr.getch()
            if key == ord('+'):
                delay = max(10, delay - 10)
            elif key == ord('-'):
                delay = min(500, delay + 10)
            elif key == ord(' '):
                np.copyto(anim_maze, self.maze)
                self._draw_frame(
                    stdscr,
                    anim_maze,
                    head=None,
                    action_type=None)
                break
            elif key == ord('r'):
                return True
            elif key == ord('q'):
                return False
            elif key == ord('c'):
                self.wall_color_index = (
                    (self.wall_color_index + 1) % len(self.wall_colors)
                )
                self._set_wall_color()
            elif key == ord('d'):
                self.disco_mode = not self.disco_mode

            if action['type'] == 'pattern':
                x: int
                y: int
                x, y = action['cell']
                anim_maze[y, x] = 0xF
            elif action['type'] == 'visit':
                current_head = action['cell']
            elif action['type'] == 'carve':
                fx: int
                fy: int
                tx: int
                ty: int
                fx, fy = action['from_cell']
                tx, ty = action['to_cell']
                wall_map: Dict[str, Tuple[int, int]] = {
                    'N': (0, 2), 'S': (2, 0), 'E': (1, 3), 'W': (3, 1),
                }
                from_bit: int
                to_bit: int
                from_bit, to_bit = wall_map[action['direction']]
                anim_maze[fy, fx] &= ~(1 << from_bit)
                anim_maze[ty, tx] &= ~(1 << to_bit)
                current_head = (tx, ty)
            elif action['type'] == 'backtrack':
                current_head = action['from_cell']
            elif action['type'] == 'imperfect_carve':
                x, y = action['cell']
                nx: int
                ny: int
                nx, ny = action['neighbor']
                anim_maze[y, x] &= ~(1 << action['wall'])
                anim_maze[ny, nx] &= ~(1 << action['neighbor_wall'])
                current_head = (x, y)

            if self.disco_mode:
                self._disco_tick()
            self._draw_frame(stdscr, anim_maze, current_head, action['type'])
            curses.napms(delay)

        if self.path and self.path != "No path found":
            path_coords: List[Tuple[int, int]] = self._path_to_coords(
                self.path
                )
            for i in range(len(path_coords)):
                key = stdscr.getch()
                if key == ord('q'):
                    return False
                elif key == ord('r'):
                    return True
                elif key == ord(' '):
                    self._draw_frame(
                        stdscr, anim_maze,
                        head=None, action_type=None,
                        path_sf=path_coords,
                    )
                    break
                elif key == ord('d'):
                    self.disco_mode = not self.disco_mode
                if self.disco_mode:
                    self._disco_tick()
                self._draw_frame(
                    stdscr, anim_maze,
                    head=None, action_type=None,
                    path_sf=path_coords[:i + 1],
                )
                curses.napms(30)

        show_path: bool = True
        path_coords_final: Optional[List[Tuple[int, int]]] = (
            self._path_to_coords(self.path)
            if self.path and self.path != "No path found"
            else None
        )

        self._draw_frame(
            stdscr, self.maze,
            head=None, action_type=None,
            path_sf=path_coords_final if show_path else None,
        )

        while True:
            stdscr.timeout(80 if self.disco_mode else -1)
            key = stdscr.getch()

            if key == ord('q'):
                return False
            elif key == ord('r'):
                return True
            elif key == ord('p'):
                show_path = not show_path
                self._draw_frame(
                    stdscr, self.maze,
                    head=None, action_type=None,
                    path_sf=path_coords_final if show_path else None,
                )
            elif key == ord('c'):
                self.disco_mode = False
                self.wall_color_index = (
                    (self.wall_color_index + 1) % len(self.wall_colors)
                )
                self._set_wall_color()
                self._draw_frame(
                    stdscr, self.maze,
                    head=None, action_type=None,
                    path_sf=path_coords_final if show_path else None,
                )
            elif key == ord('d'):
                self.disco_mode = not self.disco_mode
                if not self.disco_mode:
                    self._draw_frame(
                        stdscr, self.maze,
                        head=None, action_type=None,
                        path_sf=path_coords_final if show_path else None,
                    )
            elif key == -1 and self.disco_mode:
                self._disco_tick()
                self._draw_frame(
                    stdscr, self.maze,
                    head=None, action_type=None,
                    path_sf=path_coords_final if show_path else None,
                )
            elif (key in (
                curses.KEY_UP, curses.KEY_DOWN,
                curses.KEY_LEFT, curses.KEY_RIGHT,
            ) and self.player_mode):
                self._move_player(key)
                self._draw_frame(
                    stdscr, self.maze,
                    head=None, action_type=None,
                    path_sf=path_coords_final if show_path else None,
                )
                if self.player_won:
                    self._draw_win(stdscr)

    # ── static display ────────────────────

    def _draw(self, stdscr: Any) -> None:
        curses.curs_set(0)
        path_coords: Optional[List[Tuple[int, int]]] = (
            self._path_to_coords(self.path)
            if self.path and self.path != "No path found"
            else None
        )
        self._draw_frame(stdscr, self.maze, path_sf=path_coords)

    def _main(self, stdscr: Any) -> None:
        curses.curs_set(0)
        if not curses.has_colors():
            raise Exception("Terminal does not support colors")
        self._init_colors()
        self._draw(stdscr)
        stdscr.getch()

    def display(self) -> None:
        curses.wrapper(self._main)
