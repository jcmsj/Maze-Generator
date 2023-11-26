import pygame
from State import MazeState
from Cell import Cell
from breadth_first_search import breadth_first_search
from prim import prim
from widgets import BoolVal, Button, Button, Text, TextField, RadioButton, Val
from maze import as_matrix, export_file, import_file, import_maze_details, make_initial_maze, matrix_to_adjency_list, show_maze, matrox_to_str_adjency_list
from random_dfs import random_dfs
from depth_first_search import depth_first_search
from a_star import a_star_search
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
def tile_position(SIZE:int):
    def reposition(x:int|float,y:int|float,x_pad=0,y_pad=0):
        X_START:int = (x*SIZE) + x_pad # type: ignore
        Y_START:int = (y*SIZE) + y_pad # type: ignore
        return (X_START, Y_START)
    return reposition

def _main():
    SIZE = 75
    width = 16 #len(maze[0])
    length = 8 #len(maze)
    window_tile_width = width + 1
    window_tile_height = length + 1
    screen = pygame.display.set_mode((window_tile_width*SIZE, window_tile_height*SIZE))
    pygame.display.set_caption("Yet Another Maze Generator")
    # load the material icons font
    pygame.font.init()
    materialIcons = pygame.font.Font('assets/MaterialIconsOutlined-Regular.otf', 64)
    textFont = pygame.font.Font("assets/pixel.ttf", 24)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    CONFIG = {
        "FPS_CAP": 30,
        "GENERATOR": Val("random_dfs"),
        "ALGOS": ["random_dfs", "prim"],
        "SOLVER": Val("depth_first_search"),
        "SOLVER_ALGOS": ["breadth_first_search", "depth_first_search", "a_star" ]
    }

    # CURRYING MOMENTS
    reposition_img = tile_position(SIZE)
    def curried_select(config_key:str, ):
        def set_group(radiobuttons:list[RadioButton]):
            def set_choice(choice):
                def execute():
                    CONFIG[config_key].set(choice)
                    print(CONFIG[config_key].value)
                    for btn in radiobuttons:
                        btn.checked = btn.assigned == choice
                return execute
            return set_choice
        return set_group

    SOLVER_RADIO_BUTTONS = [
        RadioButton(
            assigned = "a_star",
            text = 'A*',
            x = 150,
            y = 615,
        ),
        RadioButton(
            assigned = 'breadth_first_search',
            text = 'BFS',
            x = 400,
            y = 615,
        ),
        RadioButton(
            assigned = 'depth_first_search',
            text = 'DFS',
            x = 650,
            y = 615,
            checked = True
        )
    ]

    GENERATOR_RADIO_BUTTONS = [
        RadioButton(
            text = 'Random DFS',
            assigned = "random_dfs",
            x = 150,
            y = 615,
            checked=True
        ),
        RadioButton(
            text = 'Prim',
            assigned = 'prim',
            x = 400,
            y = 615,
        ),
    ]

    set_solver_algo = curried_select("SOLVER")(SOLVER_RADIO_BUTTONS)
    set_generator_algo = curried_select("GENERATOR")(GENERATOR_RADIO_BUTTONS)

    for button in SOLVER_RADIO_BUTTONS:
        button.onclick = set_solver_algo(button.assigned)

    for button in GENERATOR_RADIO_BUTTONS:
        button.onclick = set_generator_algo(button.assigned)


    PLAYING = BoolVal(False)

    maze_state = MazeState.GENERATING
    player_coord = (-1,-1)
    index = 0
    gen = None
    start_cell = None
    ending_cell = None
    maze:list[list[Cell]] = []
    traversal = []
    traversal_order:list[tuple[int,int]] = []
    path = []
    def start(args=None):
        nonlocal start_cell, ending_cell, maze, gen, traversal, traversal_order, index, player_coord, path, player_x, player_y, maze_state
        traversal_order = []
        index = 0
        
        if CONFIG["GENERATOR"].value == "random_dfs":
            start_cell, ending_cell, gen, maze,traversal = random_dfs(length=length,width=width)

        elif CONFIG["GENERATOR"].value == "prim":
            maze = make_initial_maze(length=length,width=width)
            start_cell, ending_cell, gen, maze,traversal = prim(maze)
            
        player_x = start_cell.X
        player_y = start_cell.Y
        maze_state = MazeState.GENERATING
        PLAYING.to_false()
    CONFIG["GENERATOR"].observers.append(start)
    PLAY_BUTTON = Button(
        onclick= PLAYING.to_true,
        text=Text(
            'construction', 
            screen, 
            materialIcons, 
            reposition_img(16.5, 0.5),
            WHITE,
            BLACK,
        )
    )

    PAUSE_BUTTON = Button(
        onclick= PLAYING.to_false,
        text=Text(
            'pause',
            screen,
            materialIcons,
            reposition_img(16.5, 0.5),
            WHITE,
            BLACK,
        ),
    )
    def solve_maze():
        nonlocal path, traversal_order, index, maze, start_cell, ending_cell, player_coord, maze_state
        print("solving")
        maze_state = MazeState.SOLVING
        player_coord = start_cell.coordinate
        index = 0
        if CONFIG["SOLVER"].value == "depth_first_search":
            path, traversal_order = depth_first_search(maze, start_cell, ending_cell)
        elif CONFIG["SOLVER"].value == "a_star": 
            _traversal_order = a_star_search({
            "start": start_cell,
            "end": ending_cell,
            "graph": matrix_to_adjency_list(maze),
            }) or []
            traversal_order = [cell.coordinate for cell in _traversal_order]
        elif CONFIG["SOLVER"].value == "breadth_first_search": 
            path, traversal_order = breadth_first_search(matrix_to_adjency_list(maze), start_cell, ending_cell)
        else:
            raise ValueError(f"Unknown algorithm: {CONFIG['SOLVER']}")
    def _solver():
        nonlocal player_coord, index, maze_state, traversal_order
        if traversal_order and index < len(traversal_order):
            player_coord = traversal_order[index]
            index += 1
        else:
            maze_state = MazeState.SOLVED
            PLAYING.to_false()
            index = 0
            traversal_order = []
            # player_coord = ending_cell.coordinate

    def start_search_or_continue():
        nonlocal index, maze_state
        PLAYING.to_true()
        if maze_state == MazeState.SOLVED or maze_state == MazeState.GENERATED:
            solve_maze()
        
    SEARCH_BUTTON = Button(
        onclick= start_search_or_continue,
        text=Text(
            'search', 
            screen, 
            materialIcons, 
            reposition_img(16.5, 0.5),
            WHITE,
            BLACK,
        ),
    )
    def _step():
        nonlocal gen, traversal, maze_state
        if gen != None:
            try:
                next(gen)
            except:
                PLAYING.to_false()
                traversal = []
                gen = None
                maze_state = MazeState.GENERATED
        else:
            maze_state = MazeState.GENERATED

    def _skip():
        nonlocal gen, traversal, maze_state, traversal_order, player_coord, index
        if maze_state == MazeState.GENERATING:
            while gen != None:
                try:
                    next(gen)
                except:
                    PLAYING.to_false()
                    traversal = []
                    gen = None
            maze_state = MazeState.GENERATED
        elif maze_state ==  MazeState.SOLVING:
            PLAYING.to_false()
            index = 0
            traversal_order = []
            player_coord = ending_cell.coordinate
            maze_state = MazeState.SOLVED
        
    FAST_FORWARD = Button(
        onclick= _skip,
        text=Text(
            'fast_forward',
            screen,
            materialIcons,
            reposition_img(16.5,2.5),
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
    FPS_LABEL_RECT.center = reposition_img(16.5, 3.5)
    FPS_FIELD = TextField(
        screen, 
        str(CONFIG['FPS_CAP']), 
        reposition_img(16.5, 4), 
        textFont, 
        WHITE, 
        BLACK, 
        onSubmit=onFPSChange
    )
    def prompt_file_path():
        from tkinter import filedialog, messagebox
        filepath = filedialog.asksaveasfilename(defaultextension="json", filetypes=[("JSON", "*.json")], title="Save maze as JSON")
        if filepath and start_cell and ending_cell:
            export_file(
                matrox_to_str_adjency_list(maze), 
                (start_cell, ending_cell), 
                filepath 
            )
            messagebox.showinfo("Success", "Maze saved successfully")
    def load_file_path():
        from tkinter import filedialog, messagebox
        filepath = filedialog.askopenfilename(filetypes=[("JSON", "*.json")], title="Load maze from JSON")
        if not filepath:
            return
        try:
            maze_details = import_maze_details(filepath)
            nonlocal maze, start_cell, ending_cell
            maze = as_matrix(maze_details["graph"])
            start_cell = maze_details["start"]
            ending_cell = maze_details["end"]
        except:
            messagebox.showerror("Error", "Failed to load maze. Invalid data")
            return
        solve_maze()
        # The following lines are a workaround to make the search algos radio buttons show after loading a file
        # TODO: Fix this workaround
        nonlocal maze_state
        maze_state = MazeState.GENERATED
        _skip()

    LOAD_BUTTON = Button(
        onclick= load_file_path,
        text=Text(
            'upload',
            screen,
            materialIcons,
            reposition_img(16.5, 6.5),
            WHITE,
            BLACK,
        ),
    )
    SAVE_BUTTON = Button(
        onclick= prompt_file_path,
        text=Text(
            'download',
            screen,
            materialIcons,
            reposition_img(16.5, 7.5),
            WHITE,
            BLACK,
        ),
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
    player_x:int = start_cell.X or 0
    
    player_y:int = start_cell.Y or 0
    RESTART_BUTTON = Button(
        onclick= start,
        text=Text(
            'replay',
            screen,
            materialIcons,
            reposition_img(16.5, 1.5),
            WHITE, 
            BLACK,
        ),
    )
    
    player_cell = maze[player_y][player_x]
    P_CELL = TextField(
        screen, 
        player_cell.__repr__(), 
        reposition_img(16.5,5), 
        textFont, 
        WHITE, 
        BLACK, 
    )
    def player_movement(x_increase, y_increase):
        nonlocal player_x, player_y, player_cell, maze
        player_walls = [str(d) for d in player_cell.visited_walls()]
        if x_increase == -1 and 'W' in player_walls:
            player_x += x_increase
        elif x_increase == 1 and 'E' in player_walls:
            player_x += x_increase
        if y_increase == -1 and 'N' in player_walls:
            player_y += y_increase
        elif y_increase == 1 and 'S' in player_walls:
            player_y += y_increase
        player_cell = maze[player_y][player_x]
        P_CELL.update(f"({player_x}, {player_y})")

    player = animator("assets/player/playeridle", "gif", 6, (SIZE-30))
    goal = animator("assets/goal/goal", "gif", 4, (SIZE-45))
    building = animator("assets/building/Building", "gif", 3, (SIZE))

    
    # Start the game loop 
    while True:
        # Check for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if maze_state == MazeState.GENERATING:
                if PLAYING:
                    PAUSE_BUTTON.listen(event)
                else: 
                    for button in GENERATOR_RADIO_BUTTONS:
                        button.listen(event)
                    PLAY_BUTTON.listen(event)
            else:
                for button in SOLVER_RADIO_BUTTONS:
                    button.listen(event)
                
                if PLAYING:
                    PAUSE_BUTTON.listen(event)
                else: 
                    SEARCH_BUTTON.listen(event)
            RESTART_BUTTON.listen(event)
            FAST_FORWARD.listen(event)
            FPS_FIELD.listen(event)
            LOAD_BUTTON.listen(event)
            SAVE_BUTTON.listen(event)

            if event.type == pygame.KEYDOWN:
                player_movement(int(event.key == pygame.K_d) - int(event.key == pygame.K_a),int(event.key == pygame.K_s) - int(event.key == pygame.K_w))
                
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

        # For the DFS Solver
        if maze_state == MazeState.GENERATING:
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
                SEARCH_BUTTON.draw()
        if maze_state == MazeState.GENERATING:
            for buttons in GENERATOR_RADIO_BUTTONS:
                buttons.draw(screen)
        if maze_state == MazeState.SOLVED or maze_state == MazeState.GENERATED:
            for buttons in SOLVER_RADIO_BUTTONS:
                buttons.draw(screen)
         
        RESTART_BUTTON.draw()
        FAST_FORWARD.draw()
        SAVE_BUTTON.draw()
        LOAD_BUTTON.draw()
        screen.blit(FPS_LABEL, FPS_LABEL_RECT)
        # Draw the player at the starting cell
        if maze_state == MazeState.SOLVING or maze_state == MazeState.SOLVED: # Compare maze state
            xx,yy = reposition_img(player_coord[0], player_coord[1], player_x_pad, player_y_pad)
            screen.blit(next(player), (xx,yy))
            outline_x,outline_y = reposition_img(player_coord[0], player_coord[1])
            pygame.draw.rect(screen, (255,0,0),(outline_x,outline_y,SIZE,SIZE ), 6)
        else:
            screen.blit(next(player), reposition_img(player_x, player_y, player_x_pad, player_y_pad))
        screen.blit(next(goal), reposition_img(ending_cell.X, ending_cell.Y, goal_x_pad, goal_y_pad))
        FPS_FIELD.draw()
        P_CELL.draw()
        # Update the display
        pygame.display.flip()
        # limit FPS
        pygame.time.Clock().tick(CONFIG['FPS_CAP'])

        if PLAYING:
            if maze_state == MazeState.SOLVING:
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
