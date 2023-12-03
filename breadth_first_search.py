from Cell import Cell
from depth_first_search import depth_first_search
from maze import as_matrix, import_maze_details

def breadth_first_search(graph:dict[Cell, list[Cell]], start:Cell, end:Cell):
    '''Run breath first search on the maze'''
       # Initialize queue with starting cell
    queue = [start]

    # Initialize visited set with starting cell
    visited = set([start])
    matrix = as_matrix(graph)

    # Initialize path dictionary with starting cell
    path: dict[Cell, Cell|None] = {start: None}
    traversal:list[tuple[int,int]]  = []
    # Loop until queue is empty or ending cell is found
    def backtrack(cell:Cell):
        path_list:list[Cell] = [cell]
        while path[path_list[-1]] != None:
            path_list.append(path[path_list[-1]]) # type: ignore
        path_list.reverse()
        return path_list

    prev_start =  start
    while queue:
        # Get next cell from queue
        current_cell = queue.pop(0)
        # Purely to show the movement from the current child to the previously visited node, do a dfs
        subpath, _ = depth_first_search(matrix, prev_start, current_cell)
        if subpath:
            # we dont need current cell in the subpath, it will be included in the next subpath
            subpath.pop()
        traversal.extend(subpath)
        prev_start = current_cell
        # Check if current cell is the ending cell
        if current_cell == end:
            return backtrack(current_cell), traversal

        # Add unvisited neighbors to queue and visited set
        for child in graph[current_cell]:
            if child not in visited:
                queue.append(child)
                visited.add(child)   
                path[child] = current_cell

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
