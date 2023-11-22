import random
from Cell import Cell
from maze import adjacency_list, export_file, make_initial_maze, random_cell

def random_dfs(length:int, width:int):
    """ Returns a tuple containing the STARTING cell, ENDING cell, and a generator function for creating the maze based on those cells"""
    maze = make_initial_maze(length, width)
    # (1) Choose the initial cell, mark it as visited and push it to the stack
    STARTING_CELL = random_cell(maze)
    ENDING_CELL = random_cell(maze)

    def get_neighbors(cell:Cell):
        """Returns the dir and cell at unvisited walls"""
        # Get the cell at the given direction
        neighbors = {dir:maze[cell.Y+dir.value[1]][cell.X+dir.value[0]] for dir in cell.unvisited_walls()}
        return [(dir,n) for dir,n in neighbors.items() if not n.visited]
    path:list[Cell|str] = []
    def _generator():
        stack = [STARTING_CELL]
        # The path represents the entire graph traversal.

        # Yield the initial maze
        yield maze

        while len(stack) > 0:
            current: Cell = stack.pop()
            # (2) If the chosen cell has any unvisited neighbours
            neighbors = get_neighbors(current)
            path.append(current)
            if len(neighbors) == 0:
                continue
            # (2.1) Choose one of the unvisited neighbours
            direction, chosen = random.choice(neighbors)
            # (2.2) Mark the chosen cell as visited
            current.visit(chosen, direction)
            # (2.3) Put back current
            stack.append(current)
            # (2.4) push chosen to the stack, 
            # since we want to visit it next, since dfs
            stack.append(chosen)
          
            yield maze, path

    return STARTING_CELL, ENDING_CELL, _generator(), maze, path
def parse_cli_args() :
    import argparse
    from sys import argv
    parser = argparse.ArgumentParser(description='Generate\'s a maze using Random Depth First Search')
    parser.add_argument('-l', '--length', required=True, type=int, help='The length of the maze to be made')
    parser.add_argument('-w', '--width',required=True,  type=int, help='The width of the maze to be made')
    parser.add_argument('-export', '--export',required=True,  type=str, help='Export the created maze to a file as an adjacency list')
    if len(argv) == 1:
        parser.print_help()
        exit(0)
    return parser.parse_args(argv[1:])

def main():
    args = parse_cli_args()
    if args.length and args.width:
        (STARTING_CELL, ENDING_CELL, maze_generator, maze, path) = random_dfs(length=args.length,width=args.width)
        # Consume the entire generator
        for _, _ in maze_generator:
            pass
        if args.export:
            maze_details = adjacency_list(maze)
            export_file(maze_details, path, (STARTING_CELL, ENDING_CELL), args.export)

if __name__ == '__main__':
    main()
