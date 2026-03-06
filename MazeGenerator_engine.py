import random
from typing import List, Tuple, Optional, Set, Dict, Any, Union
import numpy as n
class MazeGenerator:
        def __init__(
            self,
            height: int,
            width: int,
            entry: Tuple[int, int],
            exit_: Tuple[int, int],
            perfect: bool,
            output_file: Optional[str],
            seed: Optional[int]
        ) -> None:
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
            base_pattern = {
                            (0,0) ,(0, 1), (0, 2), (1, 2), (2, 2), (2, 3), (2, 4), 
                            (4, 0), (5, 0), (6, 0), (6, 1),  (4, 2), (5, 2), (6, 2), (4, 3),
                            (4,4), (5,4), (6,4)
                            }
            pattern_width = max(x for x, _ in base_pattern) + 1
            pattern_height = max(y for _, y in base_pattern) + 1
            if self.height <= pattern_height or self.width <= pattern_width:
                print(f"cannot place pattern on the maze {self.width}/{self.height}")
                exit(0)
            scale_x = self.width // pattern_width
            scale_y = self.height // pattern_height
            scale = max(1, min(scale_x, scale_y) // 25)
            pattern_height = pattern_height * scale
            pattern_width = pattern_width * scale
            middle_x = (self.width - pattern_width) // 2
            middle_y = (self.height - pattern_height) // 2
            scaled_pattern = set()
            for bx, by in base_pattern:
                for sx in range(scale):
                    for sy in range(scale):
                        x = bx * scale + sx + middle_x
                        y = by * scale + sy + middle_y
                        scaled_pattern.add((x, y))
            return scaled_pattern
        
        def iterative_backtracker(
            self,
            maze: n.ndarray,
            compass: List[str],
            record: bool = False
        ) -> Union[n.ndarray, Tuple[n.ndarray, List[Dict[str, Any]]]]:
            direction_map = {
                "North": (0, -1, 1, 4),
                "South": (0,  1, 4, 1),
                "West":  (-1, 0, 8, 2),
                "East":  (1,  0, 2, 8),
            }

            actions = [] if record else None
            pattern_coords = self.pattern_42()
            enx, eny = self.entry
            random.shuffle(compass)
            stack_simulation = [(enx, eny, compass.copy())]
            visited_cells = {(enx, eny)}

            if record:
                actions.append({'type': 'visit', 'cell': (enx, eny), 'stack_size': 1})

            for cord in pattern_coords:
                if cord == self.entry or cord == self.exit:
                    print(f"Entry/Exit spotted on pattern")
                    exit(0)
                visited_cells.add(cord)
                x, y = cord
                maze[y, x] = 0xF
                if record:
                    actions.append({'type': 'pattern', 'cell': (x, y)})

            while stack_simulation:
                x, y, cell_compass = stack_simulation[-1]
                moved = False

                while cell_compass:
                    move = cell_compass.pop(0)
                    dx, dy, wall, neighbor_wall = direction_map[move]
                    nx, ny = x + dx, y + dy

                    if (0 <= nx < self.width and 0 <= ny < self.height
                            and (nx, ny) not in visited_cells):
                        maze[y, x] -= wall
                        maze[ny, nx] -= neighbor_wall
                        visited_cells.add((nx, ny))

                        if record:
                            actions.append({
                                'type': 'carve',
                                'from_cell': (x, y),
                                'to_cell': (nx, ny),
                                'direction': move[0],
                                'stack_size': len(stack_simulation)
                            })
                            actions.append({
                                'type': 'visit',
                                'cell': (nx, ny),
                                'stack_size': len(stack_simulation) + 1
                            })

                        fresh_compass = compass.copy()
                        random.shuffle(fresh_compass)
                        stack_simulation.append((nx, ny, fresh_compass))
                        moved = True
                        break

                if not moved:
                    if record:
                        actions.append({
                            'type': 'backtrack',
                            'from_cell': (x, y),
                            'stack_size': len(stack_simulation) - 1
                        })
                    stack_simulation.pop()

            return (maze, actions) if record else maze

        def bfs(self, maze: n.ndarray) -> str:
            directions = {0: (0, -1, 'N'), 1: (1, 0, 'E'), 2: (0, 1, 'S'), 3: (-1, 0, 'W')}
            enx, eny = self.entry
            exx, exy = self.exit
            queue = [(enx, eny, "")]
            visited = {(enx, eny)}
            height, width = maze.shape
            while queue:
                x, y, path = queue.pop(0)
                

                for direction, (dx, dy, compass) in directions.items():
                    if (x, y) == (exx, exy):
                        return path + compass
                    if not bool(maze[y, x] & (0x1 << direction)):
                        nx, ny = x + dx, y + dy
                        
                        if (0 <= nx < width and 
                            0 <= ny < height and
                            (nx, ny) not in visited):

                            visited.add((nx, ny))
                            queue.append((nx, ny, path + compass))

            return "No path found"
        def imperfection_helper(self, maze: n.ndarray) -> bool:
            for y in range(self.height - 2):
                for x in range(self.width - 2):
                    open_check = True
                    for y1 in range (y, y + 3):
                        for x1 in range (x, x + 3):
                            if maze[y1, x1] & (1 << 1) or maze[y1, x1] & (1 << 2):
                                open_check = False
                                break
                    if open_check:
                        return open_check
            return False

        def imperfect_maze(self, maze: n.ndarray, record: bool = False) -> n.ndarray:
            actions = [] if record else None
            pattern_coords = self.pattern_42()
            directions = [(0, -1, 0, 2), (1, 0, 1, 3), (0, 1, 2, 0), (-1, 0, 3, 1)]
            removed_walls = set()

            total_walls = int((self.width * self.height) * 0.25)
            max_tries = self.width * self.height
            walls = 0
            tries = 0
            while tries < max_tries and walls < total_walls:
                tries += 1
                x , y = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
                dx, dy , wall, neighbor_wall = random.choice(directions)
                nx = dx + x
                ny = dy + y
                if not (0 <= nx < self.width and 0 <= ny < self.height):
                    continue
                if (nx, ny) in pattern_coords or (x, y) in pattern_coords:
                    continue
                if bool(maze[y, x] & (1 << wall)):
                    maze[y,x] &= ~(1 << wall)
                    maze[ny,nx] &= ~(1 << neighbor_wall)
                    walls += 1
                    removed_walls.add((x, y))
                    if self.imperfection_helper(maze):
                        maze[y,x] |= (1 << wall)
                        maze[ny,nx] |= (1 << neighbor_wall)
                        walls -= 1
                        removed_walls.remove((x, y))
                        if record:
                            actions.append({
                                'type': 'imperfect_carve',
                                'cell': (x, y),
                                'neighbor': (nx, ny),
                                'wall': wall,
                                'neighbor_wall': neighbor_wall
                            })
            if record:
                return maze, actions
            return maze
        def get_maze(self) -> n.ndarray:
            compass = ["North", "East", "South", "West"]
            maze = n.full((self.height, self.width), 0xF,dtype=n.uint8)
            self.generated_maze = self.iterative_backtracker(maze, compass, True)
            if self.perfect == False:
                self.generated_maze = self.imperfect_maze(self.generated_maze)
            return self.generated_maze
        def get_solution_path(self, generated_maze: n.ndarray) -> str:
            self.path = self.bfs(generated_maze)
            return self.path
        def get_entry(self) -> Tuple[int, int]:
            return self.entry
        def get_exit(self) -> Tuple[int, int]:
            return self.exit
