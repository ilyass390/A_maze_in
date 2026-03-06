import random
from typing import List, Tuple, Optional, Set, Dict, Any, Union
import numpy as n


class MazeGenerator:
    """Generate mazes based on a config file using iterative backtracking."""

    def __init__(
        self,
        height: int,
        width: int,
        entry: Tuple[int, int],
        exit_: Tuple[int, int],
        perfect: bool,
        output_file: Optional[str],
        seed: Optional[int],
    ) -> None:
        """Initialise the maze generator based on parsed
        config file.

            height: Number of rows in the maze.
            width: Number of columns in the maze.
            entry: (x, y) coordinates of the entry cell.
            exit_: (x, y) coordinates of the exit cell.
            perfect: If True, generate a perfect maze.
            output_file: path for hexadecimal output.
            seed: Optional random seed for reproducibility.
        """
        self.width: int = width
        self.height: int = height
        self.entry: Tuple[int, int] = entry
        self.exit: Tuple[int, int] = exit_
        self.output_file: Optional[str] = output_file
        self.seed: Optional[int] = seed
        self.perfect: bool = perfect
        self.generated_maze: Optional[n.ndarray] = None
        self.path: Optional[str] = None

    def pattern_42(self) -> Set[Tuple[int, int]]:
        """Return scaled coordinates of the '42' pattern.
        """
        base_pattern: Set[Tuple[int, int]] = {
            (0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 3), (2, 4),
            (4, 0), (5, 0), (6, 0), (6, 1), (4, 2), (5, 2), (6, 2), (4, 3),
            (4, 4), (5, 4), (6, 4),
        }
        pattern_width: int = max(x for x, _ in base_pattern) + 1
        pattern_height: int = max(y for _, y in base_pattern) + 1
        if self.height <= pattern_height or self.width <= pattern_width:
            print(
                "cannot place pattern on the maze "
                f"{self.width}/{self.height}"
                )
            exit(0)
        scale_x: int = self.width // pattern_width
        scale_y: int = self.height // pattern_height
        scale: int = max(1, min(scale_x, scale_y) // 25)
        pattern_height = pattern_height * scale
        pattern_width = pattern_width * scale
        middle_x: int = (self.width - pattern_width) // 2
        middle_y: int = (self.height - pattern_height) // 2
        scaled_pattern: Set[Tuple[int, int]] = set()
        for px, py in base_pattern:
            for sx in range(scale):
                for sy in range(scale):
                    x: int = px * scale + sx + middle_x
                    y: int = py * scale + sy + middle_y
                    scaled_pattern.add((x, y))
        return scaled_pattern

    def iterative_backtracker(
        self,
        record: bool = False,
    ) -> Union[n.ndarray, Tuple[n.ndarray, List[Dict[str, Any]]]]:
        """Generate a perfect maze via randomised iterative backtracking.

        Uses a stack-based DFS that carves passages by removing walls
        between near unvisited cells.
        """
        direction_map: Dict[str, Tuple[int, int, int, int]] = {
            "North": (0, -1, 1, 4),
            "South": (0,  1, 4, 1),
            "West":  (-1, 0, 8, 2),
            "East":  (1,  0, 2, 8),
        }
        compass: List[str] = ["North", "East", "South", "West"]
        maze: n.ndarray = n.full(
            (self.height, self.width),
            0xF,
            dtype=n.uint8
            )
        actions: Optional[List[Dict[str, Any]]] = [] if record else None
        pattern_coords: Set[Tuple[int, int]] = self.pattern_42()
        enx: int
        eny: int
        enx, eny = self.entry
        random.shuffle(compass)
        stack_simulation: List[Tuple[int, int, List[str]]] = [
            (enx, eny, compass.copy())
            ]
        visited_cells: Set[Tuple[int, int]] = {(enx, eny)}

        if actions is not None:
            actions.append(
                {'type': 'visit', 'cell': (enx, eny), 'stack_size': 1}
                )

        for cord in pattern_coords:
            if cord == self.entry or cord == self.exit:
                print("Entry/Exit spotted on pattern")
                exit(0)
            visited_cells.add(cord)
            x: int
            y: int
            x, y = cord
            maze[y, x] = 0xF
            if actions is not None:
                actions.append({'type': 'pattern', 'cell': (x, y)})

        while stack_simulation:
            x, y, cell_compass = stack_simulation[-1]
            moved: bool = False

            while cell_compass:
                move: str = cell_compass.pop(0)
                dx: int
                dy: int
                wall: int
                neighbor_wall: int
                dx, dy, wall, neighbor_wall = direction_map[move]
                nx: int = x + dx
                ny: int = y + dy

                if (0 <= nx < self.width and 0 <= ny < self.height
                        and (nx, ny) not in visited_cells):
                    maze[y, x] -= wall
                    maze[ny, nx] -= neighbor_wall
                    visited_cells.add((nx, ny))

                    if actions is not None:
                        actions.append({
                            'type': 'carve',
                            'from_cell': (x, y),
                            'to_cell': (nx, ny),
                            'direction': move[0],
                            'stack_size': len(stack_simulation),
                        })
                        actions.append({
                            'type': 'visit',
                            'cell': (nx, ny),
                            'stack_size': len(stack_simulation) + 1,
                        })

                    fresh_compass: List[str] = compass.copy()
                    random.shuffle(fresh_compass)
                    stack_simulation.append((nx, ny, fresh_compass))
                    moved = True
                    break

            if not moved:
                if actions is not None:
                    actions.append({
                        'type': 'backtrack',
                        'from_cell': (x, y),
                        'stack_size': len(stack_simulation) - 1,
                    })
                stack_simulation.pop()

        if record:
            assert actions is not None
            return (maze, actions)
        return maze

    def bfs(self, maze: n.ndarray) -> str:
        """Find the shortest path from entry to exit using BFS.
        """
        directions: Dict[int, Tuple[int, int, str]] = {
            2: (0, 1, 'S'),
            0: (0, -1, 'N'),
            1: (1, 0, 'E'),
            3: (-1, 0, 'W'),
        }
        enx: int
        eny: int
        exx: int
        exy: int
        enx, eny = self.entry
        exx, exy = self.exit
        queue: List[Tuple[int, int, str]] = [(enx, eny, "")]
        visited: Set[Tuple[int, int]] = {(enx, eny)}
        height: int
        width: int
        height, width = maze.shape
        while queue:
            x: int
            y: int
            path: str
            x, y, path = queue.pop(0)
            if (x, y) == (exx, exy):
                return path

            for direction, (dx, dy, compass) in directions.items():
                if not bool(maze[y, x] & (0x1 << direction)):
                    nx: int = x + dx
                    ny: int = y + dy

                    if (0 <= nx < width
                            and 0 <= ny < height
                            and (nx, ny) not in visited):
                        visited.add((nx, ny))
                        queue.append((nx, ny, path + compass))

        return "No path found"

    def imperfection_helper(self, maze: n.ndarray) -> bool:
        """Check whether removing a wall created a 3x3 open area.
        """
        for y in range(self.height - 2):
            for x in range(self.width - 2):
                open_check: bool = True
                for y1 in range(y, y + 3):
                    for x1 in range(x, x + 3):
                        if maze[y1, x1] & (1 << 1) or maze[y1, x1] & (1 << 2):
                            open_check = False
                            break
                if open_check:
                    return open_check
        return False

    def imperfect_maze(
        self,
        maze: n.ndarray,
        record: bool = False,
    ) -> Union[n.ndarray, Tuple[n.ndarray, List[Dict[str, Any]]]]:
        """Introduce imperfect mazes by randomly removing walls.
        """
        actions: Optional[List[Dict[str, Any]]] = [] if record else None
        pattern_coords: Set[Tuple[int, int]] = self.pattern_42()
        directions: List[Tuple[int, int, int, int]] = [
            (0, -1, 0, 2),
            (1, 0, 1, 3),
            (0, 1, 2, 0),
            (-1, 0, 3, 1),
        ]
        removed_walls: Set[Tuple[int, int]] = set()

        total_walls: int = int((self.width * self.height) * 0.05)
        max_tries: int = self.width * self.height
        walls: int = 0
        tries: int = 0
        while tries < max_tries and walls < total_walls:
            tries += 1
            x: int = random.randint(0, self.width - 1)
            y: int = random.randint(0, self.height - 1)
            dx: int
            dy: int
            wall: int
            neighbor_wall: int
            dx, dy, wall, neighbor_wall = random.choice(directions)
            nx: int = dx + x
            ny: int = dy + y
            if not (0 <= nx < self.width and 0 <= ny < self.height):
                continue
            if (nx, ny) in pattern_coords or (x, y) in pattern_coords:
                continue
            if bool(maze[y, x] & (1 << wall)):
                maze[y, x] &= ~(1 << wall)
                maze[ny, nx] &= ~(1 << neighbor_wall)
                walls += 1
                removed_walls.add((x, y))
                if self.imperfection_helper(maze):
                    maze[y, x] |= (1 << wall)
                    maze[ny, nx] |= (1 << neighbor_wall)
                    walls -= 1
                    removed_walls.remove((x, y))
                    if actions is not None:
                        actions.append({
                            'type': 'imperfect_carve',
                            'cell': (x, y),
                            'neighbor': (nx, ny),
                            'wall': wall,
                            'neighbor_wall': neighbor_wall,
                        })
        if record:
            assert actions is not None
            return maze, actions
        return maze

    def get_maze(self) -> n.ndarray:
        """Generate and return the maze.
        """
        result = self.iterative_backtracker()
        assert isinstance(result, n.ndarray)
        self.generated_maze = result
        if not self.perfect:
            imp_result = self.imperfect_maze(self.generated_maze)
            assert isinstance(imp_result, n.ndarray)
            self.generated_maze = imp_result
        return self.generated_maze

    def get_solution_path(self, generated_maze: n.ndarray) -> str:
        """find the solution path for the maze.
        """
        self.path = self.bfs(generated_maze)
        return self.path

    def get_entry(self) -> Tuple[int, int]:
        """Return the entry coordinates."""
        return self.entry

    def get_exit(self) -> Tuple[int, int]:
        """Return the exit coordinates."""
        return self.exit
