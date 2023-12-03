from Cell import Cell
import pygame
from typing import Callable

def tile_position(SIZE:int):
    def reposition(x:int|float,y:int|float,x_pad=0,y_pad=0):
        X_START:int = (x*SIZE) + x_pad # type: ignore
        Y_START:int = (y*SIZE) + y_pad # type: ignore
        return (X_START, Y_START)
    return reposition

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
            direction_str = "".join([str(d) for d in cell.visited_walls()])

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
