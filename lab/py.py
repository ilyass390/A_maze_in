import random
class MazeGenerationParts:
    # ... existing code ...
    
    @staticmethod
    def make_imperfect(maze, height, width):
        """
        Make maze imperfect by removing 25% of cell count worth of walls.
        """
        # Calculate walls to remove (25% of cells)
        total_cells = height * width
        num_walls_to_remove = int(total_cells * 0.25)
        
        directions = [(0, -1, 0, 2), (1, 0, 1, 3), (0, 1, 2, 0), (-1, 0, 3, 1)]
        
        removed = 0
        attempts = 0
        max_attempts = num_walls_to_remove * 100
        
        while removed < num_walls_to_remove and attempts < max_attempts:
            attempts += 1
            
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            dx, dy, my_wall, neighbor_wall = random.choice(DIRECTIONS)
            nx, ny = x + dx, y + dy
            
            if not (0 <= nx < width and 0 <= ny < height):
                continue
            
            has_wall = bool(maze[y, x] & (1 << my_wall))
            
            if has_wall:
                maze[y, x] &= ~(1 << my_wall)
                maze[ny, nx] &= ~(1 << neighbor_wall)
                removed += 1
        
        return maze