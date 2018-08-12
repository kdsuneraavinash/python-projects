import cv2
from datatypes import Direction
import utils


class UserScript:

    def __init__(self, bot):
        self.bot = bot

    # --------------------------------------------------------------
    # ROBOT MOVEMENT -----------------------------------------------
    # --------------------------------------------------------------

    def turnRight(self,  refresh):
        """Turn the bot 90' right"""
        self.direction = (self.direction + 1) % 4
        self.bot.turnRight()
        refresh()

    def turnLeft(self,  refresh):
        """Turn the bot 90' right"""
        self.direction = (self.direction - 1) % 4
        self.bot.turnLeft()
        refresh()

    def goForward(self, refresh):
        """Goes One step forward"""
        self.x, self.y = self.tileInTheDirection(self.direction)
        self.bot.goForward()
        refresh()

    # HIGHER ORDER -------------------------------------------------

    def goToRight(self, refresh):
        """Goes to Right side tile"""
        self.turnRight(refresh)
        self.goForward(refresh)

    def goToLeft(self, refresh):
        """Goes to Left side tile"""
        self.turnLeft(refresh)
        self.goForward(refresh)

    def goBackward(self, refresh):
        """Goes to tile behind"""
        self.turnRight(refresh)
        self.turnRight(refresh)
        self.goForward(refresh)

    # --------------------------------------------------------------
    # ROBOT SENSOR DATA --------------------------------------------
    # --------------------------------------------------------------

    def isWallInFront(self):
        """Return True if wall is in front"""
        return self.bot.frontSensor() < self.bot.side

    def isWallInRight(self):
        """Return True if wall is in right"""
        return self.bot.rightSensor() < self.bot.side

    def isWallInLeft(self):
        """Return True if wall is in left"""
        return self.bot.leftSensor() < self.bot.side

    def isGroundCenter(self):
        """Check if ground color is center color"""
        return self.bot.groundSensor()

    # --------------------------------------------------------------
    # HELPER FUNCTIONS ---------------------------------------------
    # --------------------------------------------------------------

    def tileInTheDirection(self, direction):
        """ Get the coordinates of the tile in the 'direction'"""
        dirX = self.x
        dirY = self.y
        if (direction == Direction.EAST):
            dirX += 1
        elif (direction == Direction.WEST):
            dirX -= 1
        elif (direction == Direction.NORTH):
            dirY -= 1
        elif (direction == Direction.SOUTH):
            dirY += 1
        return (dirX, dirY)

    def refreshScreen(self, img):
        """Refreshes Screen"""
        utils.refreshScreen(img, self.bot)
        self.sleep(self.waitDuration)

    def waitForUserKey(self, timeout):
        """Return user interruption"""
        return cv2.waitKey(timeout)

    def sleep(self, timeout):
        """Wait for some time"""
        self.waitForUserKey(timeout)

    def userPressedExit(self, timeout):
        """Wait for some time and if Esc pressed return True"""
        pressedKey = self.waitForUserKey(timeout)
        if pressedKey == 27:
            cv2.destroyAllWindows()
            return True
        return False

    # --------------------------------------------------------------
    # RUNNING ENTRY POINTS -----------------------------------------
    # --------------------------------------------------------------

    def setup(self):
        """Setup function"""
        # Have SOME initial values, doesn't matter what the values are
        self.start = (0, 0)
        self.x, self.y = self.start
        self.direction = Direction.NORTH
        self.waitDuration = 100

    def loop(self, img):
        """Loop Function"""
        print("Override loop() method")
