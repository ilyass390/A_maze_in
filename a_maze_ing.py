import numpy as n
import sys
import random
sys.setrecursionlimit(50000)

class A_Maze_Ing:
    def __init__(self):
        tokens = self.Maze_Config_Analyzer.Combining_rules()
        self.width = tokens["WIDTH"]
        self.height = tokens["HEIGHT"]
        self.entry = tokens["ENTRY"]
        self.exit = tokens["EXIT"]
        self.output_file = tokens["OUTPUT_FILE"]
        self.seed = tokens["SEED"]
        self.perfect = tokens["PERFECT"]
        self.flawed = tokens["FLAWED"]
        self.maze = self.Recursive_Backtracker(self)

    class Maze_Config_Analyzer:
        @staticmethod
        def comment_lines_trigger(line: str ) -> bool:
            return line is None or line == "" or line[0] == "#"
        @staticmethod
        def empty_outputf_trigger(output_file: str) -> bool:
            if output_file is None or output_file == "":
                return True
            for i in output_file:
                if i != " ":
                    return False
            return True
        @staticmethod
        def validate_lines(config_lines: list[str]) -> dict[str:int | str]:
            tokens_to_return = {"WIDTH": 0, "HEIGHT": 0, "EXIT": {"x": 0, "y": 0},"ENTRY": {"x": 0, "y": 0}, "OUTPUT_FILE": None, "PERFECT": 0, "FLAWED": 0, "SEED": None}
            tokens_count = {"WIDTH": 0, "HEIGHT": 0, "EXIT": 0,"ENTRY": 0, "OUTPUT_FILE": 0, "PERFECT": 0, "FLAWED": 0, "SEED": 0}
            tokens_name = ["WIDTH", "HEIGHT", "EXIT","ENTRY", "OUTPUT_FILE", "PERFECT", "FLAWED", "SEED"]
            for line in config_lines:
                if A_Maze_Ing.Maze_Config_Analyzer.comment_lines_trigger(line):
                    continue
                for token in tokens_name:
                    if token == "WIDTH" and token in line:
                        tokens_count["WIDTH"] += 1
                        tokens_to_return["WIDTH"] = int(line.split("=")[1])
                    elif token == "HEIGHT" and token in line:
                        tokens_count["HEIGHT"] += 1
                        tokens_to_return["HEIGHT"] = int(line.split("=")[1])
                    elif token == "OUTPUT_FILE" and token in line:
                        tokens_count["OUTPUT_FILE"] += 1
                        tokens_to_return["OUTPUT_FILE"] = line.split("=")[1]
                        if len(tokens_to_return["OUTPUT_FILE"].split()) > 1:
                            raise ValueError(f"Invalid file name {tokens_to_return['OUTPUT_FILE']}")
                        else:
                            tokens_to_return["OUTPUT_FILE"] = tokens_to_return["OUTPUT_FILE"].strip()
                    elif token == "PERFECT" and token in line:
                        tokens_count["PERFECT"] += 1
                        tokens_to_return["PERFECT"] = line.split("=")[1]
                    elif token == "EXIT" and token in line:
                        tokens_count["EXIT"] += 1
                        x, y = line.split("=")[1].split(",")
                        tokens_to_return["EXIT"]["x"] = int(x)
                        tokens_to_return["EXIT"]["y"] = int(y)
                    elif token == "ENTRY" and token in line:
                        tokens_count["ENTRY"] += 1
                        x, y = line.split("=")[1].split(",")
                        tokens_to_return["ENTRY"]["x"] = int(x)
                        tokens_to_return["ENTRY"]["y"] = int(y)
                    elif token == "FLAWED" and token in line:
                        tokens_count["FLAWED"] += 1
                        try:
                            tokens_to_return["FLAWED"] = int(line.split("=")[1])
                        except ValueError:
                            tokens_to_return["FLAWED"] = None
                    elif token == "SEED" and token in line:
                        tokens_count["SEED"] += 1
                        try:
                            tokens_to_return["SEED"] = int(line.split("=")[1])
                        except ValueError:
                            tokens_to_return["SEED"] = None
            for token in tokens_count:
                if tokens_count[token] > 1:
                    raise ValueError(f"Parsing Error: Too many tokens of the same aspect {tokens_count[token]}")
            return tokens_to_return

        @staticmethod
        def validate_tokens(config_tokens: dict) -> None:
            width = config_tokens["WIDTH"]
            height = config_tokens["HEIGHT"]
            if A_Maze_Ing.Maze_Config_Analyzer.empty_outputf_trigger(config_tokens["OUTPUT_FILE"]) and not None:
                raise ValueError ("Output file name cannot be Empty/None.")
            if config_tokens["PERFECT"] not in ("True" ,"False") and not None:
                raise ValueError ("Acceptable 'Perfect' format is 'True' or 'False'.")
            if config_tokens['ENTRY']['x'] >= width or config_tokens["ENTRY"]["y"] >= height:
                raise ValueError(f'Invalid Entry: ({config_tokens["ENTRY"]["x"]}, {config_tokens["ENTRY"]["y"]}), width/height=({width}, {height})')
            if config_tokens["EXIT"]["x"] >= width or config_tokens["EXIT"]["y"] >= height:
                raise ValueError(f'Invalid Exit: ({config_tokens["EXIT"]["x"]}, {config_tokens["EXIT"]["y"]}), width/height=({width}, {height})')
            if config_tokens['ENTRY']['x'] == config_tokens['EXIT']['x'] and config_tokens['ENTRY']['y'] == config_tokens['EXIT']['y']:
                raise ValueError(f"Entry and Exit cannot share the same point: "
                                f"Entry=({config_tokens['ENTRY']['x']}, {config_tokens['ENTRY']['y']}), "
                                f"Exit=({config_tokens['EXIT']['x']}, {config_tokens['EXIT']['y']})")
        @staticmethod
        def Combining_rules() -> dict:
            try:
                if len(sys.argv) > 2:
                    raise ValueError("Too many arguments provided. Only the configuration file path is required.")
                elif len(sys.argv) < 2:
                    raise ValueError("No configuration file provided. Please provide the path to the configuration file.")
                config_file = sys.argv[1]
                with open(config_file, "r") as f:
                    config_lines = [line.strip() for line in f]
                tokens = A_Maze_Ing.Maze_Config_Analyzer.validate_lines(config_lines)
                A_Maze_Ing.Maze_Config_Analyzer.validate_tokens(tokens)
                return tokens
            except Exception as e:
                print("An Error Occured:")
                print(f"\nType: {e.__class__.__name__}\nDetails: {e}")
                sys.exit(1)  
                
    class Recursive_Backtracker:
        def __init__(self, maze):
            self.maze = maze 
        def pattern_42(self):
            return {(0,0), (2,0), (0,1), (2,1), (0,2), (1,2), (2,2), (2,3), (2,4), (4,0), (5,0), (6,0), (6,1), (4,2), (5,2), (6,2), (4,3), (4,4), (5,4), (6,4)}         # '2'
        def shape_patter_42(self, maze):
            pattern = self.pattern_42()
            pattern_height = max(y for _, y in pattern) + 1
            pattern_width = max(x for x, _ in pattern) + 1
            half_grid_h = (maze.shape[0] - 1) // 2
            half_grid_w = (maze.shape[1] - 1) // 2
            
            entry_tuple = (self.maze.entry["x"], self.maze.entry["y"])
            exit_tuple = (self.maze.exit["x"], self.maze.exit["y"])
            for y in range (1, half_grid_h - pattern_height):
                for x in range (1, half_grid_w - pattern_width):
                    possible_cells = {(x + pattern_x, y + pattern_y) for pattern_x, pattern_y in pattern}
                    if entry_tuple not in possible_cells and exit_tuple not in possible_cells:
                        return x, y
            raise ValueError(f"Cannot shape the pattern, Maze is too small ({self.maze.height}, {self.maze.width})")
            
            
        def grid_creator(self, height: int, width: int) -> n.ndarray:
            maze = n.ones((height, width), dtype=int)
            return maze
        
        def recursive_backtracker(self, maze, enx, eny, height, width, exx, exy, path_way):
            maze[eny, enx] = 0
            path = (enx, eny) == (exx, exy)
            directions = ["north", "south", "west", "east"]
            random.shuffle(directions)
            for move in directions:
                if move == "north" and eny > 1 and maze[eny-2, enx] == 1:
                    maze[eny-1, enx] = 0
                    if self.recursive_backtracker(maze, enx, eny-2, height, width, exx, exy, path_way)[0]:
                        path = True
                        maze[eny-1, enx] = 42
                        path_way.append("N")  # Went north during exploration
                elif move == "south" and eny < height - 2 and maze[eny+2, enx] == 1:
                    maze[eny+1, enx] = 0
                    if self.recursive_backtracker(maze, enx, eny+2, height, width, exx, exy, path_way)[0]:
                        path = True
                        maze[eny+1, enx] = 42
                        path_way.append("S")  # Went south during exploration
                elif move == "west" and enx > 1 and maze[eny, enx-2] == 1:
                    maze[eny, enx-1] = 0
                    if self.recursive_backtracker(maze, enx-2, eny, height, width, exx, exy, path_way)[0]:
                        path = True
                        maze[eny, enx-1] = 42
                        path_way.append("W")  # Went west during exploration
                elif move == "east" and enx < width - 2 and maze[eny, enx+2] == 1:
                    maze[eny, enx+1] = 0
                    if self.recursive_backtracker(maze, enx+2, eny, height, width, exx, exy, path_way)[0]:
                        path = True
                        maze[eny, enx+1] = 42
                        path_way.append("E")  # Went east during exploration
            if path:
                maze[eny, enx] = 42
            return path, path_way
        
        def generate_maze(self, height: int, width: int, entry_point: tuple, exit_point: tuple) -> n.ndarray:
    
            maze = self.grid_creator(height, width)
            
            entry_x , entry_y = entry_point
            exit_x , exit_y = exit_point
            
            if entry_x == 0 or entry_y == 0 or entry_x >= width - 1 or entry_y >= height - 1:
                raise ValueError(f"Invalid Entry ({entry_x}, {entry_y}): entry cannot be on the maze boundary.")
            if exit_x == 0 or exit_y == 0 or exit_x >= width - 1 or exit_y >= height - 1:
                raise ValueError(f"Invalid Exit ({exit_x}, {exit_y}): exit cannot be on the maze boundary.")
            
            exit_x = exit_x if exit_x % 2 != 0 else exit_x + 1
            exit_y = exit_y if exit_y % 2 != 0 else exit_y + 1


            entry_x = entry_x if entry_x % 2 != 0 else entry_x + 1
            entry_y = entry_y if entry_y % 2 != 0 else entry_y + 1
            
            entry_x = min(entry_x, width - 2)
            entry_y = min(entry_y, height - 2)
            
            exit_x = min(exit_x, width - 2)
            exit_y = min(exit_y, height - 2)
            valid_point = self.shape_patter_42(maze)
            if valid_point:
                pattern = self.pattern_42()
                x, y = valid_point
                for pattern_x, pattern_y in pattern:
                    valid_cell_x = (x + pattern_x) * 2 + 1
                    valid_cell_y = (y + pattern_y) * 2 + 1
                    maze[valid_cell_y, valid_cell_x] = 0xf
            path_way = []
            self.recursive_backtracker(maze, entry_x, entry_y, height, width, exit_x, exit_y, path_way)
            maze[entry_y, entry_x] = 0xE
            maze[exit_y, exit_x] = 0xE2
            
            
            return maze, path_way
        
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
                entry  = (self.maze.entry["x"], self.maze.entry["y"],)
                exit = (self.maze.exit["x"], self.maze.exit["y"],)
                perfect = True if 'True' in self.maze.perfect else False
                flawed = self.maze.flawed
                seed = self.maze.seed
                height = self.maze.height
                width = self.maze.width
                
                if flawed is None:
                    flawed = 0
                if seed is not None:
                    random.seed(seed)
                if width % 2 == 0:
                    width += 1
                if height % 2 == 0:
                    height += 1
                
                
                self.maze.width = width
                self.maze.height = height
                
                maze, path_way = self.generate_maze(height, width, entry, exit)
                if not perfect:
                    maze = self.imperfect_maze(maze, height, width, flawed)
                
                return maze, path_way
            except Exception as e:
                print(f"Error: {e}")
                sys.exit(1)

    @staticmethod
    def maze_printer(maze):
        
        RESET = "\033[0m"
        WALL  = "\033[40m  "           
        PATH  = "\033[48;5;254m  "    
        SYM   = "\033[48;5;250m░░"    
        START = "\033[48;5;129m  "    
        END   = "\033[48;5;196m  "
        
        mapping = {
            0: PATH,
            1: WALL,
            0xE: START,
            0xE2: END,
            42: SYM
        }
        for row in maze:
            for cell in row:
                print(mapping.get(cell, PATH), end="")
            print(RESET)
    @staticmethod
    def maze_hexadecimal(maze, output_file, height, width, entry_p, exit_p, path_way):
        path_from_entry_to_exit = list(reversed(path_way))
        
        with open(output_file, "w+") as f:
            for y in range(1, height-1 , 2):  
                row_cells = []
                for x in range(1, width-1, 2):  
                    cell_hex = 0
                    if maze[y-1][x] == 1: cell_hex += 1 #North
                    if maze[y+1][x] == 1: cell_hex += 4 #South
                    if maze[y][x+1] == 1: cell_hex += 2 #East
                    if maze[y][x-1] == 1: cell_hex += 8 #West
                    row_cells.append(hex(cell_hex)[2:].upper())
                print("".join(row_cells), file=f)
            enx, eny, = entry_p["x"], entry_p["y"]
            exx, exy, = exit_p["x"], exit_p["y"]
            print(f"\n{enx},{eny}", file=f, end="\n")
            print(f"{exx},{exy}", file=f, end="\n")
            for direction in path_from_entry_to_exit:
                print(direction, file=f, end="")
            print(file=f, end="\n")
            
    def generate_maze(self):
        maze, path_way = self.maze.maze_bringer()
        A_Maze_Ing.maze_hexadecimal(maze, self.output_file, self.height, self.width, self.entry, self.exit, path_way)
        A_Maze_Ing.maze_printer(maze)
        
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
