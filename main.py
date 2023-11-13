import pygame
from random_dfs import Cell, State, Direction, random_dfs, show_maze

def _main(maze:list[list[Cell]], start_cell:Cell, ending_cell: Cell):
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("My Game")

    button = pygame.Rect(900, 200, 100, 25)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)

    length=len(maze)
    width = len(maze[0])
    def _refresh():
        nonlocal start_cell, ending_cell, maze
        start_cell, ending_cell, gen = random_dfs(length=length,width=width)
        final_maze = []
        for _maze, _ in gen:
            final_maze = _maze
        maze = final_maze
    # Start the game loop
    while True:
        # Check for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONUP:
                if button.collidepoint(event.pos):
                    _refresh()
        # Draw the game screen
        screen.fill((0, 0, 0))

        SIDE = 50
        for y in range(length):
            for x in range(width):
                cell = maze[y][x]
                X_START = x*SIDE+25
                Y_START = y*SIDE+25
                # Draw a border for the north and west walls
                COLOR = BLACK if cell.walls[Direction.NORTH] == State.VISITED else WHITE
                # TODO: Draw a horizontal line for the north wall
                pygame.draw.line(screen, COLOR, (X_START, Y_START), (X_START+SIDE, Y_START), 1)
                COLOR = BLACK if cell.walls[Direction.WEST] == State.VISITED else WHITE
                # TODO: Draw a vertical line for the west wall
                pygame.draw.line(screen, COLOR, (X_START, Y_START), (X_START, Y_START+SIDE ), 1)

                # Paint the rightmost walls
                X_START = (width)*SIDE+25
                pygame.draw.line(screen, WHITE, (X_START, Y_START), (X_START, Y_START+SIDE ), 1)
        # Paint the bottommost walls
        for x in range(width):
            X_START = x*SIDE+25
            Y_START = (length)*SIDE+25
            pygame.draw.line(screen, WHITE, (X_START, Y_START), (X_START+SIDE, Y_START), 1)

        # Create a button that handles a click event
        pygame.draw.rect(screen, (255, 0, 0), button, )

        # Update the display
        pygame.display.flip()

def main():
    length = 8
    width = 16
    STARTING_CELL,ENDING_CELL, maze_generator = random_dfs(length=length,width=width)
    final_maze = []
    final_path = []
    for maze, path in maze_generator:
        final_maze = maze
        final_path = path
    show_maze(final_maze, STARTING_CELL, ENDING_CELL)
    _main(final_maze, STARTING_CELL, ENDING_CELL)


if __name__ == '__main__':
    main()
