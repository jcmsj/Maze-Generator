
from Cell import Cell
from maze import import_maze_details

def breadth_first_search(graph:dict[Cell, list[Cell]], start:Cell, end:Cell):
    '''Run breath first search on the maze'''
       # Initialize queue with starting cell
    queue = [start]

    # Initialize visited set with starting cell
    visited = set([start])

    # Initialize path dictionary with starting cell
    path: dict[Cell, Cell|None] = {start: None}
    traversal:list[tuple[int,int]]  = []
    # Loop until queue is empty or ending cell is found
    while queue:
        # Get next cell from queue
        current_cell = queue.pop(0)
        traversal.append(current_cell.coordinate)
        # Check if current cell is the ending cell
        if current_cell == end:
            # Build path from ending cell to starting cell
            path_list:list[Cell] = [end]
            while path[path_list[-1]] is not None:
                path_list.append(path[path_list[-1]]) # type: ignore
            path_list.reverse()
            return path_list, traversal

        # Add unvisited neighbors to queue and visited set
        for neighbor in graph[current_cell]:
            if neighbor not in visited:
                queue.append(neighbor)
                visited.add(neighbor)
                path[neighbor] = current_cell

    # If ending cell was not found, return None
    return [], traversal
def parse_cli_args() :
    import argparse
    from sys import argv
    parser = argparse.ArgumentParser(description='Solves a maze using Breadth First Search')
    parser.add_argument('-f', '--file', type=str, required=True, help='reads a json file containing a maze')
    if len(argv) == 1:
        parser.print_help()
        exit(0)
    return parser.parse_args(argv[1:])
def main():
    '''Run if main module'''
    args = parse_cli_args()
    if args.file:
        maze_info = import_maze_details(args.file)
        path,traversal = breadth_first_search(**maze_info)
        print("No path" if path == None else " -> ".join([str(cell) for cell in path]))

if __name__ == '__main__':
    main()
