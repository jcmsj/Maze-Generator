import random
from enum import Enum

class Direction(Enum):
    WEST = (-1,0)
    NORTH = (0,-1)
    EAST = (1,0)
    SOUTH = (0,1)

    def __add__(self, other):
        return Direction((self.value + other) % 4)
    
    def inverse(self):
        match self:
            case Direction.WEST:
                return Direction.EAST
            case Direction.NORTH:
                return Direction.SOUTH
            case Direction.EAST:
                return Direction.WEST
            case Direction.SOUTH:
                return Direction.NORTH
            case _:
                raise Exception("Invalid Direction")
            
    def show(self) -> str:
        match self:
            case Direction.WEST:
                return 'W'
            case Direction.NORTH:
                return 'N'
            case Direction.EAST:
                return 'E'
            case Direction.SOUTH:
                return 'S'
            case _:
                raise Exception("Invalid Direction")
DIRECTIONS = list(Direction)

class State(Enum):
    UNVISITED = 0
    VISITED = 1
    BLOCKED = 2

class Cell:
    def __init__(self, x:int, y:int ) -> None:
        self.X = x
        self.Y = y
        self.walls = {d:State.UNVISITED for d in DIRECTIONS}
        self.visited = False

    def __repr__(self) -> str:
        return f'C({self.X},{self.Y})'
    
def init_cells(length: int, width: int):
    return [[Cell(x,y) for x in range(width)] for y in range(length)]

def block_edges(cell:Cell, length:int, width:int):
    """Sets the walls of a Cell in some directions as Blocked if it is an edge"""
    if cell.X == 0:
        cell.walls[Direction.WEST] = State.BLOCKED
    elif cell.X == width-1:
        cell.walls[Direction.EAST] = State.BLOCKED

    if cell.Y == 0:
        cell.walls[Direction.NORTH] = State.BLOCKED
    elif cell.Y==length-1:
        cell.walls[Direction.SOUTH] = State.BLOCKED

    return cell

def make_initial_maze(length: int, width: int):
    return [[block_edges(Cell(x, y), length=length, width=width) for x in range(width)] for y in range(length)]

def random_cell(maze:list[list[Cell]]):
    width = len(maze[0])
    length = len(maze)
    X = random.randint(0, width-1)
    Y = random.randint(0, length-1)
    return maze[Y][X]

def random_dfs(length:int, width:int):
    """A generator function for maze creation using Random Depth-First Search. 
    Calling __next__ the first time returns a tuple containing the STARTING and ENDING cell. Further calls returns the same maze and path"""
    maze = make_initial_maze(length, width)
    stack = []
    # (1) Choose the initial cell, mark it as visited and push it to the stack
    STARTING_CELL = random_cell(maze)
    ENDING_CELL = random_cell(maze)
    stack.append(STARTING_CELL)
    yield STARTING_CELL, ENDING_CELL
    path = [STARTING_CELL]

    while len(stack):
        current:Cell = stack.pop()
        open_list = [dir for dir, state in current.walls.items() if state == State.UNVISITED]
        if len(open_list) == 0:
            continue
   
        # (2.3) Choose one of the unvisited neighbours
        direction = random.choice(open_list)
 
        # Get the cell at the given direction
        chosen: Cell = maze[current.Y+direction.value[1]][current.X+direction.value[0]]
        # (2.1) If the current cell has any unvisited neighbours
        if chosen.visited:
            continue
        # (2.2) Push it to the stack
        stack.append(current)
        # (2.4) Remove the wall between the current cell and the chosen cell
        current.walls[direction] = State.VISITED
        # Inverse direction, read (2.4)
        chosen.walls[direction.inverse()] = State.VISITED
        # (2.5) Mark the chosen cell as visited and push it to the stack
        chosen.visited = True
        stack.append(chosen)

        # Note the path
        path.append(direction.show())
        path.append(chosen)
        yield maze, path

    return maze, path

def show_maze(maze:list[list[Cell]], start_cell:Cell, ending_cell: Cell):
    length = len(maze)
    width = len(maze[0])
    for y in range(length):
        for x in range(width):
            cell = maze[y][x]
            if cell.walls[Direction.NORTH] == State.VISITED:
                print("+   ", end="")
            else:
                print("+---", end="")
        print('+')
        for x in range(width):
            cell = maze[y][x]
            if cell == start_cell:
                if cell.walls[Direction.WEST] == State.VISITED:
                    print("  ⬤ ", end="")
                else:
                    print("| ⬤ ", end="")
            elif cell != ending_cell:
                if cell.walls[Direction.WEST] == State.VISITED:
                    print("    ", end="")
                else:
                    print("|   ", end="")
            else:
                if cell.walls[Direction.WEST] == State.VISITED:
                    print("  X ", end="")
                else:
                    print("| X ", end="")
                
        print('|')
    print("+---"*width, end="")
    print('+')
def main():
    '''Run if main module'''
    length = int(input("Enter length:"))
    width = int(input("Enter width:"))

    maze_generator = random_dfs(length=length,width=width)
    STARTING_CELL,ENDING_CELL = maze_generator.__next__()
    print(f"Starting at {STARTING_CELL}")
    print(f"Ending cell {ENDING_CELL}")
    final_maze = None
    final_path = None
    for maze, path in maze_generator:
        final_maze = maze
        final_path = path
    show_maze(final_maze, STARTING_CELL, ENDING_CELL)
    print(" -> ".join([str(p) for p in path]))

if __name__ == '__main__':
    main()
