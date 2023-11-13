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
            
    def __str__(self): 
        return self.show()
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

    def __str__(self): 
        return self.name

class Cell:
    def __init__(self, x:int, y:int ) -> None:
        self.X = x
        self.Y = y
        self.walls = {d:State.UNVISITED for d in DIRECTIONS}

    def unvisited_walls(self):
        return [dir for dir, state in self.walls.items() if state == State.UNVISITED]

    def __repr__(self) -> str:
        return f'({self.X},{self.Y})'
    
    
    @property
    def visited(self) -> bool:
        return State.VISITED in self.walls.values()

    @classmethod
    def from_str(cls, s:str):
        import re
        digit_scanner = re.compile('\\d+')
        x,y = [int(i) for i in digit_scanner.findall(s)]
        return Cell(x,y)

    def __str__(self) -> str:
        return self.__repr__()
        # return self.__dict__.__str__()
    
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
    """ Returns a tuple containing the STARTING cell, ENDING cell, and a generator function for creating the maze based on those cells"""
    maze = make_initial_maze(length, width)
    # (1) Choose the initial cell, mark it as visited and push it to the stack
    STARTING_CELL = random_cell(maze)
    # STARTING_CELL.visited = True
    ENDING_CELL = random_cell(maze)
    stack = [STARTING_CELL]
    path:list[Cell|str] = [STARTING_CELL]
    def _generator():
        while len(stack):
            current:Cell = stack.pop()
            # Identify unvisited neighbors
            open_list = current.unvisited_walls()
            # (2) If the chosen cell has any unvisited neighbours
            if len(open_list) == 0:
                continue
            # (2.2) Choose one of the unvisited neighbours
            direction = random.choice(open_list)
    
            # Get the cell at the given direction
            chosen: Cell = maze[current.Y+direction.value[1]][current.X+direction.value[0]]
            if chosen.visited:
                continue
            # (2.2) Push the current cell to the stack
            stack.append(current)
            # (2.3) Remove the wall between the current cell... 
            current.walls[direction] = State.VISITED
            # and the chosen cell
            chosen.walls[direction.inverse()] = State.VISITED
            # (2.4) Mark the chosen cell as visited and push it to the stack
            # Modifying the walls of the chosen cell is enough to mark it as visited
            stack.append(chosen)
          
            # Note the path
            path.append(direction.show())
            path.append(chosen)
            yield maze, path

    return STARTING_CELL, ENDING_CELL, _generator()

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
            elif cell == ending_cell:
                if cell.walls[Direction.WEST] == State.VISITED:
                    print("  X ", end="")
                else:
                    print("| X ", end="")
            else:
                if cell.walls[Direction.WEST] == State.VISITED:
                    print("    ", end="")
                else:
                    print("|   ", end="")
                
        print('|')
    print("+---"*width, end="")
    print('+')

def export_file(maze: dict[str,list[str]], path:str):
    import json
    with open(path, 'w') as f:
        json.dump(maze, f, indent=2)

def adjacency_list(maze: list[list[Cell]]):
    length = len(maze)
    width = len(maze[0])
    adj_list:dict[str,list[str]] = {}
    for y in range(length):
        for x in range(width):
            cell = maze[y][x]
            s = str(cell)
            adj_list[s] = []

            for direction, state in cell.walls.items():
                if state == State.VISITED:
                    adj_list[s].append(str(maze[y+direction.value[1]][x+direction.value[0]]))
    return adj_list

def import_file(path:str):
    import json
    with open(path, 'r') as f:
        return json.load(f)

def import_adjacency_list(path:str):
    import re
    raw:dict[str, list[str]] = import_file(path)
    adj_list:dict[Cell, list[Cell]] = {}

    converted_nodes:dict[str, Cell] = {}
    def _iter(raw_node, raw_neighbors):
        cell = None
        if raw_node in converted_nodes:
            cell = converted_nodes[raw_node]
        else:
            cell = converted_nodes[raw_node] = Cell.from_str(raw_node)

    for raw_node in raw.keys():
        cell = None
        if raw_node in converted_nodes:
            cell = converted_nodes[raw_node]
        else:
            cell = converted_nodes[raw_node] = Cell.from_str(raw_node)
        
def main():
    from sys import argv
    # match a -l and -w flag from argv
    length = None
    width = None
    match argv:
        case [_, '-l', length, '-w', width]:
            length = int(length)
            width = int(width)
        case [_, '-l', length]:
            length = int(length)
            width = length
        case [_, '-w', width]:
            width = int(width)
            length = width
        # case [_, '-f', path]:
        #     maze = import_file(path)
        #     length = len(maze)
        #     width = len(maze[0])
        case _:
            print("Usage: python random-dfs.py [-l length] [-w width]")
            return

    STARTING_CELL,ENDING_CELL, maze_generator = random_dfs(length=length,width=width)
    print(f"Starting at {STARTING_CELL}")
    print(f"Ending cell {ENDING_CELL}")
    final_maze = []
    final_path = []
    for maze, path in maze_generator:
        final_maze = maze
        final_path = path
        show_maze(final_maze, STARTING_CELL, ENDING_CELL)

    print(" -> ".join([str(p) for p in final_path]))
    l = adjacency_list(final_maze)
    # print(l)
    export_file(l, 'maze.json')

if __name__ == '__main__':
    main()
