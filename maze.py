from random import randint
from Cell import Cell
from Direction import DIRECTIONS, Direction
from State import State

def init_cells(length: int, width: int):
    """
    Initialize the cells of the maze.

    Parameters:
    length (int): The length of the maze.
    width (int): The width of the maze.

    Returns:
    list: A 2D list representing the cells of the maze.
    """
    return [[Cell(x,y) for x in range(width)] for y in range(length)]

def block_edges(cell:Cell, length:int, width:int):
    """Sets the walls of a Cell in some directions as Blocked if it is an edge

    Args:
        cell (Cell): The cell to set the walls for.
        length (int): The length of the maze.
        width (int): The width of the maze.

    Returns:
        Cell: The updated cell with blocked walls.
    """
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
    """
    Create an initial maze with the given length and width.

    Parameters:
    - length (int): The number of rows in the maze.
    - width (int): The number of columns in the maze.

    Returns:
    - list: A 2D list representing the initial maze, where each element is a list of block edges.
    """
    return [[block_edges(Cell(x, y), length=length, width=width) for x in range(width)] for y in range(length)]

def random_cell(maze:list[list[Cell]]) -> Cell:
    """
    Selects a random cell from the given maze.

    Parameters:
    maze (list[list[Cell]]): The maze represented as a 2D list of cells.

    Returns:
    Cell: The randomly selected cell.
    """
    width = len(maze[0])
    length = len(maze)
    X = randint(0, width-1)
    Y = randint(0, length-1)
    return maze[Y][X]

def as_matrix(adjacency_list: dict[Cell, list[Cell]]):
    """Converts an adjacency list of Cells to a matrix

    Args:
        adjacency_list (dict[Cell, list[Cell]]): The adjacency list representing the maze

    Returns:
        list[list[Cell]]: The matrix representation of the maze
    """
    # Get the length and width of the maze
    length = max([cell.Y for cell in adjacency_list.keys()]) + 1
    width = max([cell.X for cell in adjacency_list.keys()]) + 1
    # Initialize the matrix
    matrix = [[Cell(x,y) for x in range(width)] for y in range(length)]
    # Fill the matrix with the cells from the adjacency list
    for cell, neighbors in adjacency_list.items():
        matrix[cell.Y][cell.X] = cell
        cell.walls = {direction:State.UNVISITED for direction in DIRECTIONS}
        for neighbor in neighbors:
            # Get the direction of the neighbor
            direction = Direction((neighbor.X - cell.X, neighbor.Y - cell.Y))
            cell.walls[direction] = State.VISITED
        block_edges(cell, length, width)

    return matrix

def adjacency_list(maze: list[list[Cell]]) -> dict[str, list[str]]:
    """
    Generates an adjacency list representation of the given maze.

    Parameters:
    maze (list[list[Cell]]): The maze represented as a 2D list of Cell objects.

    Returns:
    dict[str, list[str]]: The adjacency list representation of the maze, where each key is a string representation of a cell and the corresponding value is a list of adjacent cells.
    """
    length = len(maze)
    width = len(maze[0])
    adj_list: dict[str, list[str]] = {}
    for y in range(length):
        for x in range(width):
            cell = maze[y][x]
            s = str(cell)
            adj_list[s] = []

            for direction, state in cell.walls.items():
                if state == State.VISITED:
                    adj_list[s].append(str(maze[y + direction.value[1]][x + direction.value[0]]))
    return adj_list

def show_maze(maze:list[list[Cell]], start_cell:Cell, ending_cell: Cell):
    """Prints the maze to the stdout by iterating over the y axis then the x axis. Only the north and west walls are checked for each cell to avoid double printing. Checking the East wall is handled by the next cell as that would be its west wall. While the South wall is handled by the cell below it as that would be its north wall."""
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

def export_file(maze: dict[str,list[str]], traversal:list[Cell|str], startEnd:tuple[Cell,Cell], filepath:str):
    import json
    with open(filepath, 'w') as f:
        json.dump({
            "start": str(startEnd[0]),
            "maze": maze,
            "traversal": [str(path) for path in traversal],
            "end": str(startEnd[1])
        }, f, indent=2)

def import_file(path:str):
    import json
    with open(path, 'r') as f:
        return json.load(f)

def import_maze_details(path:str):
    raw = import_file(path)
    maze: dict[str, list[str]] = raw['maze']
    start = raw['start']
    end = raw['end']
    adj_list:dict[Cell, list[Cell]] = {}

    # Map the string representations into their cell counterparts
    converted_nodes:dict[str, Cell] = {raw_node:Cell.from_str(raw_node) for raw_node in maze.keys()}
    for raw_node, raw_neighbors in maze.items():
        cell = converted_nodes[raw_node]
        # Find the neighbors using the converted nodes
        adj_list[cell] = [converted_nodes[raw_neighbor] for raw_neighbor in raw_neighbors]

    return {
        "graph": adj_list,
        "start": converted_nodes[start],
        "end": converted_nodes[end],
        # TODO: Convert the solution to a list of Cells and directions
        # TODO: Apparently, this is the actual traversal not only the solution
        "traversal": raw['traversal'],
    }

# Create a cli args parser that accepts a json file and prints the maze
def parse_cli_args() :
    import argparse
    from sys import argv
    parser = argparse.ArgumentParser(description='Prints the maze from a json file')
    parser.add_argument('-f', '--file', type=str, required=True, help='reads a json file containing a maze')
    if len(argv) == 1:
        parser.print_help()
        exit(0)
    return parser.parse_args(argv[1:])

def main():
    args = parse_cli_args()
    if args.file:
        maze_details = import_maze_details(args.file)
        maze = as_matrix(maze_details['graph'])
        show_maze(maze, maze_details['start'], maze_details['end'])

if __name__ == '__main__':
    main()
