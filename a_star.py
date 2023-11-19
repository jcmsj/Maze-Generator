from queue import PriorityQueue
from Cell import Cell
from maze import import_maze_details

def heuristic(a:Cell, b:Cell):
    '''Calculate the Manhattan distance between two cells'''
    return abs(a.X - b.X) + abs(a.Y - b.Y)

def a_star_search(maze_info):
    '''Run A* search on the maze'''
    starting_cell:Cell = maze_info['start']
    ending_cell:Cell = maze_info['end']
    maze:dict[Cell,list[Cell]] = maze_info['graph']

    # Initialize priority queue with starting cell
    queue = PriorityQueue()
    queue.put((0, starting_cell))

    # Initialize cost dictionary with starting cell
    cost_so_far: dict[Cell, int] = {starting_cell: 0}

    # Initialize path dictionary with starting cell
    path: dict[Cell, Cell|None] = {starting_cell: None}

    # Loop until queue is empty or ending cell is found
    while not queue.empty():
        # Get next cell from queue
        _, current_cell = queue.get()

        # Check if current cell is the ending cell
        if current_cell == ending_cell:
            # Build path from ending cell to starting cell
            path_list:list[Cell] = [ending_cell]
            while path[path_list[-1]] is not None:
                path_list.append(path[path_list[-1]])
            path_list.reverse()
            return path_list

        # Add neighbors to queue with priority based on cost and heuristic
        for neighbor in maze[current_cell]:
            new_cost = cost_so_far[current_cell] + 1
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + heuristic(ending_cell, neighbor)
                queue.put((priority, neighbor))
                path[neighbor] = current_cell

    # If ending cell was not found, return None
    return None
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
