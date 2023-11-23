import pygame
from Cell import Cell
from prim import prim
from widgets import BoolVal, Button, Button, Text, TextField
from maze import make_initial_maze, show_maze
from random_dfs import random_dfs
from depth_first_search import depth_first_search

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
    SIZE = 75
    width = 16 #len(maze[0])
    length = 8 #len(maze)
    screen = pygame.display.set_mode(((width+1)*SIZE, length*SIZE))
    pygame.display.set_caption("Yet Another Maze Generator")
    # load the material icons font
    pygame.font.init()
    materialIcons = pygame.font.Font('assets/MaterialIconsOutlined-Regular.otf', 64)
    textFont = pygame.font.Font("assets/pixel.ttf", 24)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    CONFIG = {
        "FPS_CAP": 30,
        "GENERATOR": "random_dfs",
        "ALGOS": ["random_dfs", "prim"],
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
    done_solving = False
    value = (-1,-1)
    index = 0
    gen = None
    start_cell:Cell|None = None
    ending_cell:Cell|None = None
    maze:list[list[Cell]] = []
    traversal = []
    traversal_order = []
    path = []
    done_solving = False
    def start():
        nonlocal start_cell, ending_cell, maze, gen, traversal
        if CONFIG["GENERATOR"] == "random_dfs":
            start_cell, ending_cell, gen, maze,traversal = random_dfs(length=length,width=width)
        elif CONFIG["GENERATOR"] == "prim":
            maze = make_initial_maze(length=length,width=width)
            start_cell, ending_cell, gen, maze,traversal = prim(maze)
        else:
            raise ValueError(f"Unknown algorithm: {CONFIG['ALGO']}")
    
    def solve_dfs():
        nonlocal path, traversal_order, index, maze, start_cell, ending_cell, value, done_solving
        print("solving")
        index = 0
        value = (-1,-1)
        done_solving = False
        path, traversal_order = depth_first_search(maze,start_cell,ending_cell)
        
    def _solver():
        nonlocal value, index, done_solving, traversal_order
        if traversal_order and index < len(traversal_order):
            value = traversal_order[index]
            index += 1
        else:
            done_solving = True
            PLAYING.to_false()
            value = traversal_order[-1]
            traversal_order = []

    def start_or_continue():
        nonlocal index, done_solving
        PLAYING.to_true()
        if index == 0 or done_solving:
            solve_dfs()

    PLAY_BUTTON_SOLVE = Button(
        onclick= start_or_continue,
        text=Text(
            'circle', 
            screen, 
            materialIcons, 
            (1232, 50),
            WHITE,
            BLACK,
        ),
    )
 
    def _step():
        nonlocal gen, traversal
        if gen != None:
            try:
                next(gen)
            except:
                PLAYING.to_false()
                traversal = None
                gen = None

    def _skip():
        nonlocal gen, traversal
        while gen != None:
            try:
                next(gen)
            except:
                PLAYING.to_false()
                traversal = None
                gen = None
    NEXT_STEP = Button(
        onclick= _skip,
        text=Text(
            'fast_forward',
            screen,
            materialIcons,
            (1232, 250),
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

    start()
    _step()
    player_x = start_cell.X
    
    player_y = start_cell.Y
    
    # Restart button
    def restart():
        nonlocal player_x, player_y
        start()
        player_x = start_cell.X
        player_y = start_cell.Y
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

    def reposition_img(x,y,x_pad=0,y_pad=0):
        X_START = (x*SIZE) + x_pad
        Y_START = (y*SIZE) + y_pad

        # original_scale x new_scale + diff
        # upscaling_factor = 4
        # downscaling_factor = 3
        # (1,1) * 4 = (4,4) 
        # scaled = (4,4) * 3/4 = (3,3)
        # diff = (4,4)- (3,3) = (1,1)
        # = (3.5, 3.5) add the half??
        return (X_START, Y_START)

    player = animator("assets/player/playeridle", "gif", 6, (SIZE-30))
    goal = animator("assets/goal/goal", "gif", 4, (SIZE-45))
    playerwalk = animator("assets/player/playerwalk", "gif", 4, (SIZE-30))
    building = animator("assets/building/Building", "gif", 3, (SIZE))

    # Start the game loop 
    while True:
        # Check for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if gen == None:
                if PLAYING:
                    PAUSE_BUTTON.listen(event)
                else: 
                    PLAY_BUTTON_SOLVE.listen(event)
            else:
                if PLAYING:
                    PAUSE_BUTTON.listen(event)
                else: 
                    PLAY_BUTTON.listen(event)
            RESTART_BUTTON.listen(event)
            NEXT_STEP.listen(event)
            FPS_FIELD.listen(event)
            
            if event.type == pygame.KEYDOWN:
                player_x += int(event.key == pygame.K_d) - int(event.key == pygame.K_a)
                player_y += int(event.key == pygame.K_s) - int(event.key == pygame.K_w)
                
            # event.unicode
            # check what letter
            
        # Draw the game screen
        screen.fill((0, 0, 0))
        
        player_x_pad = 14
        player_y_pad = 3
        goal_x_pad = 23
        goal_y_pad = 8
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
                if traversal and cell == traversal[-1]:
                    # draw the building sprite
                    screen.blit(next(building),position)
        # Draw the play button


        # For the DFS Solver
        if gen != None:
            # show the UI for generating
            if PLAYING:
                PAUSE_BUTTON.draw()
            else:
                PLAY_BUTTON.draw()
        else:
            # show the UI for solving
            if PLAYING:
                PAUSE_BUTTON.draw()
            else:
                PLAY_BUTTON_SOLVE.draw()
           
        RESTART_BUTTON.draw()
        NEXT_STEP.draw()
        screen.blit(FPS_LABEL, FPS_LABEL_RECT)
        # Draw the player at the starting cell
        if gen == None and not done_solving:
            xx,yy = reposition_img(value[0], value[1], player_x_pad, player_y_pad)
            screen.blit(next(player), (xx,yy))
            pygame.draw.rect(screen, (255,0,0),(xx,yy,SIZE,SIZE ), 6)
        else:
            screen.blit(next(player), reposition_img(player_x, player_y, player_x_pad, player_y_pad))
        screen.blit(next(goal), reposition_img(ending_cell.X, ending_cell.Y, goal_x_pad, goal_y_pad))
        FPS_FIELD.draw()
        # Update the display
        pygame.display.flip()
        # limit FPS
        pygame.time.Clock().tick(CONFIG['FPS_CAP'])

        if PLAYING:
            if gen == None:
                _solver()
            else:
                _step()
        
  

def main():
    length = 8
    width = 16
    STARTING_CELL,ENDING_CELL, maze_generator,maze,path = random_dfs(length=length,width=width)
    for _ in maze_generator:
        pass
    show_maze(maze, STARTING_CELL, ENDING_CELL)
    _main()


if __name__ == '__main__':
    main()
