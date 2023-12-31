from queue import PriorityQueue
from Cell import Cell
from depth_first_search import depth_first_search
from maze import as_matrix, import_maze_details

from queue import PriorityQueue

def heuristic(a:Cell, b:Cell):
    '''Calculate the Manhattan distance between two cells'''
    return abs(a.X - b.X) + abs(a.Y - b.Y)

def a_star_search(maze_info):
    #Run A* search on the maze
    starting_cell:Cell = maze_info['start']
    ending_cell:Cell = maze_info['end']
    maze:dict[Cell,list[Cell]] = maze_info['graph']

    # Initialize priority queue with starting cell
    queue: PriorityQueue[tuple[int,Cell]] = PriorityQueue()
    queue.put((0, starting_cell))

    cost_so_far: dict[Cell, int] = {starting_cell: 0}
    path: dict[Cell, Cell|None] = {starting_cell: None}
    visited_cells = [starting_cell.coordinate]
    matrix = as_matrix(maze)
    marker = starting_cell
    while not queue.empty():
        _, current_cell= queue.get()
        subpath, _ = depth_first_search(matrix, marker, current_cell)
        subpath.pop()
        visited_cells.extend(subpath)
        marker = current_cell

        if current_cell == ending_cell:
            visited_cells.append(current_cell.coordinate)
            path_list:list[Cell] = [ending_cell]
            while path[path_list[-1]] is not None:
                path_list.append(path[path_list[-1]]) # type: ignore since the check above is not None
            path_list.reverse()
            return path_list, visited_cells
        for neighbor in maze[current_cell]:
            new_cost = cost_so_far[current_cell] + 1
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + heuristic(ending_cell, neighbor)
                queue.put((priority, neighbor))  
                path[neighbor] = current_cell
               
    # If ending cell was not found, return None
    return None, visited_cells
def parse_cli_args() :
    from argparse import ArgumentParser
    from sys import argv
    parser = ArgumentParser(description='Solves  a maze using A* search')
    parser.add_argument('-f', '--file', type=str, help='reads a json file containing a maze')
    if len(argv) == 1:
        parser.print_help()
        exit(0)
    return parser.parse_args(argv[1:])
def main():
    '''Run if main module'''
    args = parse_cli_args()
    if args.file:
        maze_info = import_maze_details(args.file)
        path = a_star_search(maze_info)
        print("No path" if path == None else " -> ".join([str(cell) for cell in path]))

if __name__ == '__main__':
    main()
