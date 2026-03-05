import numpy as n
import random
from typing import Any, List, Dict, Union, Optional
from config_validator import Maze_config_analyzer as ConfigAnalyzer
from backtracker import MazeGenerationParts as MazeGenParts
from maze_renderer import Render_Maze


def main():
    parsed_config = ConfigAnalyzer.parse_and_validate()
    entry = tuple(parsed_config["ENTRY"].values())
    exit_ = tuple(parsed_config["EXIT"].values())
    width = parsed_config["WIDTH"]
    height = parsed_config["HEIGHT"]
    output_file = parsed_config["OUTPUT_FILE"]
    perfect = parsed_config["PERFECT"]
    seed = parsed_config["SEED"]
    while True:
        if seed:
            random.seed(seed)

        compass = ["North", "East", "South", "West"]
        grid = n.full((height, width), 0xF, dtype=n.uint8)

        generated_maze, gen_actions = MazeGenParts.iterative_backtracker(
            grid, height, width, entry, compass, exit_, seed, record=True
        )

        if not perfect:
            generated_maze, imp_actions = MazeGenParts.imperfect_maze(
                generated_maze, height, width, record=True
            )
        else:
            imp_actions = []

        path = MazeGenParts.bfs(generated_maze, entry, exit_)
        renderer = Render_Maze(generated_maze, entry, exit_, path)
        regenerate = renderer.animate(gen_actions + imp_actions)

        if not regenerate:
            break

if __name__ == "__main__":
   main()

