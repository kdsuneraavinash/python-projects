import cv2
import numpy

import robot
import utils
from datatypes import Direction, SimulationRunStatus


class UserScript:

    def __init__(self, bot: robot.Robot):
        self.bot = bot
        self.direction: int = None
        self.x: int = None
        self.y: int = None
        self.start: int = None
        self.waitDuration: int = None

    # --------------------------------------------------------------
    # ROBOT MOVEMENT -----------------------------------------------
    # --------------------------------------------------------------

    def turn_right(self, refresh):
        """Turn the bot 90' right"""
        self.direction = (self.direction + 1) % 4
        self.bot.turn_right()
        refresh()

    def turn_left(self, refresh):
        """Turn the bot 90' right"""
        self.direction = (self.direction - 1) % 4
        self.bot.turn_left()
        refresh()

    def go_forward(self, refresh):
        """Goes One step forward"""
        self.x, self.y = self.tile_in_the_direction(self.direction)
        self.bot.go_forward()
        refresh()

    # HIGHER ORDER -------------------------------------------------

    def go_to_right(self, refresh):
        """Goes to Right side tile"""
        self.turn_right(refresh)
        self.go_forward(refresh)

    def go_to_left(self, refresh):
        """Goes to Left side tile"""
        self.turn_left(refresh)
        self.go_forward(refresh)

    def go_backward(self, refresh):
        """Goes to tile behind"""
        self.turn_right(refresh)
        self.turn_right(refresh)
        self.go_forward(refresh)

    # --------------------------------------------------------------
    # ROBOT SENSOR DATA --------------------------------------------
    # --------------------------------------------------------------

    def is_wall_in_front(self) -> bool:
        """Return True if wall is in front"""
        return self.bot.front_sensor() < self.bot.side

    def is_wall_in_right(self) -> bool:
        """Return True if wall is in right"""
        return self.bot.right_sensor() < self.bot.side

    def is_wall_in_left(self) -> bool:
        """Return True if wall is in left"""
        return self.bot.left_sensor() < self.bot.side

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

    def refresh_screen(self, img: numpy.array):
        """Refreshes Screen"""
        utils.refresh_screen(img, self.bot)
        self.sleep(self.waitDuration)

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
        """Wait for some time and if Esc pressed return True"""
        pressed_key = UserScript.wait_for_user_key(timeout)
        if pressed_key == 27:
            cv2.destroyAllWindows()
            return SimulationRunStatus.STOP_SIMULATION
        return SimulationRunStatus.RESUME_SIMULATION

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
        return SimulationRunStatus.RESUME_SIMULATION
