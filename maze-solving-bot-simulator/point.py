class Point:
    """
    Class to define a point in X Y coordinate plane.
    Top Left of the screen is (0, 0) and X increases Left to Right and Y increases Top to Bottom.
    """

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __addition(self, other, add):
        """
        Helper function to + and - operators.

        Arguments:
            other -- Other value to add. Can be int, float, tuple, list or Point.
            add -- Boolean value indicating whether to add. If [False] performs subtraction.

        Returns:
            Point -- result of operation
        """

        multiple = 1 if add else -1
        if type(other) is float or type(other) is int:
            return Point(self.x + multiple*other, self.y + multiple*other)
        if type(other) is tuple or type(other) is list:
            return Point(self.x + multiple*other[0], self.y + multiple*other[1])
        if type(other) is Point:
            return Point(self.x + multiple*other.x, self.y + multiple*other.y)
        else:
            raise ValueError("Unknowned type: {0}".format(type(other)))

    def __add__(self, other):
        """
        Adds a value to point

        Arguments:
            other -- Other value to add.

        Returns:
            Point -- result of Point1 + Point2
        """

        return self.__addition(other, add=True)

    def __sub__(self, other):
        """
        Subtracts a value from point

        Arguments:
            other -- Other value to subtract.

        Returns:
            Point -- result of Point1 - Point2
        """

        return self.__addition(other, add=False)

    def __iter__(self):
        """
        To help convert this to tuples or lists
        """

        yield int(self.x)
        yield int(self.y)

