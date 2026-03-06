import numpy as n
import random
from typing import Any, List, Dict, Union, Optional
from config_validator import Maze_config_analyzer as ConfigAnalyzer
from MazeGenerator_engine import MazeGenerator as MazeGen
from maze_renderer import Render_Maze


class PyMaze:
    def __init__(self):
        self.imp_actions = []
    def generate_maze(self, height: int, width: int, entry: tuple, exit_: tuple, perfect: bool, seed: Optional[int] = None, record: bool = False):
        compass = ["North", "East", "South", "West"]
        grid = n.full((height, width), 0xF, dtype=n.uint8)
        maze_generator = MazeGen(height, width, entry, exit_, perfect, None, None)
        generated_maze, actions = maze_generator.iterative_backtracker(
            grid, compass, record=record
        )
        if seed is not None:
            random.seed(seed)

        if not perfect:
            generated_maze, self.imp_actions = maze_generator.imperfect_maze(generated_maze, height, width, record=True)

        path = maze_generator.bfs(generated_maze)
        return generated_maze, path, actions

    def maze_hexadecimal(self, output_file: str, generated_maze: n.ndarray, entry: tuple, exit_: tuple, path: List[tuple]):
        with open(output_file, "w") as f:
            for y in range(generated_maze.shape[0]):  
                row_cells = []
                for x in range(generated_maze.shape[1]):  
                    cell_hex = generated_maze[y, x]
                    row_cells.append(hex(cell_hex)[2:].upper())
                print("".join(row_cells), file=f)
            enx, eny = entry
            exx, exy = exit_
            print(f"\n{enx},{eny}", file=f, end="\n")
            print(f"{exx},{exy}", file=f, end="\n")
            print(f"{path}", file=f, end="\n")


def main():
    parsed_config = ConfigAnalyzer.parse_and_validate()
    entry = tuple(parsed_config["ENTRY"].values())
    exit_ = tuple(parsed_config["EXIT"].values())
    width = parsed_config["WIDTH"]
    height = parsed_config["HEIGHT"]
    output_file = parsed_config["OUTPUT_FILE"]
    perfect = parsed_config["PERFECT"]
    seed = parsed_config["SEED"]

    if seed:
        random.seed(str(seed))
    while True:
        compass = ["North", "East", "South", "West"]
        grid = n.full((height, width), 0xF, dtype=n.uint8)
        maze = PyMaze()
        generated_maze, path, actions = maze.generate_maze(height, width, entry, exit_, perfect, seed, record=True)
        maze.maze_hexadecimal(output_file, generated_maze, entry, exit_, path)

        
        renderer = Render_Maze(generated_maze, entry, exit_, path)
        regenerate = renderer.animate(actions + maze.imp_actions)
        renderer.display()
        if seed:
            random.seed()
        if not regenerate:
            break


if __name__ == "__main__":
    try:
        # main()
        print(n.__version__)
    except KeyboardInterrupt:
       exit(0)
    except Exception as e:
        print(f"Error during program execution: {e.__class__.__name__} - {e}")

