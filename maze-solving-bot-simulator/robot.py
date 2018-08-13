import numpy as np

from datatypes import Point, Direction


class Robot:
    def __init__(self, x: int, y: int, direction: int, wall_map: np.array, ground_map: np.array,
                 no_of_squares_per_side: int, cell_side_length: int):
        """[summary]

        Arguments:
            x -- Start X position
            y -- Start Y position
            direction -- Start facing direction
            wall_map -- Image which is filtered so that barriers are marked with 0 value (Black)
            ground_map -- Image which is filtered so that ground colors are marked with 255 value (White)
            side -- Side length of one block the robot can travel
        """

        self._x = x
        self._y = y
        self._direction = direction
        self._wallMap = wall_map
        self._groundMap = ground_map
        self.no_of_squares_per_side = no_of_squares_per_side
        self.cell_side_length = cell_side_length
        self._ball_color = (0, 0, 0)

    def _top_corner_point(self) -> Point:
        """Get the position of vehicle as a Point"""

        return Point(self._x * self.cell_side_length, self._y * self.cell_side_length)

    def _center_point(self) -> Point:
        """Get the position of vehicle center as a Point"""

        return self._top_corner_point() - self.cell_side_length * 0.5

    def _left_side_direction(self) -> int:
        """Get direction of left side"""

        return (self._direction - 1) % Direction.DIRECTIONS

    def _right_side_direction(self) -> int:
        """Get direction of right side"""

        return (self._direction + 1) % Direction.DIRECTIONS

    def _go(self, forward: bool):
        """Helper function to go forward/backward"""

        direction_multiplier = 1 if forward else -1

        if self._direction == Direction.EAST:
            self._x += direction_multiplier
        elif self._direction == Direction.WEST:
            self._x -= direction_multiplier
        elif self._direction == Direction.NORTH:
            self._y -= direction_multiplier
        elif self._direction == Direction.SOUTH:
            self._y += direction_multiplier

    def _rotate(self, clockwise: bool):
        """Helper function to turn clockwise/anti-clockwise."""

        if clockwise:
            self._direction = self._right_side_direction()
        else:
            self._direction = self._left_side_direction()

    def _send_signal(self, signal_direction: int, max_signal_dist: int = 1000, barrier_color: int = 0) -> int:
        """Send a signal and return distance to closest barrier"""

        pos_x, pos_y = tuple(self._center_point())
        distance = max_signal_dist
        for distance in range(max_signal_dist):
            if self._wallMap[pos_y, pos_x] == barrier_color:
                break
            if signal_direction == Direction.EAST:
                pos_x += 1
            elif signal_direction == Direction.WEST:
                pos_x -= 1
            elif signal_direction == Direction.NORTH:
                pos_y -= 1
            elif signal_direction == Direction.SOUTH:
                pos_y += 1
        return distance

    def _check_ground(self, true_color: int = 255) -> bool:
        """Check if ground mask color"""

        return self._groundMap[tuple(self._center_point())] == true_color

    def go_forward(self):
        """Goes one step forward"""

        self._go(forward=True)

    def go_backward(self):
        """Goes one step backward"""

        self._go(forward=False)

    def turn_right(self):
        """Turns 90' clockwise"""

        self._rotate(clockwise=True)

    def turn_left(self):
        """Turns 90' counter-clockwise"""

        self._rotate(clockwise=False)

    def front_sensor(self) -> int:
        """Distance from front sensor to object"""

        return self._send_signal(self._direction)

    def left_sensor(self) -> int:
        """Distance from left sensor to object"""

        return self._send_signal(self._left_side_direction())

    def right_sensor(self) -> int:
        """Distance from right sensor to object"""

        return self._send_signal(self._right_side_direction())

    def ground_sensor(self) -> bool:
        """True if ground has the filtered color"""

        return self._check_ground()

    def set_ball_color(self, color):
        """Set ball color of the robot (Analogous to a LED)"""

        self._ball_color = color
