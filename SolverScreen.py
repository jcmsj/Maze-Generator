from typing import Callable
from Animator import animator, load_image
from CONFIG import CONFIG, curried_select
from Cell import Cell
from Colors import Colors
from Direction import Direction
from Fonts import Fonts
from State import State
from a_star import a_star_search
from breadth_first_search import breadth_first_search
from depth_first_search import depth_first_search
from maze import matrix_to_edgelist
from render_maze import render_maze, tile_position
from widgets import BoolVal, Button, RadioButton, Text, TextField, Val
import pygame

def calc_direction(
    MAZE: list[list[Cell]],
    to:tuple[int,int], 
    traversal_order: list[tuple[int,int]]
):
    # Check the maze for t
    TARGET = MAZE[to[1]][to[0]]
    for coord in traversal_order:
        cell = MAZE[coord[1]][coord[0]]
        dx = TARGET.coordinate[0] - cell.coordinate[0]
        dy = TARGET.coordinate[1] - cell.coordinate[1]
        if abs(dx) == abs(dy) or abs(dx) > 1 or abs(dy) > 1:
            continue
        dir = Direction((dx,dy))
        if cell.walls[dir] == State.VISITED:
            return dir
    return None

class HighlightedPathRender:
    def __init__(
            self, 
            SIZE:int,
            PATH_PAD:tuple[int,int],
            reposition_img:Callable[[int,int, int,int],tuple[int,int]],
        ):
        self.SIZE = SIZE
        self.highlighted_path_sprites = {
            Direction.WEST: load_image("assets/footPathHiglight/W.png", SIZE, SIZE),
            Direction.EAST: load_image("assets/footPathHiglight/E.png", SIZE, SIZE),
            Direction.NORTH: load_image("assets/footPathHiglight/N.png", SIZE, SIZE),
            Direction.SOUTH: load_image("assets/footPathHiglight/S.png", SIZE, SIZE),
        }
        self.directions:list[tuple[tuple[int,int], Direction]] = []
        self.PATH_PAD_X = PATH_PAD[0]
        self.PATH_PAD_Y = PATH_PAD[1]
        self.reposition_img = reposition_img
 
    def render(self, screen:pygame.Surface):
        for highlighted_coord,dir in self.directions:
            screen.blit(self.highlighted_path_sprites[dir], highlighted_coord)
    def calculate(
        self, 
        path:list[tuple[int,int]],
        maze: list[list[Cell]],
        ):
        self.directions = [( # type: ignore
            self.reposition_img(*path[i], self.PATH_PAD_X, self.PATH_PAD_Y), calc_direction(maze,path[i], path)) for i in range(len(path))
        ]

class PlayerRenderer:
    def __init__(
            self,
            SIZE:int,
            PLAYER_X_PAD:int,
            PLAYER_Y_PAD:int,
            reposition_img:Callable[[int,int, int,int],tuple[int,int]],
        ):
        self.SIZE = SIZE
        self.X_PAD = PLAYER_X_PAD
        self.Y_PAD = PLAYER_Y_PAD
        self.sprite = animator("assets/ekko/idle/ekkoidle", "png", 8, (SIZE))
        self.coord: Val[tuple[int,int]] = Val((-1,-1))
        self.scaled_coord = (-1,-1)
        self.coord.observers.append(self.scale)
        self.reposition_img = reposition_img

    def scale(self, coord:tuple[int,int]):
        self.scaled_coord = self.reposition_img(coord[0], coord[1], self.X_PAD,self.Y_PAD)
    def render(self, screen:pygame.Surface):
        screen.blit(next(self.sprite), self.scaled_coord)
class TrailRenderer:
    def __init__(
            self,
            MAZE: list[list[Cell]],
            SIZE:int, 
            reposition_img:Callable[[int|float,int|float, int,int],tuple[int,int]],
            TRAIL_PAD :tuple[int,int]
    ):
        self.SIZE = SIZE
        self.MAZE = MAZE
        self.reposition_img = reposition_img
        self.visited_coords: list[tuple[tuple[int,int], Direction]] = []
        self.traversal_order: list[tuple[int,int]] = []
        self.TRAIL_X_PAD = TRAIL_PAD[0]
        self.TRAIL_Y_PAD = TRAIL_PAD[1]

        self.trail_sprites = {
            Direction.WEST: load_image("assets/footPath/W.png", SIZE, SIZE),
            Direction.EAST: load_image("assets/footPath/E.png", SIZE, SIZE),
            Direction.NORTH: load_image("assets/footPath/N.png", SIZE, SIZE),
            Direction.SOUTH: load_image("assets/footPath/S.png", SIZE, SIZE),
        }
        self.highlighted_path_sprites = {
            Direction.WEST: load_image("assets/footPathHiglight/W.png", SIZE, SIZE),
            Direction.EAST: load_image("assets/footPathHiglight/E.png", SIZE, SIZE),
            Direction.NORTH: load_image("assets/footPathHiglight/N.png", SIZE,SIZE),
            Direction.SOUTH: load_image("assets/footPathHiglight/S.png", SIZE,SIZE),
        }

    def add_visited_coords(self,coord:tuple[int,int]):
        d = calc_direction(
            MAZE=self.MAZE,
            to=coord,
            traversal_order=self.traversal_order
        )
        if d == None:
            return

        self.visited_coords.append((self.reposition(coord), d))

    def render(self, screen:pygame.Surface):
        for trail_coord, dir in self.visited_coords:
            screen.blit(self.trail_sprites[dir], trail_coord)
    def reposition(self, coord: tuple[int,int]):
        return self.reposition_img(coord[0], coord[1], self.TRAIL_X_PAD, self.TRAIL_Y_PAD)
    def skip(self):
        for coord in self.traversal_order:
            self.add_visited_coords(coord)
        # self.traversal_order = []
class CoordinateField:
    def __init__(
        self,
        screen:pygame.Surface,
        text:str,
        position:tuple[int,int],
        font:pygame.font.Font,
        color:tuple[int,int,int],
        background:tuple[int,int,int],
        MAZE:list[list[Cell]],
        onCoordChange:Callable[[tuple[int,int]],None]
    ):
        self.MAZE = MAZE
        self.screen = screen
        self.lastValid = text
        self.tupleField = TextField(
            screen,
            text,
            position,
            font,
            color,
            background,
            onSubmit=self.parse,
        )
        self.onCoordChange = onCoordChange
    def revert(self):
        self.tupleField.update(self.lastValid)
    def parse(self, text:str):
        text = text.strip(")")
        text = text.strip("(")
        try:
            (input_x, input_y) = tuple(int(s) for s in text.split(","))
        except ValueError:
            self.revert()
            return True
        if input_x < 0 or input_x >= len(self.MAZE[0]) or input_y < 0 or input_y >= len(self.MAZE):
            self.revert()
            return True
        self.onCoordChange((input_x, input_y))
        return False
    def draw(self):
        self.tupleField.draw()

    def listen(self, event):
        self.tupleField.listen(event)
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
        self.path = []
        self.reposition_img = tile_position(SIZE)
        self.MAZE:list[list[Cell]] = maze
        self.start_cell:Cell = None # type: ignore
        self.ending_cell:Cell = None # type: ignore
        self.PLAYING = BoolVal(False)
        self.save_button = save_button
        self.load_button = load_button
        self._running = True
        self.index = 0
        self.GOAL = animator("assets/goal/goal", "gif", 4, (SIZE-45))
        self.PLAYER = PlayerRenderer(SIZE-30, 14, 3, self.reposition_img)
        self.GOAL_X_PAD = 23
        self.GOAL_Y_PAD = 8
        self.RADIO_BUTTONS = [
            RadioButton(
                assigned = "a_star",
                text = 'A*',
                x = self.reposition_img(0.5, 7)[0],
                y = self.reposition_img(0.5, 8.3)[1],
            ),
            RadioButton(
                assigned = 'breadth_first_search',
                text = 'Breadth First Search',
                x = self.reposition_img(1.3, 7)[0],
                y = self.reposition_img(0.5, 8.3)[1],
                checked = True
            ),
            RadioButton(
                assigned = 'depth_first_search',
                text = 'Depth First Search',
                x = self.reposition_img(4, 7)[0],
                y = self.reposition_img(0.5, 8.3)[1],
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
        self.RESTART_BUTTON = Button(
            onclick= self.start,
            text=Text(
                'replay',
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
            self.PLAYER.coord.value.__repr__(),
            self.reposition_img(16.5,5),
            Fonts.textFont,
            Colors.WHITE,
            Colors.BLACK,
        )
        self.PLAYER.coord.observers.append(lambda v: self.P_CELL.update(v.__repr__()))
        self.FPS_FIELD = FPS_FIELD
        self.FPS_LABEL =  FPS_LABEL
        self.FPS_LABEL_RECT = FPS_LABEL_RECT

        # Setup the trail
        self.trail_sprites = {
            Direction.WEST: load_image("assets/footPath/W.png", (SIZE-40), (SIZE-40)),
            Direction.EAST: load_image("assets/footPath/E.png", (SIZE-40), (SIZE-40)),
            Direction.NORTH: load_image("assets/footPath/N.png", (SIZE-40), (SIZE-40)),
            Direction.SOUTH: load_image("assets/footPath/S.png", (SIZE-40), (SIZE-40)),
        }
        self.solved = False
        self.flag_sprite = animator("assets/flag/flag", "png", 7, (SIZE-45))
        self.flagPosition = (-1,-1)
        self.goalPosition = (-1,-1)
        self.trailRenderer = TrailRenderer(
            self.MAZE,
            self.SIZE-40,
            self.reposition_img,
            (self.PLAYER.X_PAD+8, self.PLAYER.Y_PAD + 15)
        )
        self.PLAYER.coord.observers.append(self.trailRenderer.add_visited_coords)
        self.pathRenderer = HighlightedPathRender(
            self.SIZE-40,
            (self.PLAYER.X_PAD+8, self.PLAYER.Y_PAD + 15),
            self.reposition_img) # type: ignore

        self.NEXT_STEP = Button(
            onclick= self.step,
            text=Text(
                'skip_next',
                self.screen,
                Fonts.materialIcons,
                self.reposition_img(14.5, 8.5), # type: ignore
                Colors.WHITE,
                Colors.BLACK,
            ),
        )
        self.STEP_LABEL = TextField(
            self.screen, 
            "Step", 
            self.reposition_img(13.5, 8.5), 
            Fonts.textFont, 
            Colors.WHITE, 
            Colors.BLACK
        )
        self.PLAYER.coord.observers.append(lambda _: self.STEP_LABEL.update(f"{self.index}"))
        self.PREVIOUS_STEP = Button(
            onclick= self.undo,
            text=Text(
                'skip_previous',
                self.screen,
                Fonts.materialIcons,
                self.reposition_img(12.5, 8.5), # type: ignore
                Colors.WHITE,
                Colors.BLACK,
            ),
        )
        self.START_CELL_LABEL = Text("Start:", self.screen, Fonts.textFont, self.reposition_img(7.5, 8.5), Colors.WHITE, Colors.BLACK)
        self.START_CELL_FIELD = CoordinateField(
            screen,
            "",
            self.reposition_img(8.5, 8.5), # type: ignore
            Fonts.textFont,
            Colors.WHITE,
            Colors.BLACK,
            self.MAZE,
            lambda newStart: self.search(self.MAZE, self.MAZE[newStart[1]][newStart[0]], self.ending_cell)
        )
        self.END_CELL_LABEL = Text("Goal:", self.screen, Fonts.textFont, self.reposition_img(10, 8.5), Colors.WHITE, Colors.BLACK)
        self.ENDING_CELL_FIELD = CoordinateField(
            screen,
            "",
            self.reposition_img(11, 8.5), # type: ignore
            Fonts.textFont,
            Colors.WHITE,
            Colors.BLACK,
            self.MAZE,
            lambda newEnd: self.search(self.MAZE, self.start_cell, self.MAZE[newEnd[1]][newEnd[0]])
        )
    def end(self):
        self._running = False
        self.solved = False
    def skip(self):
        self.PLAYING.to_false()
        self.index = len(self.trailRenderer.traversal_order)
        self.trailRenderer.skip()
        self.PLAYER.coord.set(self.ending_cell.coordinate)
        self.solved = True
    def player_movement(self,x_increase, y_increase):
        player_walls = [str(d) for d in self.MAZE[self.PLAYER.coord.value[1]][self.PLAYER.coord.value[0]].visited_walls()]
        if x_increase == -1 and 'W' in player_walls or x_increase == 1 and 'E' in player_walls:
            # add the current position to the traversal order
            self.trailRenderer.traversal_order.append(self.PLAYER.coord.value)
            self.PLAYER.coord.set((
                self.PLAYER.coord.value[0] + x_increase, # dx
                self.PLAYER.coord.value[1])
            )

        if y_increase == -1 and 'N' in player_walls or y_increase == 1 and 'S' in player_walls:
            self.trailRenderer.traversal_order.append(self.PLAYER.coord.value)
            self.PLAYER.coord.set((
                self.PLAYER.coord.value[0],
                self.PLAYER.coord.value[1] + y_increase # dy
            ))
    def search(self, maze:list[list[Cell]], start_cell:Cell, ending_cell:Cell):
        self.MAZE = maze
        self.start_cell = start_cell
        self.ending_cell = ending_cell
        # self.PLAYER.coord.set(self.start_cell.coordinate)
        # self.trailRenderer.visited_coords = []
        self.start()

    def start(self, _=None):
        print("solving")
        self.solved = False
        self.trailRenderer.MAZE = self.MAZE
        self.PLAYER.coord.set(self.start_cell.coordinate)
        self.trailRenderer.visited_coords = []
        self.index = 0
        # Update the field coordinates
        self.START_CELL_FIELD.tupleField.update(self.start_cell.coordinate.__repr__())
        self.ENDING_CELL_FIELD.tupleField.update(self.ending_cell.coordinate.__repr__())
        if CONFIG["SOLVER"].value == "depth_first_search":
            self.path, self.trailRenderer.traversal_order = depth_first_search(self.MAZE, self.start_cell, self.ending_cell)

        elif CONFIG["SOLVER"].value == "a_star":
            path, _traversal_order = a_star_search({
            "start": self.start_cell,
            "end": self.ending_cell,
            "graph": matrix_to_edgelist(self.MAZE),
            })
            self.path = [] if path == None else [cell.coordinate for cell in path]
            self.trailRenderer.traversal_order = [cell.coordinate for cell in _traversal_order]
        elif CONFIG["SOLVER"].value == "breadth_first_search":
            path, self.trailRenderer.traversal_order = breadth_first_search(matrix_to_edgelist(self.MAZE), self.start_cell, self.ending_cell)
            self.path = [] if path == None else [cell.coordinate for cell in path]
        else:
            raise ValueError(f"Unknown algorithm: {CONFIG['SOLVER']}")

        # Note: The main loop can be optimized by pre-calculating the tile positions
        self.pathRenderer.calculate(self.path, self.MAZE)
        self.goalPosition = self.reposition_img(self.ending_cell.X, self.ending_cell.Y, self.GOAL_X_PAD, self.GOAL_Y_PAD)
        self.flagPosition = self.reposition_img(self.start_cell.X, self.start_cell.Y, self.GOAL_X_PAD, self.GOAL_Y_PAD)

    def loop(self):
        while self._running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

                if self.PLAYING:
                    self.PAUSE_BUTTON.listen(event)
                elif self.solved:
                    self.RESTART_BUTTON.listen(event)
                else:
                    self.SEARCH_BUTTON.listen(event)
                self.START_CELL_FIELD.listen(event)
                self.ENDING_CELL_FIELD.listen(event)
                if not self.solved:
                    self.NEXT_STEP.listen(event)
                self.PREVIOUS_STEP.listen(event)
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
                    if self.PLAYING:
                        self.PLAYING.to_false()
                    else:
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
            elif self.solved:
                self.RESTART_BUTTON.draw()
            else:
                self.SEARCH_BUTTON.draw()
            self.NEXT_STEP.draw()

            self.PREVIOUS_STEP.draw()
            self.STEP_LABEL.draw()
            self.SKIP_BUTTON.draw()
            self.REGENERATE_BUTTON.draw()
            self.screen.blit(self.FPS_LABEL, self.FPS_LABEL_RECT)
            self.FPS_FIELD.draw()
            self.save_button.draw()
            self.load_button.draw()
            self.P_CELL.draw()

            # Coordinate changing
            self.START_CELL_FIELD.draw()
            self.ENDING_CELL_FIELD.draw()
            self.START_CELL_LABEL.draw()
            self.END_CELL_LABEL.draw()

            # Paint the radio buttosn
            for button in self.RADIO_BUTTONS:
                button.draw(self.screen)

            # Draw the trail:
            self.trailRenderer.render(self.screen)
            # Draw the highlighted path
            if self.solved:
                self.pathRenderer.render(self.screen)

            #Draw the flag
            self.screen.blit(next(self.flag_sprite), self.flagPosition)

            # Draw the player
            self.PLAYER.render(self.screen)
            # Draw a red outline
            outline_x,outline_y = self.reposition_img(self.PLAYER.coord.value[0], self.PLAYER.coord.value[1])
            pygame.draw.rect(self.screen, Colors.RED,(outline_x,outline_y,self.SIZE,self.SIZE ), 6)
            # Draw a red outline around the tile the player is in
            # Draw the goal
            self.screen.blit(
                next(self.GOAL),
                self.goalPosition
            )

            # Update the display
            pygame.display.flip()
            # limit FPS
            pygame.time.Clock().tick(CONFIG['FPS_CAP'])

            if self.PLAYING:
                self.step()
    def step(self):
        """Returns if the generator is done"""
        if self.trailRenderer.traversal_order and self.index < len(self.trailRenderer.traversal_order):
            self.PLAYER.coord.set(self.trailRenderer.traversal_order[self.index])
            self.index += 1
        else:
            self.PLAYING.to_false()
            self.index = len(self.trailRenderer.traversal_order)
            self.PLAYER.coord.set(self.ending_cell.coordinate)
            self.solved = True
    def undo(self):
        if self.solved:
            self.solved = False

        if self.index > 0:
            self.index -= 1
            self.PLAYER.coord.set(self.trailRenderer.traversal_order[self.index])


    def start_or_continue(self):
        self.PLAYING.to_true()
        if self.index == 0:
            self.start()
