import cv2
from direction import Direction, UndefinedDirectionError
from point import Point
import numpy as np
from collections import defaultdict


class Vehicle:
    """
    Class to define a vehicle which can move forward/backward and rotate 90'
    """

    def __init__(self, x, y, direction, threshholded):
        """
        Initalizes a new vehicle

        Arguments:
            x -- Current X coordinate of the vehicle.
            y -- Current Y coordinate of the vehicle
            direction -- Current direction vehicle is facing as defined by Direction class
        """

        self.side = 55
        self.minX = -float("inf")
        self.minY = -float("inf")
        self.maxX = float("inf")
        self.maxY = float("inf")

        self.x = x
        self.y = y
        self.direction = direction
        self.threshholded = threshholded

        self.graph = defaultdict(set)
        self.visited = set()
        self.goForwardRemember = False
        self.clockWiseTurnRemember = False

    def __realPoint(self):
        """
        Get the position of vehicle as a Point

        Returns:
            [Point] -- Point object which refer to the position of top left corner of vehicle tile in the screen
        """

        return Point(self.x*self.side, self.y*self.side)

    def __centerPoint(self):
        """
        Get the position of vehicle center as a Point

        Returns:
            [Point] -- Point object which refer to the position of center in the screen
        """

        return self.__realPoint() - self.__sidePercent(50)

    def __sidePercent(self, percentage):
        """
        Get a percentage of side length

        Arguments:
            percentage -- Integer between 0-100

        Returns:
            float -- side length percentage
        """

        return self.side * percentage * 0.01

    def __sendSignal(self, signalDirection):
        posX, posY = tuple(self.__centerPoint())
        for step in range(1000):
            if self.threshholded[posY, posX] == 0:
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
        isPath = step > self.side
        return isPath

    def __getPoint(self, direction):
        if (direction == Direction.EAST):
            return self.x + 1, self.y
        elif (direction == Direction.WEST):
            return self.x - 1, self.y
        elif (direction == Direction.NORTH):
            return self.x, self.y - 1
        elif (direction == Direction.SOUTH):
            return self.x, self.y + 1
        else:
            raise UndefinedDirectionError()

    def traverse(self):
        this = self.getCurrentPos()

        front = self.__sendSignal(self.front())
        left = self.__sendSignal(self.left())
        right = self.__sendSignal(self.right())

        if self.goForwardRemember:
            self.goForwardRemember = False
            self.goForward()
            return
        
        if self.clockWiseTurnRemember:
            self.clockWiseTurnRemember = False
            self.goForwardRemember = True
            self.turnClockwise()
            return

        self.visited.add(this)

        if not(front or left or right):
            # No Path (visited ot unvisited)
            self.turnClockwise()
            self.clockWiseTurnRemember = True
        else:
            if right:
                self.graph[this].add(self.__getPoint(self.right()))
            if front:
                self.graph[this].add(self.__getPoint(self.front()))
            if left:
                self.graph[this].add(self.__getPoint(self.left()))

            if right:
                self.turnClockwise()
                self.goForwardRemember = True
            elif front:
                self.goForward()
            elif left:
                self.turnCounterClockwise()
                self.goForwardRemember = True
            else:
                raise ValueError("Impossible path")


    def setBoundaries(self, minX, minY, maxX, maxY):
        """
        Set boundaries for the vehicle so it cannot exceed them

        Arguments:
            minX -- minimum X vehicle can obtain
            minY -- minimum Y vehicle can obtain
            maxX -- maximum X vehicle can obtain
            maxY -- maximum Y vehicle can obtain
        """

        self.minX = minX
        self.minY = minY
        self.maxX = maxX
        self.maxY = maxY

    def drawVehicle(self, img):
        """
        Draws a vehicle in the image

        Arguments:
            img -- cv2 image denoting original image. This image will be modified.

        Raises:
            UndefinedDirectionError -- when direction is not a value which is defined

        Returns:
            image -- Modified image. Note that the original image will be modified and returned.
        """

        middle = self.__centerPoint()

        rectStart = middle - self.__sidePercent(30)
        rectEnd = middle + self.__sidePercent(30)

        circleRadius = self.__sidePercent(20)
        side25p = self.__sidePercent(25)
        if (self.direction == Direction.EAST):
            circleCenter = middle + (side25p, 0)
        elif (self.direction == Direction.WEST):
            circleCenter = middle + (-side25p, 0)
        elif (self.direction == Direction.NORTH):
            circleCenter = middle + (0, -side25p)
        elif (self.direction == Direction.SOUTH):
            circleCenter = middle + (0, side25p)
        else:
            raise UndefinedDirectionError()

        colorBlack = (0, 0, 0)
        colorOrange = (23, 74, 230)

        cv2.rectangle(img, tuple(rectStart), tuple(
            rectEnd), colorOrange, cv2.FILLED)
        cv2.rectangle(img, tuple(rectStart), tuple(rectEnd), colorBlack, 1)

        cv2.circle(img, tuple(circleCenter), int(
            circleRadius), colorBlack, cv2.FILLED)

        return img

    def __go(self, forward):
        """
        Helper function to go forward/backward

        Arguments:
            forward -- Boolean value indicating going forward.

        Raises:
            UndefinedDirectionError -- when direction is not a value which is defined
        """

        if forward:
            if (self.direction == Direction.EAST):
                self.x += 1 if self.maxX != self.x else 0
            elif (self.direction == Direction.WEST):
                self.x -= 1 if self.minX != self.x else 0
            elif (self.direction == Direction.NORTH):
                self.y -= 1 if self.minY != self.y else 0
            elif (self.direction == Direction.SOUTH):
                self.y += 1 if self.maxY != self.y else 0
            else:
                raise UndefinedDirectionError()

    def __turn(self, clockwise):
        """
        Helper function to turn clockwise/anti-clockwise.

        Arguments:
            clockwise -- Boolean value indicating turning clockwise.
        """

        self.direction = self.right() if clockwise else self.left()

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

        self.__turn(clockwise=True)

    def turnCounterClockwise(self):
        """
        Turns 90' counter-clockwise
        """

        self.__turn(clockwise=False)

    def front(self):
        return self.direction

    def left(self):
        return (self.direction - 1) % Direction.DIRECTIONS

    def right(self):
        return(self.direction + 1) % Direction.DIRECTIONS

    def getCurrentPos(self):
        return (self.x, self.y)
