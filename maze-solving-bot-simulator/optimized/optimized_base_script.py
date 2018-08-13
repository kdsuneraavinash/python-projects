import cv2
import numpy

import robot
import utils

# #define values
NORTH = 0
EAST = 1
SOUTH = 2
WEST = 3

# No implementation
WAIT_DURATION = 200


class OptimizedUserScript:

    def __init__(self, bot: robot.Robot):
        self.bot = bot

        # Constants
        self.SIDE_SQUARES = bot.no_of_squares_per_side
        self.START = 0

        # Positional variables
        self.direction: int = None
        self.pos: int = None

        # No implementation in Arduino, so no need to optimize
        self.img: numpy.array = None

    # ==============================================================
    # ENTRY POINTS =================================================
    # ==============================================================

    def setup(self):
        """Setup function"""
        # Have SOME initial values, doesn't matter what the values are
        self.direction = NORTH
        self.pos = self.START

    def loop(self, img: numpy.array):
        """Loop Function"""
        self.img = img

    # ==============================================================
    # DIRECT IMPLEMENTATION IN ARDUINO =============================
    # ==============================================================

    def tile_in_the_direction(self, direction: int) -> int:
        """ Get the coordinates of the tile in the 'direction'"""
        x = self.get_x_coord(self.pos)
        y = self.get_y_coord(self.pos)
        if direction == EAST:
            x += 1
        elif direction == WEST:
            x -= 1
        elif direction == NORTH:
            y -= 1
        elif direction == SOUTH:
            y += 1
        return self.get_pos(x, y)

    def get_x_coord(self, pos):
        return pos // self.SIDE_SQUARES

    def get_y_coord(self, pos):
        return pos % self.SIDE_SQUARES

    def get_pos(self, x, y):
        return x * self.SIDE_SQUARES + y

    # ==============================================================
    # NO DIRECT IMPLEMENTATION IN ARDUINO ==========================
    # ==============================================================

    # ROBOT MOVEMENT -----------------------------------------------

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
        self.pos = self.tile_in_the_direction(self.direction)
        self.bot.go_forward()
        self.refresh_screen(self.img)

    # HIGHER ORDER MOVEMENT ---------------------------------------

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
        self.turn_left()
        self.turn_left()
        self.go_forward()

    # ROBOT SENSOR DATA --------------------------------------------

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

    def refresh_screen(self, img: numpy.array) -> bool:
        """Refreshes Screen"""
        utils.refresh_screen(img, self.bot)
        return self.user_pressed_exit(WAIT_DURATION)

    # --------------------------------------------------------------
    # STATIC METHODS -----------------------------------------------
    # --------------------------------------------------------------

    @staticmethod
    def wait_for_user_key(timeout: int) -> int:
        """Return user interruption"""
        return cv2.waitKey(timeout)

    @staticmethod
    def user_pressed_exit(timeout: int) -> bool:
        """Wait for some time and if Esc pressed exit, otherwise return False"""
        pressed_key = OptimizedUserScript.wait_for_user_key(timeout)
        if pressed_key == 27:
            cv2.destroyAllWindows()
            raise SystemExit
        return False
