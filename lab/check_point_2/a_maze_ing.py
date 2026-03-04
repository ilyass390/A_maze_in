from turtle import width
from amz_parsing import Combining_rules
# import amz_recursive_backtracker as maze
import numpy as n
import sys
import random
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
sys.setrecursionlimit(50000)

class A_Maze_Ing:
    def __init__(self):
        tokens = Combining_rules()
        self.width = tokens["WIDTH"]
        self.height = tokens["HEIGHT"]
        self.entry = tokens["ENTRY"]
        self.exit = tokens["EXIT"]
        self.output_file = tokens["OUTPUT_FILE"]
        self.seed = tokens["SEED"]
        self.perfect = tokens["PERFECT"]
        self.flawed = tokens["FLAWED"]
        self.maze = self.Recursive_Backtracker(self) 
        
    class Recursive_Backtracker:
        def __init__(self, outer):
            self.outer = outer 
        
        def grid_creator(self, height: int, width: int) -> n.ndarray:
            maze = n.ones((height, width), dtype=int)
            return maze
        
        def recursive_backtracker(self, maze, enx, eny, height, width, exx, exy) -> None:
            maze[eny, enx] = 0
            path = (enx, eny) == (exx, exy)
            directions = ["north", "south", "west", "east"]
            random.shuffle(directions)
            for move in directions:
                if move == "north" and eny > 1 and maze[eny-2, enx] == 1:
                    maze[eny-1, enx] = 0
                    if self.recursive_backtracker(maze, enx, eny-2, height, width, exx, exy):
                        path = True
                        maze[eny-1, enx] = 42
                elif move == "south" and eny < height - 2 and maze[eny+2, enx] == 1:
                    maze[eny+1, enx] = 0
                    if self.recursive_backtracker(maze, enx, eny+2, height, width, exx, exy):
                        path = True
                        maze[eny+1, enx] = 42
                elif move == "west" and enx > 1 and maze[eny, enx-2] == 1:
                    maze[eny, enx-1] = 0
                    if self.recursive_backtracker(maze, enx-2, eny, height, width, exx, exy):
                        path = True
                        maze[eny, enx-1] = 42
                elif move == "east" and enx < width - 2 and maze[eny, enx+2] == 1:
                    maze[eny, enx+1] = 0
                    if self.recursive_backtracker(maze, enx+2, eny, height, width, exx, exy):
                        path = True
                        maze[eny, enx+1] = 42
            if path:
                maze[eny, enx] = 42
            return path
        
        def generate_maze(self, height: int, width: int, entry_point: tuple, exit_point) -> n.ndarray:
    
            maze = self.grid_creator(height, width)
            
            actual_height, actual_width = height, width
            entry_x , entry_y = entry_point
            exit_x , exit_y = exit_point
            
            exit_x = exit_x if exit_x % 2 != 0 else exit_x + 1
            exit_y = exit_y if exit_y % 2 != 0 else exit_y + 1


            entry_x = entry_x if entry_x % 2 != 0 else entry_x + 1
            entry_y = entry_y if entry_y % 2 != 0 else entry_y + 1
            
            entry_x = min(entry_x, actual_width - 2)
            entry_y = min(entry_y, actual_height - 2)
            
            exit_x = min(exit_x, actual_width - 2)
            exit_y = min(exit_y, actual_height - 2)
            
            self.recursive_backtracker(maze, entry_x, entry_y, actual_height, actual_width, exit_x, exit_y)
            
            if maze[entry_point[1], entry_point[0]] == 0:
                maze[entry_point[1], entry_point[0]] = 42
            if maze[exit_point[1], exit_point[0]] == 0:
                maze[exit_point[1], exit_point[0]] = 42
            
            return maze
        
        def imperfect_maze(self, maze, height, width, flawed):
            removeable_walls = []
            for y in range(1, height - 1):
                for x in range(1, width - 1):
                    if(maze[y,x] == 1):
                        if (maze[y+1, x] == 0 and maze[y-1, x] == 0) or (maze[y, x+1] == 0 and maze[y, x-1] == 0):
                            removeable_walls.append((y,x))
            random.shuffle(removeable_walls)
            for y, x in removeable_walls[:flawed]:
                maze[y, x] = 0
            return maze
        
        def maze_bringer(self):
            try:
                entry  = (self.outer.entry["x"], self.outer.entry["y"],)
                exit = (self.outer.exit["x"], self.outer.exit["y"],)
                perfect = True if 'True' in self.outer.perfect else False
                flawed = self.outer.flawed
                seed = self.outer.seed
                height = self.outer.height
                width = self.outer.width
                
                if flawed is None:
                    flawed = 0
                if seed is not None:
                    random.seed(seed)
                if width % 2 == 0:
                    width += 1
                if height % 2 == 0:
                    height += 1
                
                maze = self.generate_maze(height, width, entry, exit)
                if not perfect:
                    maze = self.imperfect_maze(maze, height, width, flawed)
                
                return maze
            except Exception as e:
                print(f"Error: {e}")
                sys.exit(1)
            finally:
                display_maze = n.copy(maze)
                display_maze = display_maze.astype(float)
                display_maze[maze == 42] = 0.5 
                display_maze[maze == 0] = 1.0   
                display_maze[maze == 1] = 0.0  
                
                # Dynamically calculate figure size based on maze dimensions
                aspect_ratio = width / height
                base_size = 10  # Base size for smaller dimension
                if aspect_ratio > 1:  # Width > Height
                    fig_width = base_size * aspect_ratio
                    fig_height = base_size
                else:  # Height >= Width
                    fig_width = base_size
                    fig_height = base_size / aspect_ratio
                
                plt.figure(figsize=(fig_width, fig_height))
                cmap = mcolors.ListedColormap(['black', 'lime', 'white'])
                bounds = [0, 0.25, 0.75, 1.0]
                norm = mcolors.BoundaryNorm(bounds, cmap.N)
                
                plt.imshow(display_maze, cmap=cmap, norm=norm) 
                
                plt.title(f"Maze {maze.shape[1]}x{maze.shape[0]} (Green = Path)")
                plt.axis('off') 
                
                plt.savefig("maaaze.png")
                print(f"Maze visualization saved to maaaze.png")
                
    def generate_maze(self):
        return self.maze.maze_bringer()
        
    def print_arguments(self):
        print(f"Height: {self.height}")
        print(f"Width: {self.width}")
        print(f"Entry Point: {self.entry}")
        print(f"Exit Point: {self.exit}")
        print(f"Output File: {self.output_file}")
        print(f"Seed: {self.seed}")
        print(f"Perfect: {self.perfect}")
        print(f"Flawed: {self.flawed}")
        
            
if __name__ == "__main__":
    maze = A_Maze_Ing()
    # maze.print_arguments()
    maze.generate_maze()
