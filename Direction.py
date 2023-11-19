from enum import Enum

class Direction(Enum):
    WEST = (-1,0)
    NORTH = (0,-1)
    EAST = (1,0)
    SOUTH = (0,1)

    def inverse(self):
        match self:
            case Direction.WEST:
                return Direction.EAST
            case Direction.NORTH:
                return Direction.SOUTH
            case Direction.EAST:
                return Direction.WEST
            case Direction.SOUTH:
                return Direction.NORTH
            case _:
                raise Exception("Invalid Direction")

    def __str__(self):
        return self.show()
    def show(self) -> str:
        match self:
            case Direction.WEST:
                return 'W'
            case Direction.NORTH:
                return 'N'
            case Direction.EAST:
                return 'E'
            case Direction.SOUTH:
                return 'S'
            case _:
                raise Exception("Invalid Direction")
            
DIRECTIONS = list(Direction)
