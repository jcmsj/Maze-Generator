import pygame
from widgets import BoolVal, Button, Button, Text, TextField
from maze import show_maze
from random_dfs import random_dfs

def load_image(path:str, width:int, length:int, ):
    """
    Load an image from the given path and resize it to the specified size.

    Args:
        path (str): The path to the image file.
        size (int): The desired size of the image.

    Returns:
        pygame.Surface: The scaled image.
    """
    return pygame.transform.scale(pygame.image.load(path), (width, length))
def animator(basename: str, file_extension: str, frame_count: int, size, loop=True):
    """
    Generates frames for animation based on the given parameters.

    Args:
        basename (str): The base name of the animation frames.
        file_extension (str): The file extension of the animation frames.
        frame_count (int): The number of frames in the animation.
        size: The size of each frame.
        loop (bool, optional): Whether the animation should loop. Defaults to True.

    Yields:
        frame: The next frame in the animation.

    """
    frames = tuple([
        load_image(f"{basename}_{i}.{file_extension}", size,size) for i in range(frame_count)
    ])
    index = 0
    if loop:
        while True:
            yield frames[index]
            index = (index + 1) % len(frames)
    else:
        while index < len(frames):
            yield frames[index]
            index += 1

def _main():
    # maze:list[list[Cell]], start_cell:Cell, ending_cell: Cell, 
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Yet Another Maze Generator")
    # load the material icons font
    pygame.font.init()
    materialIcons = pygame.font.Font('assets/MaterialIconsOutlined-Regular.otf', 64)
    textFont = pygame.font.Font("assets/pixel.ttf", 24)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    CONFIG = {
        "FPS_CAP": 10,
    }
    PLAYING = BoolVal(False)
    PLAY_BUTTON = Button(
        onclick= PLAYING.to_true,
        text=Text(
            'play_arrow', 
            screen, 
            materialIcons, 
            (1232, 50),
            WHITE,
            BLACK,
        ),
    )
    PAUSE_BUTTON = Button(
        onclick= PLAYING.to_false,
        text=Text(
            'pause',
            screen,
            materialIcons,
            (1232, 50),
            WHITE,
            BLACK,
        ),
    )

    length =8 #len(maze)
    width = 16 #len(maze[0])
    gen = None
    start_cell = None
    ending_cell = None
    maze = []
    
    def start():
        nonlocal start_cell, ending_cell, maze, gen
        start_cell, ending_cell, gen = random_dfs(length=length,width=width)

    def _step():
        nonlocal maze, gen
        if gen != None:
            try:
                maze,_ = next(gen)
            except:
                PLAYING.to_false()
                gen = None

    NEXT_STEP = Button(
        onclick= _step,
        text=Text(
            'fast_forward',
            screen,
            materialIcons,
            (1232, 300),
            WHITE,
            BLACK,
        ),
    )

    def onFPSChange(val:str):
        if val.isdigit():
            CONFIG["FPS_CAP"] = int(val)
            print(f"FPS_CAP: {CONFIG['FPS_CAP']}")
            return False
        return True
    
    FPS_LABEL = textFont.render('FPS:', True, WHITE, BLACK)
    FPS_LABEL_RECT = FPS_LABEL.get_rect()
    FPS_LABEL_RECT.center = (1232, 350)
    FPS_FIELD = TextField(
        screen, 
        str(CONFIG['FPS_CAP']), 
        1232, 
        400, 
        textFont, 
        WHITE, 
        BLACK, 
        onSubmit=onFPSChange
    )
    SIDE = 50
    SIZE = SIDE + 25
    paths = {
        'northOOB': load_image("assets/paths/northOOB.png", SIZE,SIZE), #0
        'southOOB': load_image("assets/paths/southOOB.png", SIZE,SIZE), #1
        'eastOOB': load_image("assets/paths/eastOOB.png", SIZE,SIZE), #2
        'westOOB': load_image("assets/paths/westOOB.png", SIZE,SIZE), #3
        'NORTHEAST': load_image("assets/paths/NORTHEAST.png", SIZE,SIZE), #4
        'NORTHWEST': load_image("assets/paths/NORTHWEST.png", SIZE,SIZE), #5
        'SOUTHEAST': load_image("assets/paths/SOUTHEAST.png", SIZE,SIZE), #6
        'SOUTHWEST': load_image("assets/paths/SOUTHWEST.png", SIZE,SIZE), #7
        'H_north': load_image("assets/paths/H_north.png", SIZE,SIZE), #8
        'H_south': load_image("assets/paths/H_south.png", SIZE, SIZE), #9
        'V_east': load_image("assets/paths/V_east.png", SIZE,SIZE), #10
        'V_west': load_image("assets/paths/V_west.png", SIZE,SIZE), #11
        'HORIZONTAL': load_image("assets/paths/HORIZONTAL.png", SIZE,SIZE), #12
        'VERTICAL': load_image("assets/paths/VERTICAL.png", SIZE,SIZE), #13
        'INTERSECTION': load_image("assets/paths/INTERSECTION.png", SIZE,SIZE), #14
        'unsectioned': load_image("assets/paths/unsectioned.png", SIZE,SIZE) #15   
    }
    # Restart button
    def restart():
        start()
        PLAYING.to_false()
        _step()

    RESTART_BUTTON = Button(
        onclick= restart,
        text=Text(
            'replay',
            screen,
            materialIcons,
            (1232, 150),
            WHITE, 
            BLACK,
        ),
    )

    def reposition_img(x,y):
        X_START = x*SIZE
        Y_START = y*SIZE
        return (X_START, Y_START)

    player = animator("assets/player/playeridle", "gif", 6, SIZE)
    goal = animator("assets/goal/goal", "gif", 4, SIZE)
    start()
    _step()
    # Start the game loop 
    while True:
        # Check for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if PLAYING:
                PAUSE_BUTTON.listen(event)
            else: 
                PLAY_BUTTON.listen(event)
            RESTART_BUTTON.listen(event)
            NEXT_STEP.listen(event)
            FPS_FIELD.listen(event)
        # Draw the game screen
        screen.fill((0, 0, 0))

        for y in range(length):
            for x in range(width):
                cell = maze[y][x]
                position = reposition_img(x,y)
                direction_list = [str(d) for d in cell.visited_walls()]
                if len(direction_list) == 0:
                    screen.blit(paths['unsectioned'], position)
                elif len(direction_list) == 4:
                    screen.blit(paths['INTERSECTION'], position)
                elif direction_list == ['N','S']:
                    screen.blit(paths['VERTICAL'], position)
                elif direction_list == ['W','E']:
                    screen.blit(paths['HORIZONTAL'], position)
                elif direction_list == ['W','N','S']:
                    screen.blit(paths['V_west'], position)
                elif direction_list == ['N','E','S']:
                    screen.blit(paths['V_east'], position)
                elif direction_list == ['W','E','S']:
                    screen.blit(paths['H_south'], position)
                elif direction_list == ['W','N','E']:
                    screen.blit(paths['H_north'], position)
                elif direction_list == ['W','S']:
                    screen.blit(paths['SOUTHWEST'], position)
                elif direction_list == ['E','S']:
                    screen.blit(paths['SOUTHEAST'], position)
                elif direction_list == ['W','N']:
                    screen.blit(paths['NORTHWEST'], position)
                elif direction_list == ['N','E']:
                    screen.blit(paths['NORTHEAST'], position)
                elif direction_list == ['E']:
                    screen.blit(paths['westOOB'], position)
                elif direction_list == ['W']:
                    screen.blit(paths['eastOOB'], position)
                elif direction_list == ['S']:
                    screen.blit(paths['northOOB'], position)
                elif direction_list == ['N']:
                    screen.blit(paths['southOOB'], position)
                else: 
                    pass
        
        # Draw the play button
        if PLAYING:
            PAUSE_BUTTON.draw()
        else:
            PLAY_BUTTON.draw()
        RESTART_BUTTON.draw()
        NEXT_STEP.draw()
        screen.blit(FPS_LABEL, FPS_LABEL_RECT)
        # Draw the player at the starting cell
        screen.blit(next(player), reposition_img(start_cell.X, start_cell.Y))
        screen.blit(next(goal), reposition_img(ending_cell.X, ending_cell.Y))
        FPS_FIELD.draw()
        # Update the display
        pygame.display.flip()
        # limit FPS
        pygame.time.Clock().tick(CONFIG['FPS_CAP'])

        if PLAYING:
            _step()

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
    _main()


if __name__ == '__main__':
    main()
