class Direction:
    """Directions enum"""

    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3
    DIRECTIONS = 4


class SimulationRunStatus:
    """Simulation Run Status enum"""

    STOP_SIMULATION = 0x234
    RESUME_SIMULATION = 0x345


class Point:
    """Class to define a point in X Y coordinate plane.
    Top Left of the screen is (0, 0) and X increases Left to Right and Y increases Top to Bottom. """

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __addition(self, other, add: bool):
        """Helper function to + and - operators."""

        multiple = 1 if add else -1
        if type(other) is float or type(other) is int:
            return Point(self.x + multiple * other, self.y + multiple * other)
        if type(other) is tuple or type(other) is list:
            return Point(self.x + multiple * other[0], self.y + multiple * other[1])
        if type(other) is Point:
            return Point(self.x + multiple * other.x, self.y + multiple * other.y)
        else:
            return self

    def __add__(self, other):
        """Adds a value to point"""

        return self.__addition(other, add=True)

    def __sub__(self, other):
        """Subtracts a value from point"""

        return self.__addition(other, add=False)

    def __iter__(self):
        """To help convert this to tuples or lists"""

        yield int(self.x)
        yield int(self.y)
