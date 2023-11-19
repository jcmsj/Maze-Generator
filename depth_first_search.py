from random_dfs import Cell, State, as_matrix, import_maze_details, parse_cli_args

def depth_first_search(maze: list[list[Cell]], start:Cell, end:Cell):
    """Run depth first search on a matrix representation of the maze. Returns a tuple containing the path and the entire traversal order"""
    stack = [(start, [(start.X, start.Y)])]
    visited = set()
    traversal_order = []
    while stack:
        current, path = stack.pop()

        coord = (current.X, current.Y)
        # Every loop, add the current cell's coordinate to the traversal list
        traversal_order.append(coord)

        if coord == (end.X, end.Y):
            return path, traversal_order

        if current not in visited:
            visited.add(current)

            neighbors = [neighbor for neighbor, state in current.walls.items() if state == State.VISITED]
            for neighbor in neighbors:
                next_cell = maze[current.Y + neighbor.value[1]][current.X + neighbor.value[0]]
                stack.append((next_cell, path + [(next_cell.X, next_cell.Y)]))

    return None, traversal_order

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
        path, traversal = depth_first_search(maze_matrix, maze_info['start'], maze_info['end'])
        print_path(path)
        print_path(traversal)


if __name__ == '__main__':
    dfs_main()
