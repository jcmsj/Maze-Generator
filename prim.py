from random import choice, randint
from Cell import Cell
from Direction import Direction
from maze import matrix_to_str_edgelist, export_file, make_initial_maze, random_cell

def prim(maze: list[list[Cell]]):
    """ based on Iterative Prim:\n
    https://en.wikipedia.org/wiki/Maze_generation_algorithm 
        Returns a tuple containing the STARTING cell, ENDING cell, and a generator function for creating the maze based on those cells. 
        Note: The start and end cells doesnt actually matter.
    """

    # 1. Start with a grid full of walls.
    # It is assumed that a maze with all isolated cells are passed in.

    def get_neighbor(c:Cell, d:Direction):
        """Helper function to get the neighbor"""
        return maze[c.Y + d.value[1]][c.X + d.value[0]]
    
    # 2. Pick a cell
    start = random_cell(maze)

    # Make use of a generator, because for the GUIs, we want to show the maze being generated, step by step. This can be most conveniently done with a generator.
    traversal = [start]
    def generator():
        direction = choice(start.unvisited_walls())
        neighbor = get_neighbor(start, direction)
        # 2.1 mark it as part of the maze.
        start.visit(neighbor, direction)
        # 2.2 Add the walls of starting cell to the wall list.
        walls = [(start, d) for d in  start.non_blocked_walls()]
        # 3. While there are walls in the list
        yield maze, traversal
        while len(walls) > 0:
            # 3.1 and 3.3: Remove a random wall from the list.
            # In contrast to the wikipedia article, it is faster to remove the cell immediately than do so later on since:
            #   1. the list will get bigger,
            #   2. it would take time to search the cells
            cell, direction = walls.pop(randint(0, len(walls) - 1))
            neighbor = get_neighbor(cell, direction)
            # 3.2 If only one of the cells that the wall divides is visited, then: 
            if cell.visited != neighbor.visited: # cell xor neighor
                # 3.2.1 Make the wall a passage and mark the unvisited cell as part of the maze.
                cell.visit(neighbor, direction)
                # 3.2.2 Add the neighboring walls of the cell to the wall list.
                walls.extend([(neighbor, d) for d in neighbor.unvisited_walls()])
                traversal.append(neighbor)
                yield maze, traversal

    end = random_cell(maze)
    return start, end, generator(), maze, traversal

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
    '''Run if main module'''
    args = parse_cli_args()
    if args.length and args.width:
        maze = make_initial_maze(args.length, args.width)
        (STARTING_CELL, ENDING_CELL, maze_generator, maze, traversal) = prim(maze)
        # Just consume the entire generator
        for m,t in maze_generator:
            pass
        if args.export:
            maze_details = matrix_to_str_edgelist(maze)
            export_file(maze_details, (STARTING_CELL, ENDING_CELL), args.export, traversal)

if __name__ == '__main__':
    main()
