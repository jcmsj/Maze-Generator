from enum import Enum

class State(Enum):
    """
    Represents the state of a node or element.

    Attributes:
        UNVISITED: The node or element has not been visited.
        VISITED: The node or element has been visited.
        BLOCKED: The node or element is blocked or inaccessible.

    Methods:
        __str__: Returns the name of the state as a string.
    """

    UNVISITED = 0
    VISITED = 1
    BLOCKED = 2

    def __str__(self):
        return self.name

class MazeState(Enum):
    GENERATING = 0
    GENERATED = 1
    SOLVING = 2
    SOLVED = 3
