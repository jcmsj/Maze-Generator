from Direction import DIRECTIONS
from State import State
import re

class Cell:
    def __init__(self, x:int, y:int ) -> None:
        self.X = x
        self.Y = y
        # For every direction, set the wall in that direction as unvisited
        self.walls = {d:State.UNVISITED for d in DIRECTIONS}

    def unvisited_walls(self):
        """Returns a list of directions that are unvisited"""
        return [dir for dir, state in self.walls.items() if state == State.UNVISITED]

    def __repr__(self) -> str:
        return f'({self.X},{self.Y})'

    @property
    def visited(self) -> bool:
        return State.VISITED in self.walls.values()

    @classmethod
    def from_str(cls, s:str):
        digit_scanner = re.compile('\\d+')
        x,y = [int(i) for i in digit_scanner.findall(s)]
        return Cell(x,y)

    def __str__(self) -> str:
        return self.__repr__()

    def __doc__(self):
        """Represents a cell in a grid.

        Attributes:
        - X: The x-coordinate of the cell.
        - Y: The y-coordinate of the cell.
        - walls: A dictionary representing the state of each wall of the cell.
        """
