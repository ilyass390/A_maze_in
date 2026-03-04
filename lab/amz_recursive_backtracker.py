import numpy as n
import sys
import random

from amz_parsing import Combining_rules
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt


def grid_creator(height: int, width: int) -> n.ndarray:
    
    maze = n.ones((height, width), dtype=int)
    return maze

def recursive_backtracker(maze, enx, eny, height, width, exx, exy) -> None:
    maze[eny, enx] = 0
    path = (enx, eny) == (exx, exy)
    directions = ["north", "south", "west", "east"]
    random.shuffle(directions)
    for move in directions:
        if move == "north" and eny > 1 and maze[eny-2, enx] == 1:
            maze[eny-1, enx] = 0
            if recursive_backtracker(maze, enx, eny-2, height, width, exx, exy):
                path = True
                maze[eny-1, enx] = 42
        elif move == "south" and eny < height - 2 and maze[eny+2, enx] == 1:
            maze[eny+1, enx] = 0
            if recursive_backtracker(maze, enx, eny+2, height, width, exx, exy):
                path = True
                maze[eny+1, enx] = 42
        elif move == "west" and enx > 1 and maze[eny, enx-2] == 1:
            maze[eny, enx-1] = 0
            if recursive_backtracker(maze, enx-2, eny, height, width, exx, exy):
                path = True
                maze[eny, enx-1] = 42
        elif move == "east" and enx < width - 2 and maze[eny, enx+2] == 1:
            maze[eny, enx+1] = 0
            if recursive_backtracker(maze, enx+2, eny, height, width, exx, exy):
                path = True
                maze[eny, enx+1] = 42
    if path:
        maze[eny, enx] = 42
    return path

def generate_maze(height: int, width: int, entry_point: tuple, exit_point) -> n.ndarray:
    
    maze = grid_creator(height, width)
    
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
    
    recursive_backtracker(maze, entry_x, entry_y, actual_height, actual_width, exit_x, exit_y)
    
    if maze[entry_point[1], entry_point[0]] == 0:
        maze[entry_point[1], entry_point[0]] = 42
    if maze[exit_point[1], exit_point[0]] == 0:
        maze[exit_point[1], exit_point[0]] = 42
    
    return maze


def imperfect_maze(maze, height, width, flawed):
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

def maze_bringer(height, width, entry_point, exit_point, perfect, flawed, seed, output_file):
    try:
        entry  = (entry_point["x"], entry_point["y"],)
        exit = (exit_point["x"], exit_point["y"],)
        perfect = True if 'True' in perfect else False
        flawed = flawed
        seed = seed
        if flawed is None:
            flawed = 0
        if seed is not None:
            random.seed(seed)
        if width % 2 == 0:
            width += 1
        if height % 2 == 0:
            height += 1
        
        maze = generate_maze(height, width, entry, exit)
        if not perfect:
            maze = imperfect_maze(maze, height, width, flawed)
        
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
        
        plt.figure(figsize=(10, 10))
        cmap = mcolors.ListedColormap(['black', 'lime', 'white'])
        bounds = [0, 0.25, 0.75, 1.0]
        norm = mcolors.BoundaryNorm(bounds, cmap.N)
        
        plt.imshow(display_maze, cmap=cmap, norm=norm) 
        
        plt.title(f"Maze {maze.shape[1]}x{maze.shape[0]} (Green = Path)")
        plt.axis('off') 
        
        plt.savefig("maze.png")
        print(f"Maze visualization saved to maze.png")

if __name__ == "__main__":
    try:
        tokens = Combining_rules()
        height = tokens['HEIGHT']
        width = tokens['WIDTH']
        entry_point = (tokens['ENTRY']["x"], tokens['ENTRY']["y"],)
        exit_point = (tokens['EXIT']["x"], tokens['EXIT']["y"],)
        perfect = True if 'True' in tokens['PERFECT'] else False
        flawed = tokens["FLAWED"]
        seed = tokens["SEED"]
        if flawed is None:
            flawed = 0
        if seed is not None:
            random.seed(seed)
        if width % 2 == 0:
            width += 1
        if height % 2 == 0:
            height += 1
        
        maze = generate_maze(height, width, entry_point, exit_point)
        if not perfect:
            maze = imperfect_maze(maze, height, width, flawed)
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        display_maze = n.copy(maze)
        display_maze = display_maze.astype(float)
        display_maze[maze == 42] = 0.5 
        display_maze[maze == 0] = 1.0   
        display_maze[maze == 1] = 0.0  
        
        plt.figure(figsize=(10, 10))
        cmap = mcolors.ListedColormap(['black', 'lime', 'white'])
        bounds = [0, 0.25, 0.75, 1.0]
        norm = mcolors.BoundaryNorm(bounds, cmap.N)
        
        plt.imshow(display_maze, cmap=cmap, norm=norm) 
        
        plt.title(f"Maze {maze.shape[1]}x{maze.shape[0]} (Green = Path)")
        plt.axis('off') 
        
        output_file = tokens["OUTPUT_FILE"]
        plt.savefig(output_file)
        print(f"Maze visualization saved to {output_file}")