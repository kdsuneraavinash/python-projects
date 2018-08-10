class Direction:
    """
    Directions enum
    """

    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3
    DIRECTIONS = 4

class UndefinedDirectionError(Exception):
    def __init__(self):
        self.message = "Direction is not defined"

    def __str__(self):
        return self.message