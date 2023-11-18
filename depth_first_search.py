from random_dfs import Cell, State, as_matrix, import_maze_details, parse_cli_args

def depth_first_search(maze: list[list[Cell]], start:Cell, end:Cell):
    """Run depth first search on a matrix representation of the maze"""
    stack = [(start, [(start.X, start.Y)])]
    visited = set()

    while stack:
        current, path = stack.pop()

        if (current.X, current.Y) == (end.X, end.Y):
            return path

        if current not in visited:
            visited.add(current)

            neighbors = [neighbor for neighbor, state in current.walls.items() if state == State.VISITED]
            for neighbor in neighbors:
                next_cell = maze[current.Y + neighbor.value[1]][current.X + neighbor.value[0]]
                stack.append((next_cell, path + [(next_cell.X, next_cell.Y)]))

    return None

def print_path(path):
    if path:
            print("Solution:", " -> ".join(map(str, path)))
    else:
            print("No solution found.")

def dfs_main():
    args = parse_cli_args()
    if args.file:
        maze_info = import_maze_details(args.file)
        maze_matrix = as_matrix(maze_info['graph'])
        path = depth_first_search(maze_matrix, maze_info['start'], maze_info['end'])
        print_path(path)

if __name__ == '__main__':
    dfs_main()
