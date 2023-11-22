from Direction import DIRECTIONS, Direction
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

    def visited_walls(self):
        """Returns a list of directions that are visited"""
        return [dir for dir, state in self.walls.items() if state == State.VISITED]
    def __repr__(self) -> str:
        return f'({self.X},{self.Y})'
    def non_blocked_walls(self):
        return [d for d in self.walls if self.walls[d] != State.BLOCKED]
    @property
    def visited(self) -> bool:
        return State.VISITED in self.walls.values()

    def visit(self, other: "Cell", d:Direction):
        # Remove the wall between the current cell and chosen cell... 
        self.walls[d] = State.VISITED
        # and the chosen cell
        other.walls[d.inverse()] = State.VISITED

    @classmethod
    def from_str(cls, s:str):
        digit_scanner = re.compile('\\d+')
        x,y = [int(i) for i in digit_scanner.findall(s)]
        return Cell(x,y)

    def __str__(self) -> str:
        return self.__repr__()
    
    def __lt__(self, other):
        """ To support using < operator """
        return self.X < other.X and self.Y < other.Y
    def __le__(self, other):
        """ To support using <= operator """
        return self.X <= other.X and self.Y <= other.Y
    
    def __doc__(self):
        """Represents a cell in a grid.

        Attributes:
        - X: The x-coordinate of the cell.
        - Y: The y-coordinate of the cell.
        - walls: A dictionary representing the state of each wall of the cell.
        """
