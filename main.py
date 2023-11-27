from typing import Callable
import pygame
from Cell import Cell
from breadth_first_search import breadth_first_search
from prim import prim
from widgets import BoolVal, Button, Button, Text, TextField, RadioButton, Val
from maze import as_matrix, export_file, import_maze_details, make_initial_maze, matrix_to_edgelist, matrix_to_str_edgelist
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

class Colors:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)

class Fonts:
    materialIcons:pygame.font.Font = None # type: ignore
    textFont: pygame.font.Font = None # type: ignore

    @classmethod
    def init(cls):
        pygame.font.init()
        cls.materialIcons = pygame.font.Font('assets/MaterialIconsOutlined-Regular.otf', 64)
        cls.textFont = pygame.font.Font("assets/pixel.ttf", 24)
CONFIG = {
    "FPS_CAP": 30,
    "GENERATOR": Val("random_dfs"),
    "ALGOS": ["random_dfs", "prim"],
    "SOLVER": Val("depth_first_search"),
    "SOLVER_ALGOS": ["breadth_first_search", "depth_first_search", "a_star" ]
}
def onFPSChange(val:str):
    if val.isdigit():
        CONFIG["FPS_CAP"] = int(val)
        print(f"FPS_CAP: {CONFIG['FPS_CAP']}")
        return False
    return True

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

class GeneratorScreen:
    def __init__(
        self, 
        SIZE:int, 
        width:int, 
        length:int, 
        screen:pygame.Surface, 
        paths:dict[str,pygame.Surface], 
        reposition_img:Callable[[int,int],tuple[int,int]],
        save_button: Button,
        load_button: Button,
        FPS_FIELD: TextField,
        FPS_LABEL: pygame.Surface,
        FPS_LABEL_RECT: pygame.Rect,
    ):
        self.SIZE = SIZE
        self.width = width
        self.length = length
        self.screen = screen
        self.paths = paths
        self.reposition_img = reposition_img
        self.maze:list[list[Cell]] = []
        self.traversal_order = []
        self.gen = None
        self.start_cell:Cell = None # type: ignore
        self.ending_cell:Cell = None # type: ignore
        self.PLAYING = BoolVal(False)
        self._running = True
        self.BUILDING_SPRITE = animator("assets/building/Building", "gif", 3, (SIZE))
        self.generated = False
        self.save_button = save_button
        self.load_button = load_button
        self.FPS_FIELD = FPS_FIELD
        self.FPS_LABEL = FPS_LABEL
        self.FPS_LABEL_RECT = FPS_LABEL_RECT
        self.RADIO_BUTTONS = [
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

        self.set_algo = curried_select("GENERATOR")(self.RADIO_BUTTONS)
        for button in self.RADIO_BUTTONS:
            button.onclick = self.set_algo(button.assigned)
        CONFIG["GENERATOR"].observers.append(self.start)
        self.PLAY_BUTTON = Button(
            onclick= self.PLAYING.to_true,
            text=Text(
                'construction', 
                self.screen, 
                Fonts.materialIcons, 
                self.reposition_img(16.5, 0.5), # type: ignore
                Colors.WHITE,
                Colors.BLACK,
            )
        )

        self.PAUSE_BUTTON = Button(
            onclick= self.PLAYING.to_false,
            text=Text(
                'pause',
                self.screen,
                Fonts.materialIcons,
                self.reposition_img(16.5, 0.5), # type: ignore
                Colors.WHITE,
                Colors.BLACK,
            ),
        )
        self.SEARCH_BUTTON = Button(
            onclick= self.end,
            text=Text(
                'search', 
                self.screen, 
                Fonts.materialIcons, 
                self.reposition_img(16.5, 0.5), # type: ignore
                Colors.WHITE,
                Colors.BLACK,
            ),
        )
        self.SKIP_BUTTON = Button(
            onclick= self.skip,
            text=Text(
                'fast_forward',
                self.screen,
                Fonts.materialIcons,
                self.reposition_img(16.5,2.5), # type: ignore
                Colors.WHITE,
                Colors.BLACK,
            ),
        )
        self.RESTART_BUTTON = Button(
        onclick= self.start,
        text=Text(
            'replay',
            screen,
            Fonts.materialIcons,
            reposition_img(16.5, 1.5), # type: ignore
            Colors.WHITE, 
            Colors.BLACK,
        ),
    )
 
    def end(self):
        self._running = False
    def start(self, _=None):
        self._running = True
        self.generated = False
        if CONFIG["GENERATOR"].value == "random_dfs":
            self.start_cell, self.ending_cell, self.gen,self.maze,self.traversal = random_dfs(length=self.length,width=self.width)

        elif CONFIG["GENERATOR"].value == "prim":
            self.maze = make_initial_maze(length=self.length,width=self.width)
            self.start_cell, self.ending_cell, self.gen,self.maze,self.traversal = prim(self.maze)
            
        self.PLAYING.to_false()
    def skip(self):
        while self.gen != None:
            self.step()

    def loop(self):
        while self._running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

                if self.PLAYING:
                    self.PAUSE_BUTTON.listen(event)
                elif self.generated:
                    self.SEARCH_BUTTON.listen(event)
                else:
                    self.PLAY_BUTTON.listen(event)
                self.SKIP_BUTTON.listen(event)
                self.RESTART_BUTTON.listen(event)
                self.FPS_FIELD.listen(event)
                for button in self.RADIO_BUTTONS:
                    button.listen(event)
                self.save_button.listen(event)
                self.load_button.listen(event)

                # toggle playing on spacebar
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    if self.generated:
                        self.end()
                    else:
                        self.PLAYING.toggle()
            # Draw the game screen
            self.screen.fill((0, 0, 0))
            # Draw the maze
            render_maze(
                self.maze, 
                self.width, 
                self.length, 
                self.screen, 
                self.paths, 
                self.reposition_img, 
                self.render_builder_sprite
            )
            # show the UI for generating
            if self.PLAYING:
                self.PAUSE_BUTTON.draw()
            elif self.generated:
                self.SEARCH_BUTTON.draw()
            else:
                self.PLAY_BUTTON.draw()
            self.SKIP_BUTTON.draw()
            self.RESTART_BUTTON.draw()
            self.screen.blit(self.FPS_LABEL, self.FPS_LABEL_RECT)
            self.FPS_FIELD.draw()
            self.save_button.draw()
            self.load_button.draw()
            # Paint the radio buttons
            for button in self.RADIO_BUTTONS:
                button.draw(self.screen)
            # Update the display
            pygame.display.flip()
            # limit FPS
            pygame.time.Clock().tick(CONFIG['FPS_CAP'])

            if self.PLAYING:
                self.step()
    def step(self):
        """Returns if the generator is done"""
        if self.gen != None:
            try:
                next(self.gen)
            except:
                self.PLAYING.to_false()
                self.traversal = []
                self.gen = None
                self.generated = True
        else:
            self.generated = True


    def render_builder_sprite(
            self, 
            cell:Cell, 
            position: tuple[int,int]
        ):
        if self.traversal and cell == self.traversal[-1]:
            # draw the building sprite
            self.screen.blit(next(self.BUILDING_SPRITE),position)

class SolverScreen:
    def __init__(
        self, 
        SIZE:int, 
        width:int, 
        length:int, 
        screen:pygame.Surface, 
        paths:dict[str,pygame.Surface], 
        maze: list[list[Cell]],
        save_button: Button,
        load_button: Button,
        FPS_FIELD: TextField,
        FPS_LABEL: pygame.Surface,
        FPS_LABEL_RECT: pygame.Rect,
    ):
        self.SIZE = SIZE
        self.width = width
        self.length = length
        self.screen = screen
        self.paths = paths
        self.reposition_img = tile_position(SIZE)
        self.MAZE:list[list[Cell]] = maze
        self.traversal_order = []
        self.start_cell:Cell = None # type: ignore
        self.ending_cell:Cell = None # type: ignore
        self.PLAYING = BoolVal(False)
        self.save_button = save_button
        self.load_button = load_button
        self._running = True
        self.index = 0
        self.PLAYER = animator("assets/player/playeridle", "gif", 6, (SIZE-30))
        self.GOAL = animator("assets/goal/goal", "gif", 4, (SIZE-45))
        self.PLAYER_X_PAD = 14
        self.PLAYER_Y_PAD = 3
        self.GOAL_X_PAD = 23
        self.player_coord:Val[tuple[int,int]]= Val((-1,-1))
        self.GOAL_Y_PAD = 8
        self.RADIO_BUTTONS = [
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

        self.set_algo = curried_select("SOLVER")(self.RADIO_BUTTONS)
        for button in self.RADIO_BUTTONS:
            button.onclick = self.set_algo(button.assigned)
        CONFIG["SOLVER"].observers.append(self.start)
        self.PAUSE_BUTTON = Button(
            onclick= self.PLAYING.to_false,
            text=Text(
                'pause',
                self.screen,
                Fonts.materialIcons,
                self.reposition_img(16.5, 0.5), # type: ignore
                Colors.WHITE,
                Colors.BLACK,
            ),
        )
        self.SEARCH_BUTTON = Button(
            onclick= self.start_or_continue,
            text=Text(
                'search', 
                self.screen, 
                Fonts.materialIcons, 
                self.reposition_img(16.5, 0.5), # type: ignore
                Colors.WHITE,
                Colors.BLACK,
            ),
        )
        self.SKIP_BUTTON = Button(
            onclick= self.skip,
            text=Text(
                'fast_forward',
                self.screen,
                Fonts.materialIcons,
                self.reposition_img(16.5,2.5), # type: ignore
                Colors.WHITE,
                Colors.BLACK,
            ),
        )
        self.REGENERATE_BUTTON = Button(
        onclick= self.end,
            text=Text(
                'construction',
                screen,
                Fonts.materialIcons,
                self.reposition_img(16.5, 1.5), # type: ignore
                Colors.WHITE, 
                Colors.BLACK,
            ),
        )

        self.P_CELL = TextField(
            screen, 
            self.player_coord.value.__repr__(), 
            self.reposition_img(16.5,5), 
            Fonts.textFont, 
            Colors.WHITE, 
            Colors.BLACK, 
        )
        self.player_coord.observers.append(lambda v: self.P_CELL.update(v.__repr__()))
        self.FPS_FIELD = FPS_FIELD
        self.FPS_LABEL =  FPS_LABEL
        self.FPS_LABEL_RECT = FPS_LABEL_RECT

        # Setup the trail
        self.trail_image = load_image("assets/footPath/left.png", (SIZE-40), (SIZE-40))
        self.visited_coords = []
        self.player_coord.observers.append(lambda c: self.visited_coords.append((c[0], c[1])))


    def end(self):
        self._running = False
    def skip(self):
        self.PLAYING.to_false()
        self.index = 0
        self.visited_coords = self.traversal_order
        self.traversal_order = []
        self.player_coord.set((self.ending_cell.coordinate))
    def player_movement(self,x_increase, y_increase):
        player_walls = [str(d) for d in self.MAZE[self.player_coord.value[1]][self.player_coord.value[0]].visited_walls()]
        if x_increase == -1 and 'W' in player_walls:
            self.player_coord.set((self.player_coord.value[0] + x_increase, self.player_coord.value[1]))
        elif x_increase == 1 and 'E' in player_walls:
            self.player_coord.set((self.player_coord.value[0] + x_increase, self.player_coord.value[1]))
        if y_increase == -1 and 'N' in player_walls:
            self.player_coord.set((self.player_coord.value[0], self.player_coord.value[1] + y_increase))
        elif y_increase == 1 and 'S' in player_walls:
            self.player_coord.set((self.player_coord.value[0], self.player_coord.value[1] + y_increase))
    def search(self, maze:list[list[Cell]], start_cell:Cell, ending_cell:Cell):
        self.MAZE = maze
        self.start_cell = start_cell
        self.ending_cell = ending_cell
        self.player_coord.set(self.start_cell.coordinate)
        self.visited_coords = []
        self.start()

    def start(self, _=None):
        print("solving")
        self.player_coord.set(self.start_cell.coordinate)
        self.index = 0
        self.visited_coords = []
        if CONFIG["SOLVER"].value == "depth_first_search":
            self.path, self.traversal_order = depth_first_search(self.MAZE, self.start_cell, self.ending_cell)
        elif CONFIG["SOLVER"].value == "a_star": 
            self.path, _traversal_order = a_star_search({
            "start": self.start_cell,
            "end": self.ending_cell,
            "graph": matrix_to_edgelist(self.MAZE),
            }) or []
            self.traversal_order = [cell.coordinate for cell in _traversal_order]
        elif CONFIG["SOLVER"].value == "breadth_first_search": 
            self.path, self.traversal_order = breadth_first_search(matrix_to_edgelist(self.MAZE), self.start_cell, self.ending_cell)
        else:
            raise ValueError(f"Unknown algorithm: {CONFIG['SOLVER']}")
    def loop(self):
        while self._running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

                if self.PLAYING:
                    self.PAUSE_BUTTON.listen(event)
                else:
                    self.SEARCH_BUTTON.listen(event)
                self.SKIP_BUTTON.listen(event)
                self.REGENERATE_BUTTON.listen(event)
                self.FPS_FIELD.listen(event)
                for button in self.RADIO_BUTTONS:
                    button.listen(event)
                self.save_button.listen(event)
                self.load_button.listen(event)
                if event.type == pygame.KEYDOWN:
                    self.player_movement(int(event.key == pygame.K_d) - int(event.key == pygame.K_a),int(event.key == pygame.K_s) - int(event.key == pygame.K_w))

                # toggle playing on spacebar
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.start_or_continue()
            
            # Draw the game screen
            self.screen.fill((0, 0, 0))
            # Draw the maze
            render_maze(
                self.MAZE, 
                self.width, 
                self.length, 
                self.screen, 
                self.paths, 
                self.reposition_img, 
                lambda cell, position: None
            )
            # show the UI for generating
            if self.PLAYING:
                self.PAUSE_BUTTON.draw()
            else:
                self.SEARCH_BUTTON.draw()
            self.SKIP_BUTTON.draw()
            self.REGENERATE_BUTTON.draw()
            self.screen.blit(self.FPS_LABEL, self.FPS_LABEL_RECT)
            self.FPS_FIELD.draw()
            self.save_button.draw()
            self.load_button.draw()
            self.P_CELL.draw()
            # Paint the radio buttosn
            for button in self.RADIO_BUTTONS:
                button.draw(self.screen)

            # Draw the player
            xx,yy = self.reposition_img(self.player_coord.value[0], self.player_coord.value[1], self.PLAYER_X_PAD,self. PLAYER_Y_PAD)
            self.screen.blit(next(self.PLAYER), (xx,yy))
            # Draw a red outline around the tile the player is in
            outline_x,outline_y = self.reposition_img(self.player_coord.value[0], self.player_coord.value[1])
            pygame.draw.rect(self.screen, (255,0,0),(outline_x,outline_y,self.SIZE,self.SIZE ), 6)
            # Draw the goal
            self.screen.blit(
                next(self.GOAL), 
                self.reposition_img(
                    self.ending_cell.X, 
                    self.ending_cell.Y, 
                    self.GOAL_X_PAD,
                    self.GOAL_Y_PAD
                )
            )
            # Draw the trail:
            for cell_coord in self.visited_coords:
                trail_x, trail_y = self.reposition_img(cell_coord[0], cell_coord[1], self.PLAYER_X_PAD, (self.PLAYER_Y_PAD + 15))
                self.screen.blit(self.trail_image, (trail_x, trail_y)) 
            # Update the display
            pygame.display.flip()
            # limit FPS
            pygame.time.Clock().tick(CONFIG['FPS_CAP'])

            if self.PLAYING:
                self.step()
    def step(self):
        """Returns if the generator is done"""
        if self.traversal_order and self.index < len(self.traversal_order):
            self.player_coord.set(self.traversal_order[self.index])
            self.index += 1
        else:
            self.PLAYING.to_false()
            self.index = 0
            self.traversal_order = []
            self.player_coord.set(self.ending_cell.coordinate)

    def start_or_continue(self):
        self.PLAYING.to_true()
        if self.index == 0:
            self.start()
 
def render_maze(
    maze:list[list[Cell]], 
    width:int, length:int, 
    screen:pygame.Surface, 
    paths:dict[str,pygame.Surface],
    reposition_img:Callable[[int,int],tuple[int,int]],
    overlay: Callable[[Cell, tuple[int,int]], None]
):
    for y in range(length):
        for x in range(width):
            cell = maze[y][x]
            position = reposition_img(x,y)
            direction_list = [str(d) for d in cell.visited_walls()]
            direction_str = ''.join(direction_list)
            
            match direction_str:
                case '':
                    screen.blit(paths['unsectioned'], position)
                case 'NS':
                    screen.blit(paths['VERTICAL'], position)
                case 'WE':
                    screen.blit(paths['HORIZONTAL'], position)
                case 'WNS':
                    screen.blit(paths['V_west'], position)
                case 'NES':
                    screen.blit(paths['V_east'], position)
                case 'WES':
                    screen.blit(paths['H_south'], position)
                case 'WNE':
                    screen.blit(paths['H_north'], position)
                case 'WS':
                    screen.blit(paths['SOUTHWEST'], position)
                case 'ES':
                    screen.blit(paths['SOUTHEAST'], position)
                case 'WN':
                    screen.blit(paths['NORTHWEST'], position)
                case 'NE':
                    screen.blit(paths['NORTHEAST'], position)
                case 'E':
                    screen.blit(paths['westOOB'], position)
                case 'W':
                    screen.blit(paths['eastOOB'], position)
                case 'S':
                    screen.blit(paths['northOOB'], position)
                case 'N':
                    screen.blit(paths['southOOB'], position)
                case _:
                    screen.blit(paths['INTERSECTION'], position)
            overlay(cell, position)

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
    # CURRYING MOMENTS
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
