import pygame
from Animator import load_image
from CONFIG import CONFIG
from Colors import Colors
from Fonts import Fonts
from GeneratorScreen import GeneratorScreen
from SolverScreen import SolverScreen
from render_maze import tile_position
from widgets import Button, Button, Text, TextField
from maze import as_matrix, export_file, import_maze_details, matrix_to_str_edgelist

def onFPSChange(val:str):
    if val.isdigit():
        CONFIG["FPS_CAP"] = int(val)
        print(f"FPS_CAP: {CONFIG['FPS_CAP']}")
        return False
    return True

def main():
    SIZE = 75
    width = 16 #len(maze[0])
    length = 8 #len(maze)
    window_tile_width = width + 1
    window_tile_height = length + 1
    screen = pygame.display.set_mode((window_tile_width*SIZE, window_tile_height*SIZE))
    pygame.display.set_caption("Yet Another Maze Generator")
    Fonts.init()
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
    reposition_img = tile_position(SIZE)

    FPS_LABEL = Fonts.textFont.render('FPS:', True, Colors.WHITE, Colors.BLACK)
    FPS_LABEL_RECT = FPS_LABEL.get_rect()
    FPS_LABEL_RECT.center = reposition_img(16.5, 3.5) # type: ignore
    FPS_FIELD = TextField(
        screen, 
        str(CONFIG['FPS_CAP']), 
        reposition_img(16.5, 4),  # type: ignore
        Fonts.textFont, 
        Colors.WHITE, 
        Colors.BLACK, 
        onSubmit=onFPSChange
    )
    
    def prompt_file_path():
        from tkinter import filedialog, messagebox
        filepath = filedialog.asksaveasfilename(defaultextension="json", filetypes=[("JSON", "*.json")], title="Save maze as JSON")
        if filepath and GENERATOR_SCREEN.start_cell and GENERATOR_SCREEN.ending_cell:
            export_file(
                matrix_to_str_edgelist(GENERATOR_SCREEN.maze), 
                (GENERATOR_SCREEN.start_cell,GENERATOR_SCREEN.ending_cell), 
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
            maze = as_matrix(maze_details["graph"])
            # check the dimensions of this maze is the same with the constants. Otherwise show an error for now
            if len(maze) != length or len(maze[0]) != width:
                messagebox.showerror("Error", f"Failed to load maze!\n Maze dimensions must be {width} by {length}.\n Got {len(maze[0])} by {len(maze)} ")
                return
            GENERATOR_SCREEN.maze = maze
            GENERATOR_SCREEN.start_cell = maze_details["start"]
            GENERATOR_SCREEN.ending_cell = maze_details["end"]
            GENERATOR_SCREEN.end()
            if SOLVER_SCREEN._running:
                SOLVER_SCREEN.search(
                    GENERATOR_SCREEN.maze,
                    GENERATOR_SCREEN.start_cell,
                    GENERATOR_SCREEN.ending_cell
                )
        except:
            messagebox.showerror("Error", "Failed to load maze. Invalid data")
            return

    LOAD_BUTTON = Button(
        onclick= load_file_path,
        text=Text(
            'upload',
            screen,
            Fonts.materialIcons,
            reposition_img(16.5, 6.5),
            Colors.WHITE,
            Colors.BLACK,
        ),
    )
    SAVE_BUTTON = Button(
        onclick= prompt_file_path,
        text=Text(
            'download',
            screen,
            Fonts.materialIcons,
            reposition_img(16.5, 7.5),
            Colors.WHITE,
            Colors.BLACK,
        ),
    )
    GENERATOR_SCREEN = GeneratorScreen(
        SIZE, 
        width, length, 
        screen, 
        paths, 
        reposition_img, 
        SAVE_BUTTON,
        LOAD_BUTTON,
        FPS_FIELD,
        FPS_LABEL,
        FPS_LABEL_RECT,
    )
    GENERATOR_SCREEN.start()
    SOLVER_SCREEN = SolverScreen(
        SIZE, 
        width, length, 
        screen, 
        paths, 
        GENERATOR_SCREEN.maze,      
        SAVE_BUTTON,
        LOAD_BUTTON,
        FPS_FIELD,
        FPS_LABEL,
        FPS_LABEL_RECT,
    )

    # Start the game loop 
    while True:
        GENERATOR_SCREEN.start()
        GENERATOR_SCREEN.loop()
        SOLVER_SCREEN.MAZE = GENERATOR_SCREEN.maze
        SOLVER_SCREEN._running = True
        SOLVER_SCREEN.search(
            GENERATOR_SCREEN.maze, 
            GENERATOR_SCREEN.start_cell, 
            GENERATOR_SCREEN.ending_cell
        )
        SOLVER_SCREEN.loop()

if __name__ == '__main__':
    main()
