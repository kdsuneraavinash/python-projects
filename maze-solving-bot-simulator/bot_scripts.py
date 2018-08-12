"""
Define user script here.
All userscripts must,
    - include a setup() and loop(img) function
    - include a __init__() method which takes 'bot' parameter
    - Should NOT include any methods which affects the value of bot in __init__()
    - loop must accept one variable as img, but try not to change img value. If you change it change it in-place. Can use img to tasks such as refreshing window
    
- Setup will run only once at the simulation initialization
- Loop will run each time screen is updated(by default)
- You can force screen refresh by util.refreshScreen(), however note that additional loop() functions will not run at these forced refreshes
- If loop() returns STOP_SIMULATION value, simulation will stop.
- Call cv2.destroyAllWindows() to close current window. However if not STOP_SIMULATION is issued, new refresh will cause a new window to load.
- Use cv2.waitKey(0) to wait for a KeyPress

Set these global varible values to set bot settings. Place settings at the end of file.
    - settingsImagePath : Image path of maze
    - settingsStartX, settingsStartY : Start position of bot
    - settingsFaceDirection : Direction bot is facing
    - settingsGridSideSquares : Squares per each side in maze grid
    - settingsSrcClass : Default class to load as Src
"""
import cv2
from datatypes import Direction
import utils

STOP_SIMULATION = 0x435

kWaitDuration = 100


class UserKeyRobotCollisionEnabled:
    def __init__(self, bot):
        self.bot = bot

    def setup(self):
        pass

    def loop(self, img):
        pressedKey = cv2.waitKey(0)
        if pressedKey == 27:
            cv2.destroyAllWindows()
            return STOP_SIMULATION
        elif pressedKey == ord('w'):
            distanceToFrontObstacle = self.bot.frontSensor()
            if distanceToFrontObstacle >= self.bot.side:
                self.bot.goForward()
        elif pressedKey == ord('a'):
            self.bot.turnLeft()
        elif pressedKey == ord('d'):
            self.bot.turnRight()


class RightHandSide:
    def __init__(self, bot):
        self.bot = bot

    def setup(self):
        pass

    def loop(self, img):
        def refresh():
            utils.refreshScreen(img, self.bot)
            cv2.waitKey(kWaitDuration)

        pressedKey = cv2.waitKey(kWaitDuration)
        if pressedKey == 27:
            cv2.destroyAllWindows()
            return STOP_SIMULATION
        frontObstacle = self.bot.frontSensor()
        leftObstacle = self.bot.leftSensor()
        rightObstacle = self.bot.rightSensor()
        if (rightObstacle >= self.bot.side):
            self.bot.turnRight()
            refresh()
            self.bot.goForward()
        elif (frontObstacle >= self.bot.side):
            self.bot.goForward()
        elif (leftObstacle >= self.bot.side):
            self.bot.turnLeft()
            refresh()
            self.bot.goForward()
        else:
            self.bot.turnRight()
            refresh()
            self.bot.turnRight()
            refresh()
            self.bot.goForward()


class DFS:
    def __init__(self, bot):
        self.bot = bot
        self.visited = set()
        self.stack = [(settingsStartX, settingsStartY)]

    def __right(self, refresh):
        # print("Right")
        self.bot.turnRight()
        refresh()
        self.bot.goForward()

    def __forward(self, refresh):
        # print("Forward")
        self.bot.goForward()

    def __left(self, refresh):
        # print("Left")
        self.bot.turnLeft()
        refresh()
        self.bot.goForward()

    def __back(self, refresh):
        # print("Back")
        self.bot.turnRight()
        refresh()
        self.bot.turnRight()
        refresh()
        self.bot.goForward()

    def __directionPoint(self, direction):
        dirX = self.bot.x
        dirY = self.bot.y
        if (direction == Direction.EAST):
            dirX += 1
        elif (direction == Direction.WEST):
            dirX -= 1
        elif (direction == Direction.NORTH):
            dirY -= 1
        elif (direction == Direction.SOUTH):
            dirY += 1
        return (dirX, dirY)

    def setup(self):
        pass

    def loop(self, img):
        def refresh():
            utils.refreshScreen(img, self.bot)
            cv2.waitKey(kWaitDuration)

        pressedKey = cv2.waitKey(kWaitDuration)
        if pressedKey == 27 or not self.stack:
            cv2.destroyAllWindows()
            return STOP_SIMULATION

        frontObstacleFree = self.bot.frontSensor() >= self.bot.side
        leftObstacleFree = self.bot.leftSensor() >= self.bot.side
        rightObstacleFree = self.bot.rightSensor() >= self.bot.side

        # Get current and neighboring points
        thisPoint = self.stack[-1]
        frontPoint = self.__directionPoint(self.bot.direction)
        rightPoint = self.__directionPoint((self.bot.direction + 1)%4)
        leftPoint =self. __directionPoint((self.bot.direction - 1)%4)

        # mark this point as discovered
        self.visited.add(thisPoint)

        # Record all possible turns
        choices = set()
        if frontObstacleFree:
            choices.add(frontPoint)
        if leftObstacleFree:
            choices.add(leftPoint)
        if rightObstacleFree:
            choices.add(rightPoint)
        
        for choice in choices:
            # If found at least un discovered node, travel in it
            if choice not in self.visited:
                self.stack.append(choice)
                self.didBackedLastTime = False
                break
        else:
            # No undiscovered nodes near robot
            # Start to backtrack
            self.stack.pop()
            if not self.stack:
                # All done
                return
            choice = self.stack[-1]

        if choice == frontPoint:
            self.__forward(refresh)
        elif choice == leftPoint:
            self.__left(refresh)
        elif choice == rightPoint:
            self.__right(refresh)
        else:
            self.__back(refresh)


settingsImagePath = "Maze.png"
settingsStartX = 1
settingsStartY = 1
settingsFaceDirection = Direction.EAST
settingsGridSideSquares = 14
settingsSrcClass = DFS
