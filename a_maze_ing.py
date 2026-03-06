import numpy as n
import random
from typing import List, Optional, Tuple
from config_validator import Maze_config_analyzer as ConfigAnalyzer
from mazegenerator_engine import MazeGenerator as MazeGen
from maze_renderer import Render_Maze


class PyMaze:
    """orchestrator for maze generation, solving, and display."""

    def __init__(self) -> None:
        """Initialise with an empty imperfection-action list."""
        self.imp_actions: List = []

    def generate_maze(
        self,
        height: int,
        width: int,
        entry: Tuple,
        exit_: Tuple,
        perfect: bool,
        seed: Optional[int] = None,
        record: bool = False,
    ) -> Tuple[n.ndarray, str, List]:
        """Generate a maze, solve it, and return everything needed to render.
        """
        maze_generator: MazeGen = MazeGen(
            height,
            width,
            entry,
            exit_,
            perfect,
            None,
            None
            )
        generated_maze: n.ndarray
        actions: List
        generated_maze, actions = maze_generator.iterative_backtracker(
            record=record
        )
        if seed is not None:
            random.seed(seed)

        if not perfect:
            imp_result = maze_generator.imperfect_maze(
                generated_maze, record=True
            )
            assert isinstance(imp_result, tuple)
            generated_maze, self.imp_actions = imp_result

        path: str = maze_generator.bfs(generated_maze)
        return generated_maze, path, actions

    def maze_hexadecimal(
        self,
        output_file: str,
        generated_maze: n.ndarray,
        entry: Tuple,
        exit_: Tuple,
        path: str,
    ) -> None:
        """Write the maze to a file in hexadecimal format.
        """
        with open(output_file, "w") as f:
            for y in range(generated_maze.shape[0]):
                row_cells: List[str] = []
                for x in range(generated_maze.shape[1]):
                    cell_hex: int = generated_maze[y, x]
                    row_cells.append(hex(cell_hex)[2:].upper())
                print("".join(row_cells), file=f)
            enx: int
            eny: int
            exx: int
            exy: int
            enx, eny = entry
            exx, exy = exit_
            print(f"\n{enx},{eny}", file=f, end="\n")
            print(f"{exx},{exy}", file=f, end="\n")
            print(f"{path}", file=f, end="\n")


def main() -> None:
    """Entry point: parse config, generate, render, and loop on regenerate."""
    parsed_config: dict = ConfigAnalyzer.parse_and_validate()
    entry: Tuple = tuple(parsed_config["ENTRY"].values())
    exit_: Tuple = tuple(parsed_config["EXIT"].values())
    width: int = parsed_config["WIDTH"]
    height: int = parsed_config["HEIGHT"]
    output_file: str = parsed_config["OUTPUT_FILE"]
    perfect: bool = parsed_config["PERFECT"]
    seed: Optional[int] = parsed_config["SEED"]

    if seed:
        random.seed(str(seed))
    while True:
        maze: PyMaze = PyMaze()
        generated_maze: n.ndarray
        path: str
        actions: List
        generated_maze, path, actions = maze.generate_maze(
            height, width, entry, exit_, perfect, seed, record=True
        )
        maze.maze_hexadecimal(output_file, generated_maze, entry, exit_, path)

        renderer: Render_Maze = Render_Maze(generated_maze, entry, exit_, path)
        regenerate: bool = renderer.animate(actions + maze.imp_actions)
        renderer.display()
        if seed:
            random.seed()
        if not regenerate:
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit(0)
    except Exception as e:
        print(f"Error during program execution: {e.__class__.__name__} - {e}")
