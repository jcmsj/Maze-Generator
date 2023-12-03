from Animator import animator
from CONFIG import CONFIG, curried_select
from Cell import Cell
from Colors import Colors
from Fonts import Fonts
from maze import make_initial_maze
from prim import prim
from random_dfs import random_dfs
from render_maze import render_maze
from widgets import BoolVal, Button, RadioButton, Text, TextField
import pygame
from typing import Callable

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
                x = self.reposition_img(0.5, 8.3)[0], # type: ignore
                y = self.reposition_img(0.5, 8.3)[1], # type: ignore
                checked=True
            ),
            RadioButton(
                text = 'Prim',
                assigned = 'prim',
                x = self.reposition_img(2.5, 8.3)[0], # type: ignore
                y = self.reposition_img(2.5, 8.3)[1], # type: ignore
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
            'delete',
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
