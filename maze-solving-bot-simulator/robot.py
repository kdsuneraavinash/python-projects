from datatypes import Point, Direction, UndefinedDirectionError


class Robot:
    def __init__(self, x, y, direction, mazeMap, side):
        """[summary]

        Arguments:
            x -- Start X position
            y -- Start Y position
            direction -- Start facing direction
            mazeMap -- Image which is thresholded so that barriers are marked with 0 value (Black)
            side -- Side length of one block the robot can travel
        """

        self.x = x
        self.y = y
        self.direction = direction
        self.mazeMap = mazeMap
        self.side = side

    def __topCornerPoint(self):
        """
        Get the position of vehicle as a Point
        """

        return Point(self.x*self.side, self.y*self.side)

    def __centerPoint(self):
        """
        Get the position of vehicle center as a Point
        """

        return self.__topCornerPoint() - self.side * 0.5

    def __leftSideDirection(self):
        """
        Get direction of left side
        """

        return (self.direction - 1) % Direction.DIRECTIONS

    def __rightSideDirection(self):
        """
        Get direction of right side
        """

        return(self.direction + 1) % Direction.DIRECTIONS

    def __go(self, forward):
        """
        Helper function to go forward/backward
        """

        directionMultiplier = 1 if forward else -1

        if (self.direction == Direction.EAST):
            self.x += directionMultiplier
        elif (self.direction == Direction.WEST):
            self.x -= directionMultiplier
        elif (self.direction == Direction.NORTH):
            self.y -= directionMultiplier
        elif (self.direction == Direction.SOUTH):
            self.y += directionMultiplier
        else:
            raise UndefinedDirectionError()

    def __rotate(self, clockwise):
        """
        Helper function to turn clockwise/anti-clockwise.
        """

        if clockwise:
            self.direction = self.__rightSideDirection()
        else:
            self.direction = self.__leftSideDirection()

    def __sendSignal(self, signalDirection, maxSignalDist=1000, barrierColor=0):
        """
        Send a signal and return distance to closest barrier
        """

        posX, posY = tuple(self.__centerPoint())
        for distance in range(maxSignalDist):
            if self.mazeMap[posY, posX] == barrierColor:
                break
            if (signalDirection == Direction.EAST):
                posX += 1
            elif (signalDirection == Direction.WEST):
                posX -= 1
            elif (signalDirection == Direction.NORTH):
                posY -= 1
            elif (signalDirection == Direction.SOUTH):
                posY += 1
            else:
                raise UndefinedDirectionError()
        return distance

    def goForward(self):
        """
        Goes one step forward
        """

        self.__go(forward=True)

    def goBackward(self):
        """
        Goes one step backward
        """

        self.__go(forward=False)

    def turnClockwise(self):
        """
        Turns 90' clockwise
        """

        self.__rotate(clockwise=True)

    def turnCounterClockwise(self):
        """
        Turns 90' counter-clockwise
        """

        self.__rotate(clockwise=False)

    def frontSensor(self):
        """
        Distance from front sensor to object
        """

        return self.__sendSignal(self.direction)

    def leftSensor(self):
        """
        Distance from left sensor to object
        """

        return self.__sendSignal(self.__leftSideDirection())

    def rightSensor(self):
        """
        Distance from right sensor to object
        """

        return self.__sendSignal(self.__rightSideDirection())
