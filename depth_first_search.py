from Cell import Cell
from State import State
from maze import as_matrix, import_maze_details

def depth_first_search(maze: list[list[Cell]], start:Cell, end:Cell):
    """Run depth first search on a matrix representation of the maze. Returns a tuple containing the path and the entire traversal order"""
    stack = [(start)]
    visited = set()
    solution = [start.coordinate]
    traversal_order = [start.coordinate]
    while stack:
        current_cell = stack.pop()

        # Every loop, add the current cell's coordinate to the traversal list
        traversal_order.append(current_cell.coordinate)
        if current_cell.coordinate == end.coordinate:
            return solution, traversal_order
        
        if current_cell not in visited:
            visited.add(current_cell)
            for neighbor in current_cell.visited_walls():
                next_cell = maze[current_cell.Y + neighbor.value[1]][current_cell.X + neighbor.value[0]]
                if next_cell in visited:
                    continue
                stack.append(current_cell)
                stack.append(next_cell)
                solution.append(next_cell.coordinate)

    return [], traversal_order

def print_path(path):
    if path:
        print("Solution:", " -> ".join(map(str, path)))
    else:
        print("No solution found.")
def parse_cli_args() :
    import argparse
    from sys import argv
    parser = argparse.ArgumentParser(description='Solves  a maze using Depth First Search')
    parser.add_argument('-f', '--file', type=str, required=True, help='reads a json file containing a maze')
    if len(argv) == 1:
        parser.print_help()
        exit(0)
    return parser.parse_args(argv[1:])

def main():
    args = parse_cli_args()
    if args.file:
        maze_info = import_maze_details(args.file)
        maze_matrix = as_matrix(maze_info['graph'])
        path, traversal = depth_first_search(maze_matrix, maze_info['start'], maze_info['end'])
        print_path(path)
        # print_path(traversal)

if __name__ == '__main__':
    main()
