from datatypes import Point, Direction, UndefinedDirectionError


class Robot:
    def __init__(self, x, y, direction, wallMap, groundMap, side):
        """[summary]

        Arguments:
            x -- Start X position
            y -- Start Y position
            direction -- Start facing direction
            mazeMap -- Image which is thresholded so that barriers are marked with 0 value (Black)
            side -- Side length of one block the robot can travel
        """

        self._x = x
        self._y = y
        self._direction = direction
        self._wallMap = wallMap
        self._groundMap = groundMap
        self.side = side

    def __topCornerPoint(self):
        """
        Get the position of vehicle as a Point
        """

        return Point(self._x*self.side, self._y*self.side)

    def __centerPoint(self):
        """
        Get the position of vehicle center as a Point
        """

        return self.__topCornerPoint() - self.side * 0.5

    def __leftSideDirection(self):
        """
        Get direction of left side
        """

        return (self._direction - 1) % Direction.DIRECTIONS

    def __rightSideDirection(self):
        """
        Get direction of right side
        """

        return(self._direction + 1) % Direction.DIRECTIONS

    def __go(self, forward):
        """
        Helper function to go forward/backward
        """

        directionMultiplier = 1 if forward else -1

        if (self._direction == Direction.EAST):
            self._x += directionMultiplier
        elif (self._direction == Direction.WEST):
            self._x -= directionMultiplier
        elif (self._direction == Direction.NORTH):
            self._y -= directionMultiplier
        elif (self._direction == Direction.SOUTH):
            self._y += directionMultiplier
        else:
            raise UndefinedDirectionError()

    def __rotate(self, clockwise):
        """
        Helper function to turn clockwise/anti-clockwise.
        """

        if clockwise:
            self._direction = self.__rightSideDirection()
        else:
            self._direction = self.__leftSideDirection()

    def __sendSignal(self, signalDirection, maxSignalDist=1000, barrierColor=0):
        """
        Send a signal and return distance to closest barrier
        """

        posX, posY = tuple(self.__centerPoint())
        for distance in range(maxSignalDist):
            if self._wallMap[posY, posX] == barrierColor:
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

    def __checkGround(self, trueColor=255):
        """
        Check if ground mask color
        """
        
        return self._groundMap[tuple(self.__centerPoint())] == trueColor

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

    def turnRight(self):
        """
        Turns 90' clockwise
        """

        self.__rotate(clockwise=True)

    def turnLeft(self):
        """
        Turns 90' counter-clockwise
        """

        self.__rotate(clockwise=False)

    def frontSensor(self):
        """
        Distance from front sensor to object
        """

        return self.__sendSignal(self._direction)

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

    def groundSensor(self):
        """
        True if ground has the filtered color
        """

        return self.__checkGround()
