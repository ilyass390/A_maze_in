import curses
import numpy as n
import locale
locale.setlocale(locale.LC_ALL, '')

class Render_Maze:
    def __init__(self, maze, entry, exit_, path=None):
        self.maze = maze
        self.entry = entry
        self.exit = exit_
        self.path = path
        self.wall_color_index = 0
        self.wall_colors = [
            curses.COLOR_WHITE,
            curses.COLOR_CYAN,
            curses.COLOR_GREEN,
            curses.COLOR_YELLOW,
            curses.COLOR_MAGENTA,
            curses.COLOR_RED,
            curses.COLOR_BLUE,
        ]
        self.disco_mode = False
        self.disco_frame = 0
    
    def _disco_tick(self):
        self.disco_frame = (self.disco_frame + 1) % len(self.wall_colors)
        curses.init_pair(1, self.wall_colors[self.disco_frame], -1)

    def _get_intersection_char(self, up, right, down, left):
        connections = (up, right, down, left)
        mapping = {
            (1,1,1,1): "╬",
            (1,1,1,0): "╠",
            (1,0,1,1): "╣",
            (0,1,1,1): "╦",
            (1,1,0,1): "╩",
            (1,0,1,0): "║",
            (0,1,0,1): "═",
            (0,1,1,0): "╔",
            (0,0,1,1): "╗",
            (1,1,0,0): "╚",
            (1,0,0,1): "╝",
        }
        return mapping.get(connections, " ")

    def _set_wall_color(self):
        curses.init_pair(1, self.wall_colors[self.wall_color_index], -1)
    def _get_intersection_chars(self):
        return set("╬╠╣╦╩║═╔╗╚╝")

    def _path_to_coords(self, path_str):
        direction_map = {
            'N': (0, -1),
            'S': (0,  1),
            'E': (1,  0),
            'W': (-1, 0),
        }
        x, y = self.entry
        coords = [(x, y)]
        for char in path_str:
            dx, dy = direction_map[char]
            x += dx
            y += dy
            coords.append((x, y))
        return coords

    def _init_colors(self):
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(8, 8, 8)  # gray
        curses.init_pair(1, curses.COLOR_WHITE, -1)                      # walls
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_GREEN)      # entry
        curses.init_pair(3, curses.COLOR_RED,   curses.COLOR_RED)        # exit
        curses.init_pair(4, curses.COLOR_CYAN,  -1)                      # carving head
        curses.init_pair(5, curses.COLOR_YELLOW, -1)                     # backtrack head
        curses.init_pair(6, curses.COLOR_CYAN, -1)
        curses.init_pair(7, curses.COLOR_MAGENTA, -1)                    # path
        self._set_wall_color()

    def _build_display(self, maze):
        height, width = maze.shape
        display = [[" " for _ in range(3 * width + 1)] for _ in range(2 * height + 1)]

        for y in range(height):
            for x in range(width):
                cell = maze[y, x]
                base_y = 2 * y
                base_x = 3 * x

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
                up    = 1 if y > 0         and display[y-1][x] == "║" else 0
                down  = 1 if y < 2*height  and display[y+1][x] == "║" else 0
                left  = 1 if x > 0         and display[y][x-1] == "═" else 0
                right = 1 if x < 3*width   and display[y][x+1] == "═" else 0
                display[y][x] = self._get_intersection_char(up, right, down, left)

        return display

    def _draw_frame(self, stdscr, maze, head=None, action_type=None, path_so_far=None):
        stdscr.clear()
        display = self._build_display(maze)
        height, width = maze.shape
        path_set = set(path_so_far) if path_so_far else set()

        for y in range(len(display)):
            for x in range(len(display[y])):
                char = display[y][x]
                cell_x = x // 3
                cell_y = y // 2
                is_wall = char in self._get_intersection_chars() or char in ("═", "║")
                is_interior = not is_wall
                is_head = head is not None and (cell_x, cell_y) == head

                if is_interior and (cell_x, cell_y) == self.entry and x % 3 != 0 and y % 2 != 0:
                    color = curses.color_pair(2)
                    char = " "
                elif is_interior and (cell_x, cell_y) == self.exit and x % 3 != 0 and y % 2 != 0:
                    color = curses.color_pair(3)
                    char = " "
                elif is_interior and is_head:
                    char = "▓"
                    color = curses.color_pair(4) if action_type != 'backtrack' else curses.color_pair(5)
                elif is_interior and (cell_x, cell_y) in path_set:
                    char = "*" if x % 3 == 2 else " "  # center char in left slot, space in right
                    color = curses.color_pair(7)
                elif is_wall:
                    color = curses.color_pair(1)
                elif is_interior and (cell_x, cell_y) in getattr(self, 'pattern_coords', set()) and y % 2 != 0 and x % 3 != 0:
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

        height, width = maze.shape
        menu_y = 2 * height + 2  # one line below the maze

        menu_items = [
            ("  +/-", "speed"),
            ("space", "skip"),
            ("    p", "path"),
            ("    r", "new maze"),
            ("    q", "quit"),
            ("    c", "wall color"),
            ("    d", "disco mode"),
        ]

        x_offset = 0
        for key, desc in menu_items:
            try:
                stdscr.addstr(menu_y, x_offset, key, curses.color_pair(6) | curses.A_BOLD)
                stdscr.addstr(menu_y, x_offset + len(key), f" {desc}  ", curses.color_pair(1))
            except curses.error:
                pass
            x_offset += len(key) + len(desc) + 3
        stdscr.refresh()

    # ── animation ──────────────────────────────────────────────────────────────

    def animate(self, actions):
        return curses.wrapper(self._animate_main, actions)

    def _animate_main(self, stdscr, actions):
        curses.curs_set(0)
        self._init_colors()

        height, width = self.maze.shape
        anim_maze = n.full((height, width), 0xF, dtype=n.uint8)

        delay = 50
        current_head = None
        stdscr.nodelay(True)

        self.pattern_coords = set()
        for action in actions:
            if action['type'] == 'pattern':
                self.pattern_coords.add(action['cell'])
        for action in actions:
            key = stdscr.getch()
            if key == ord('+'):
                delay = max(10, delay - 10)
            elif key == ord('-'):
                delay = min(500, delay + 10)
            elif key == ord(' '):
                n.copyto(anim_maze, self.maze)
                self._draw_frame(stdscr, anim_maze, head=None, action_type=None)
                break
            elif key == ord('r'):
                return True
            elif key == ord('q'):
                return False
            elif key == ord('c'):
                self.wall_color_index = (self.wall_color_index + 1) % len(self.wall_colors)
                self._set_wall_color()
            elif key == ord('d'):
                self.disco_mode = not self.disco_mode

            if action['type'] == 'pattern':
                x, y = action['cell']
                anim_maze[y, x] = 0xF
            elif action['type'] == 'visit':
                current_head = action['cell']
            elif action['type'] == 'carve':
                fx, fy = action['from_cell']
                tx, ty = action['to_cell']
                wall_map = {'N': (0, 2), 'S': (2, 0), 'E': (1, 3), 'W': (3, 1)}
                from_bit, to_bit = wall_map[action['direction']]
                anim_maze[fy, fx] &= ~(1 << from_bit)
                anim_maze[ty, tx] &= ~(1 << to_bit)
                current_head = (tx, ty)
            elif action['type'] == 'backtrack':
                current_head = action['from_cell']
            elif action['type'] == 'imperfect_carve':
                x, y = action['cell']
                nx, ny = action['neighbor']
                anim_maze[y, x]   &= ~(1 << action['wall'])
                anim_maze[ny, nx] &= ~(1 << action['neighbor_wall'])
                current_head = (x, y)

            if self.disco_mode:
                self._disco_tick()
            self._draw_frame(stdscr, anim_maze, current_head, action['type'])
            curses.napms(delay)

        # path animation
        if self.path and self.path != "No path found":
            path_coords = self._path_to_coords(self.path)
            for i in range(len(path_coords)):
                key = stdscr.getch()
                if key == ord('q'):
                    return False
                elif key == ord('r'):
                    return True
                elif key == ord(' '):
                    self._draw_frame(stdscr, anim_maze, head=None, action_type=None, path_so_far=path_coords)
                    break
                elif key == ord('d'):
                    self.disco_mode = not self.disco_mode
                if self.disco_mode:
                    self._disco_tick()
                self._draw_frame(stdscr, anim_maze, head=None, action_type=None, path_so_far=path_coords[:i+1])
                curses.napms(30)

        # final hold loop
        show_path = True
        path_coords = self._path_to_coords(self.path) if self.path and self.path != "No path found" else None

        self._draw_frame(stdscr, self.maze, head=None, action_type=None,
                        path_so_far=path_coords if show_path else None)

        while True:
            stdscr.timeout(80 if self.disco_mode else -1)  # -1 = blocking, 80ms when disco
            key = stdscr.getch()

            if key == ord('q'):
                return False
            elif key == ord('r'):
                return True
            elif key == ord('p'):
                show_path = not show_path
                self._draw_frame(stdscr, self.maze, head=None, action_type=None,
                                path_so_far=path_coords if show_path else None)
            elif key == ord('c'):
                self.disco_mode = False  # stop disco if manually picking color
                self.wall_color_index = (self.wall_color_index + 1) % len(self.wall_colors)
                self._set_wall_color()
                self._draw_frame(stdscr, self.maze, head=None, action_type=None,
                                path_so_far=path_coords if show_path else None)
            elif key == ord('d'):
                self.disco_mode = not self.disco_mode
                if not self.disco_mode:
                    # stopped — land on whatever color is current
                    self._draw_frame(stdscr, self.maze, head=None, action_type=None,
                                    path_so_far=path_coords if show_path else None)
            elif key == -1 and self.disco_mode:  # timeout fired, no keypress
                self._disco_tick()
                self._draw_frame(stdscr, self.maze, head=None, action_type=None,
                                path_so_far=path_coords if show_path else None)

    # ── static display ─────────────────────────────────────────────────────────

    def _draw(self, stdscr):
        curses.curs_set(0)
        path_coords = self._path_to_coords(self.path) if self.path and self.path != "No path found" else None
        self._draw_frame(stdscr, self.maze, path_so_far=path_coords)

    def _main(self, stdscr):
        curses.curs_set(0)
        if not curses.has_colors():
            raise Exception("Terminal does not support colors")
        self._init_colors()
        self._draw(stdscr)
        stdscr.getch()

    def display(self):
        curses.wrapper(self._main)