*This project has been created as part of the 42 curriculum by iamessag, aymel-ha.*

# A-Maze-ing

## Description

**A-Maze-ing**, a terminal-based maze generation program written in Python. The goal of the project is to generate a perfect maze — one with no loops and exactly one path between any two cells — and render it interactively in the terminal using a dedicated graphic window or displayed on the terminal.

The maze is generated using an **iterative Depth-First Search (DFS)** algorithm, also known as Recursive Backtracking. The iterative approach was chosen over a recursive one to work around Python's default recursion limit, which becomes a problem for large mazes. The algorithm works by maintaining an explicit stack (simulating stack using list), visiting unvisited neighbors at random, and carving passages between cells until the entire grid has been explored.

---

## Instructions

### Requirements

- Python 3.x
- A Unix-like terminal with `curses` support (Linux / macOS)
- `make`

### Installation & Execution

Clone the repository and run:

```bash
make install
```

To run the program directly:

```bash
make run
```



This will generate a maze based on the configuration file and display it in the terminal.

To clean up generated files:

```bash
make clean
```

To check against flake8 and numpy
```bash
make lint
```


> **Note:** The terminal window must be large enough to display the maze. If the window is too small, the program will exit with an error.

---

## Resources

### Maze Generation

- Jamis Buck — Mazes for Programmers: Code Your Own Twisty Little Passages (Book) — explains a dozen maze generation algorithms (Binary Tree, Recursive Backtracker, Prim’s, Kruskal’s) with practical Ruby implementations.  It covers algorithm trade-offs, maze visualization, solving techniques like Dijkstra’s algorithm, and advanced topics such as mazes on hex grids, 3D surfaces

- [Maze Generation: Recursive Backtracking](https://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracking) __ A blog explaining Recursive Backtracking (4 minutes read).
- [Maze Generation — Recursive Backtracking by Aryan Abed-Esfahani](https://aryanab.medium.com/maze-generation-recursive-backtracking-5981bc5cc766) __ Another blog explaining maze generation using recursive backtracking in simple terms (9 minutes read). 
- [Maze Generation Algorithm — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm) — A solid overview of common maze generation techniques including DFS, Prim's, and Kruskal's.


### Python curses

- [Python `curses` — Official Documentation](https://docs.python.org/3/library/curses.html) — The standard library reference for the `curses` module.
- [Tech With Tim (Python Curses Tutorial)](https://youtube.com/playlist?list=PLzMcBGfZo4-n2TONAOImWL4sgZsmyMBc8&si=f6FfFq_bGAo-iZpQ) — A beginner-friendly guide to use `curses` in Python, Simple and short.

### Python Recursion Limit

- [Python `sys.setrecursionlimit` — Official Docs](https://docs.python.org/3/library/sys.html#sys.setrecursionlimit) — Documents the recursion limit and why iterative solutions are often preferred for deep traversals.
- [Stack Overflow — Iterative DFS vs Recursive DFS](https://stackoverflow.com/questions/9999784/iterative-dfs-vs-recursive-dfs-and-different-results) — Discussion on converting recursive DFS to an iterative version using an explicit stack.

### AI Usage

AI tools (specifically Claude) were used during this project for the following purposes:

- **Debugging help:** Identifying and resolving issues related to `curses` display bugs, off-by-one errors in the grid, and stack handling in the iterative DFS implementation.
- **Understanding concepts:** Clarifying how the Recursive Backtracking / DFS maze generation algorithm works conceptually, and understanding why Python's recursion limit causes issues with deep recursive traversals on large grids.

# Config File

The program is configured via a plain-text file. Each line follows the `KEY=VALUE` format. Here is the complete structure:

```
WIDTH=15
HEIGHT=15
EXIT=0,0
ENTRY=0,9
OUTPUT_FILE=maze.txt
PERFECT=true
```

| Field         | Type              | Description                                                                  |
|---------------|-------------------|------------------------------------------------------------------------------|
| `WIDTH`       | Integer           | Number of columns in the maze.                                               |
| `HEIGHT`      | Integer           | Number of rows in the maze.                                                  |
| `ENTRY`       | `row,col`         | Coordinates of the maze entry point.                                         |
| `EXIT`        | `row,col`         | Coordinates of the maze exit point.                                          |
| `OUTPUT_FILE` | String            | Path to the file where the maze will be saved.                               |
| `PERFECT`     | Boolean           | If `true`, generates a perfect maze (no loops, one unique path).             |

---

## Maze Generation Algorithm

The project uses an **iterative Depth-First Search (DFS)** algorithm, also known as Recursive Backtracking.

### How it works

1. Start at a random cell and push it onto a stack.
2. Mark the current cell as visited.
3. Pick a random unvisited neighbor, carve a passage to it, and push it onto the stack.
4. If no unvisited neighbors exist, pop the stack and backtrack.
5. Repeat until the stack is empty — the full grid has been visited.

### Why DFS?

DFS was chosen for its simplicity and reliability. Its logic is straightforward to implement, it reliably produces perfect mazes with a single solution, and it maps naturally to an explicit stack structure. More complex algorithms like Prim's or Wilson's were not necessary given the project's scope.

The recursive version of DFS was initially considered but was abandoned because Python's default recursion limit causes crashes on larger grids. The iterative version using an explicit stack solves this problem entirely without needing to raise the system limit.

---

## Reusable Components

The core of the project is encapsulated in a single self-contained module that is fully independent from the display layer. It bundles both the **iterative DFS maze generation logic** and the **BFS shortest-path finder**, operating purely on the maze grid data structure. This module can be imported and reused in any project that needs procedural maze generation or unweighted grid pathfinding, regardless of how the result is rendered or displayed.

---

## Team & Project Management

### Roles

| Team Member | Responsibility                                      |
|-------------|-----------------------------------------------------|
| `aymel-ha`  | Maze generation logic (iterative DFS algorithm)     |
| `iamessag`  | Terminal visualization (`curses` rendering/display) |

### Planning & How It Evolved

The initial plan was straightforward: one member handles generation, the other handles visualization, with a clear separation between the two layers. This division worked well in practice and allowed both of us to work in parallel with minimal blockers.

Two main challenges were encountered along the way:
- **Recursive DFS** hit Python's recursion limit on larger mazes and had to be rewritten iteratively using an explicit stack.
- **Config file parsing** had early bugs that required debugging and reworking the parser logic.

Both issues were identified and resolved during development without significantly disrupting the overall plan.

### What Worked Well

- The clear separation between generation and visualization made collaboration smooth and kept the codebase modular.
- Using an iterative DFS with an explicit stack proved to be a robust and clean solution once the recursion issue was identified.

### What Could Be Improved

- The config parser could be made more robust with better error handling for malformed or missing fields.
- Adding support for multiple maze algorithms (e.g., Prim's, Wilson's) as a selectable config option would make the project more extensible.

### Tools Used

| Tool          | Purpose                               |
|---------------|---------------------------------------|
| GitHub        | Version control and collaboration     |
| Vogsphere     | School's internal Git platform        |
| VS Code / vim | Code editing                          |
| Discord/Slack | Team communication                    |

---