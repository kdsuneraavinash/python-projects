import cv2
import numpy

import robot
import utils
from datatypes import Direction, SimulationRunStatus


class UserScript:

    def __init__(self, bot: robot.Robot):
        """Initializing method. Specifies all instance variables used.
        Values which should be considered as CONSTANTS are given the value
        and other variables are give 'None' value"""
        self.bot = bot
        self.direction: int = None
        self.x: int = None
        self.y: int = None
        self.start: tuple = None
        self.waitDuration: int = None
        self.img: numpy.array = None

    # --------------------------------------------------------------
    # ROBOT MOVEMENT -----------------------------------------------
    # --------------------------------------------------------------

    def turn_right(self):
        """Turn the bot 90' right"""
        self.direction = (self.direction + 1) % 4
        self.bot.turn_right()
        self.refresh_screen(self.img)

    def turn_left(self):
        """Turn the bot 90' right"""
        self.direction = (self.direction - 1) % 4
        self.bot.turn_left()
        self.refresh_screen(self.img)

    def go_forward(self):
        """Goes One step forward"""
        self.x, self.y = self.tile_in_the_direction(self.direction)
        self.bot.go_forward()
        self.refresh_screen(self.img)

    # HIGHER ORDER -------------------------------------------------

    def go_to_right(self, ):
        """Goes to Right side tile"""
        self.turn_right()
        self.go_forward()

    def go_to_left(self, ):
        """Goes to Left side tile"""
        self.turn_left()
        self.go_forward()

    def go_backward(self):
        """Goes to tile behind"""
        self.turn_right()
        self.turn_right()
        self.go_forward()

    # --------------------------------------------------------------
    # ROBOT SENSOR DATA --------------------------------------------
    # --------------------------------------------------------------

    def is_wall_in_front(self) -> bool:
        """Return True if wall is in front"""
        return self.bot.front_sensor() < self.bot.cell_side_length

    def is_wall_in_right(self) -> bool:
        """Return True if wall is in right"""
        return self.bot.right_sensor() < self.bot.cell_side_length

    def is_wall_in_left(self) -> bool:
        """Return True if wall is in left"""
        return self.bot.left_sensor() < self.bot.cell_side_length

    def is_ground_center(self) -> bool:
        """Check if ground color is center color"""
        return self.bot.ground_sensor()

    # --------------------------------------------------------------
    # HELPER FUNCTIONS ---------------------------------------------
    # --------------------------------------------------------------

    def tile_in_the_direction(self, direction: int) -> tuple:
        """ Get the coordinates of the tile in the 'direction'"""
        dir_x = self.x
        dir_y = self.y
        if direction == Direction.EAST:
            dir_x += 1
        elif direction == Direction.WEST:
            dir_x -= 1
        elif direction == Direction.NORTH:
            dir_y -= 1
        elif direction == Direction.SOUTH:
            dir_y += 1
        return dir_x, dir_y

    def refresh_screen(self, img: numpy.array) -> bool:
        """Refreshes Screen"""
        utils.refresh_screen(img, self.bot)
        return self.user_pressed_exit(self.waitDuration)

    # --------------------------------------------------------------
    # STATIC METHODS -----------------------------------------------
    # --------------------------------------------------------------

    @staticmethod
    def wait_for_user_key(timeout: int) -> int:
        """Return user interruption"""
        return cv2.waitKey(timeout)

    @staticmethod
    def sleep(timeout: int):
        """Wait for some time"""
        UserScript.wait_for_user_key(timeout)

    @staticmethod
    def user_pressed_exit(timeout: int) -> bool:
        """Wait for some time and if Esc pressed exit, otherwise return False"""
        pressed_key = UserScript.wait_for_user_key(timeout)
        if pressed_key == 27:
            cv2.destroyAllWindows()
            raise SystemExit
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

    def loop(self, img: numpy.array):
        """Loop Function"""
        self.img = img
        return SimulationRunStatus.RESUME_SIMULATION
