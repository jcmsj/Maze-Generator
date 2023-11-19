import random
from Cell import Cell
from Direction import Direction
from State import State
from maze import adjacency_list, export_file, make_initial_maze, random_cell

def random_dfs(length:int, width:int):
    """ Returns a tuple containing the STARTING cell, ENDING cell, and a generator function for creating the maze based on those cells"""
    maze = make_initial_maze(length, width)
    # (1) Choose the initial cell, mark it as visited and push it to the stack
    STARTING_CELL = random_cell(maze)
    # STARTING_CELL.visited = True
    ENDING_CELL = random_cell(maze)
    stack = [STARTING_CELL]
    # The path represents the entire graph traversal.
    path:list[Cell|str] = [STARTING_CELL]
    def _generator():
        while len(stack) > 0:
            current: Cell = stack.pop()
            # Identify unvisited neighbors
            open_list: list[Direction] = current.unvisited_walls()
            # (2) If the chosen cell has any unvisited neighbours
            if len(open_list) == 0:
                continue
            # (2.2) Choose one of the unvisited neighbours
            direction: Direction = random.choice(open_list)
    
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
        STARTING_CELL,ENDING_CELL, maze_generator = random_dfs(length=args.length,width=args.width)
        final_maze = []
        final_path = []
        for maze, path in maze_generator:
            final_maze = maze
            final_path = path
        if args.export:
            maze_details = adjacency_list(final_maze)
            export_file(maze_details, final_path, (STARTING_CELL, ENDING_CELL), args.export)

if __name__ == '__main__':
    main()
