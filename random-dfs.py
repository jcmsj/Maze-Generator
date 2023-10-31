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
DIRECTIONS = list(Direction)

class State(Enum):
    UNVISITED = 0
    VISITED = 1
    BLOCKED = 2

class Cell:
    def __init__(self, x:int, y:int ) -> None:
        self.x = x
        self.y = y
        self.walls = {d:State.UNVISITED for d in DIRECTIONS}
        self.visited = False

    def __repr__(self) -> str:
        return f'C({self.x},{self.y})'
    
def random_dfs(length:int, width:int):
    maze = [[Cell(x,y) for x in range(width)] for y in range(length)]
    stack = []
    # (1) Choose the initial cell, mark it as visited and push it to the stack
    start_x = random.randint(0, width-1)
    start_y = random.randint(0, length-1)
    starting_cell = maze[start_y][start_x]
    starting_cell.visited = True
    stack.append(starting_cell)

    end_x = random.randint(0, width-1)
    end_y = random.randint(0, length-1)
    print(f"Starting at {starting_cell}")
    path = []

    def _show_maze():
        show_maze(maze, (start_x,start_y), (end_x, end_y))

    def _block_edges(cell:Cell):
        if cell.x == 0:
            cell.walls[Direction.WEST] = State.BLOCKED
        elif cell.x == width-1:
            cell.walls[Direction.EAST] = State.BLOCKED

        if cell.y == 0:
            cell.walls[Direction.NORTH] = State.BLOCKED
        elif cell.y==length-1:
            cell.walls[Direction.SOUTH] = State.BLOCKED

    while len(stack):
        current:Cell = stack.pop()
        _block_edges(current)
        open_list = [dir for dir, state in current.walls.items() if state == State.UNVISITED]
        if len(open_list) == 0:
            continue
   
        # (2.3) Choose one of the unvisited neighbours
        direction = random.choice(open_list)
 
        # Get the cell at the given direction
        chosen: Cell = maze[current.y+direction.value[1]][current.x+direction.value[0]]
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
       
        # Every iteration, print the maze
        # _show_maze()

        # input() # To pause the execution
    _show_maze()
    return maze, path

def show_maze(maze:list[list[Cell]], start:tuple[int, int], end: tuple[int, int]):
    length = len(maze)
    width = len(maze[0])
    starting_cell = maze[start[1]][start[0]]
    ending_cell = maze[end[1]][end[0]]
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
            if cell == starting_cell:
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
    maze,path = random_dfs(length=length,width=width)
    # print(" -> ".join([str(p) for p in path]))
    # Show the maze as an actual maze

if __name__ == '__main__':
    main()
