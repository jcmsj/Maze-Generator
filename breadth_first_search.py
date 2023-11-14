
from random_dfs import Cell, import_maze_details, parse_cli_args

def breadth_first_search(maze_info):
    '''Run breath first search on the maze'''
    starting_cell:Cell = maze_info['start']
    ending_cell:Cell = maze_info['end']
    maze = maze_info['graph']
       # Initialize queue with starting cell
    queue = [starting_cell]

    # Initialize visited set with starting cell
    visited = set([starting_cell])

    # Initialize path dictionary with starting cell
    path: dict[Cell, Cell|None] = {starting_cell: None}

    # Loop until queue is empty or ending cell is found
    while queue:
        # Get next cell from queue
        current_cell = queue.pop(0)

        # Check if current cell is the ending cell
        if current_cell == ending_cell:
            # Build path from ending cell to starting cell
            path_list:list[Cell] = [ending_cell]
            while path[path_list[-1]] is not None:
                path_list.append(path[path_list[-1]])
            path_list.reverse()
            return path_list

        # Add unvisited neighbors to queue and visited set
        for neighbor in maze[current_cell]:
            if neighbor not in visited:
                queue.append(neighbor)
                visited.add(neighbor)
                path[neighbor] = current_cell

    # If ending cell was not found, return None
    return None

def main():
    '''Run if main module'''
    args = parse_cli_args()
    if args.file:
        maze_info = import_maze_details(args.file)
        path = breadth_first_search(maze_info)
        print("No path" if path == None else " -> ".join([str(cell) for cell in path]))

if __name__ == '__main__':
    main()
