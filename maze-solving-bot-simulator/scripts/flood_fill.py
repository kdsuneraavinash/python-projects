import collections

import cv2
import numpy

import robot
import utils
from datatypes import SimulationRunStatus, Direction
from scripts import base_script

DEBUG = True
# Top left = 0, Bottom Left = 1, Bottom Right = 2, Top Right = 3
DEBUG_ROTATE = 3


class FloodFill(base_script.UserScript):
    def __init__(self, bot: robot.Robot):
        """Initialize"""
        super().__init__(bot)
        self.facing_direction_discovered: bool = None
        self.path_traced_to_center: bool = None
        self.real_run: bool = None
        self.center: tuple = None
        self.flooded_grid: list = None
        self.walls: dict = None

    def refresh_screen(self, img: numpy.array):
        """Refreshes screen. Overrides parent function to show debug window"""
        if DEBUG:
            self.show_debug_data(img)
        super().refresh_screen(img)

    def setup(self):
        """Setup"""
        super().setup()
        self.facing_direction_discovered = False  # Whether direction which the bot is facing detected
        self.path_traced_to_center = False  # Whether went to center at least once
        self.real_run = False  # Whether this is the trip from Start to Center
        self.center = (self.bot.no_of_squares_per_side // 2, self.bot.no_of_squares_per_side // 2)  # Center coordinates
        self.flooded_grid = [[-1] * self.bot.no_of_squares_per_side for _ in range(self.bot.no_of_squares_per_side)]
        self.walls = {}  # All walls

    def loop(self, img) -> int:
        """Loop"""
        super().loop(img)

        if not self.facing_direction_discovered:
            self.discover_facing_direction()

        elif not self.path_traced_to_center:
            def located():
                self.path_traced_to_center = True

            self.traverse_to_point(self.center, [53, 216, 255], located)

        elif not self.real_run:
            def located():
                self.real_run = True

            self.traverse_to_point(self.start, [140, 110, 90], located)

        else:
            def located():
                self.real_run = False

            self.traverse_to_point(self.center, [0, 255, 0], located)

        self.user_pressed_exit(self.waitDuration)
        return SimulationRunStatus.RESUME_SIMULATION

    def traverse_to_point(self, target: tuple, ball_color: list, on_locate):
        """Go to a point while flooding"""
        self.bot.set_ball_color(ball_color)
        self.add_walls()
        self.flood_fill(target)
        self.go_to_best_cell()

        if (self.x, self.y) == target:
            on_locate()
            self.wait_for_user_key(0)

    def discover_facing_direction(self):
        """Go some distance and identify which side bot is turned"""

        self.sleep(1000)

        # First place bot so that it faces an empty space ahead
        if not self.is_wall_in_right():
            self.turn_right()
        elif not self.is_wall_in_left():
            self.turn_left()
        elif not self.is_wall_in_front():
            pass
        else:
            self.turn_right()
            self.turn_right()

        #  Then mark current direction as EAST assuming it is in top left facing east
        self.direction = Direction.EAST

        # go forward until there is a position with no wall on side
        while self.is_wall_in_right() and self.is_wall_in_left():
            self.go_forward()

        direction_assumption_correct = True
        # Then there is a wall on one side
        if not self.is_wall_in_right():
            # wall is in right side
            # so correct assuming that we were facing EAST
            pass
        else:
            # Wall is in left
            # So we were facing SOUTH
            direction_assumption_correct = False

        # Go back to start position
        self.turn_right()
        self.turn_right()
        while not self.is_wall_in_front():
            self.go_forward()
        self.turn_right()
        self.turn_right()

        if not direction_assumption_correct:
            self.direction = Direction.SOUTH

        self.facing_direction_discovered = True
        print(self.direction)

    def flood_fill(self, search_pos):
        """Fill and build flood array"""

        # Set all cells to -1 (Unvisited)
        for i in range(self.bot.no_of_squares_per_side):
            for j in range(self.bot.no_of_squares_per_side):
                self.flooded_grid[i][j] = -1

        # Set center cell distance to 0
        self.flooded_grid[search_pos[1]][search_pos[0]] = 0
        queue = collections.deque([search_pos])

        while queue:
            current = queue.pop()
            nodes = [(current[0] - 1, current[1]),
                     (current[0] + 1, current[1]),
                     (current[0], current[1] - 1),
                     (current[0], current[1] + 1)]
            for node in nodes:
                # Skip if out of range
                if not 0 <= node[0] < self.bot.no_of_squares_per_side or \
                        not 0 <= node[1] < self.bot.no_of_squares_per_side:
                    continue
                # Skip if already visited
                if self.flooded_grid[node[0]][node[1]] != -1:
                    continue
                # Skip if has a wall
                if current in self.walls:
                    if node in self.walls[current]:
                        continue
                self.flooded_grid[node[0]][node[1]] = self.flooded_grid[current[0]][current[1]] + 1
                queue.appendleft(node)

    def add_wall_between(self, a: tuple, b: tuple):
        # Skip if out of range
        if not 0 <= a[0] < self.bot.no_of_squares_per_side or \
                not 0 <= a[1] < self.bot.no_of_squares_per_side:
            return
        if not 0 <= b[0] < self.bot.no_of_squares_per_side or \
                not 0 <= b[1] < self.bot.no_of_squares_per_side:
            return
        if a not in self.walls:
            self.walls[a] = set()
        if b not in self.walls:
            self.walls[b] = set()
        self.walls[a].add(b)
        self.walls[b].add(a)

    def add_walls(self):
        """Add a wall between 2 nodes"""
        this_node = (self.x, self.y)
        front_node = self.tile_in_the_direction(self.direction)
        right_node = self.tile_in_the_direction((self.direction + 1) % 4)
        left_node = self.tile_in_the_direction((self.direction - 1) % 4)
        if self.is_wall_in_right():
            self.add_wall_between(this_node, right_node)
        if self.is_wall_in_left():
            self.add_wall_between(this_node, left_node)
        if self.is_wall_in_front():
            self.add_wall_between(this_node, front_node)

    def go_to_best_cell(self) -> tuple:
        """Select best neighbor node and traverse to it"""
        nodes = [(self.x - 1, self.y),
                 (self.x + 1, self.y),
                 (self.x, self.y - 1),
                 (self.x, self.y + 1)]

        right_node = self.tile_in_the_direction((self.direction + 1) % 4)
        front_node = self.tile_in_the_direction(self.direction)
        left_node = self.tile_in_the_direction((self.direction - 1) % 4)

        min_val = self.flooded_grid[self.x][self.y]
        min_pos = (self.x, self.y)
        for node in nodes:
            # Skip if out of range
            if not 0 <= node[0] < self.bot.no_of_squares_per_side or \
                    not 0 <= node[1] < self.bot.no_of_squares_per_side:
                continue

            if node == right_node and self.is_wall_in_right():
                continue
            elif node == front_node and self.is_wall_in_front():
                continue
            elif node == left_node and self.is_wall_in_left():
                continue

            val = self.flooded_grid[node[0]][node[1]]
            if val < min_val:
                min_val = val
                min_pos = node

        if min_pos == right_node:
            self.go_to_right()
        elif min_pos == front_node:
            self.go_forward()
        elif min_pos == left_node:
            self.go_to_left()
        else:
            self.go_backward()

        return min_pos

    def show_debug_data(self, img: numpy.array):
        debug_data = numpy.copy(img)
        utils.draw_robot(self.bot, debug_data)

        for _ in range(DEBUG_ROTATE):
            debug_data = cv2.rotate(debug_data, cv2.ROTATE_90_CLOCKWISE)

        cv2.circle(debug_data, (self.bot.cell_side_length // 2, self.bot.cell_side_length // 2),
                   self.bot.cell_side_length // 2, (0, 0, 255), 1)
        cv2.circle(debug_data, (len(img) // 2, len(img) // 2),
                   self.bot.cell_side_length, (0, 0, 255), 1)

        for wall_a in self.walls:
            left_a = wall_a[0] * self.bot.cell_side_length + self.bot.cell_side_length // 2
            top_a = wall_a[1] * self.bot.cell_side_length + self.bot.cell_side_length // 2
            for wall_b in self.walls[wall_a]:
                left_b = wall_b[0] * self.bot.cell_side_length + self.bot.cell_side_length // 2
                top_b = wall_b[1] * self.bot.cell_side_length + self.bot.cell_side_length // 2
                cv2.line(debug_data, (left_a, top_a), (left_b, top_b), (220, 220, 128), 10)

        for col_i in range(self.bot.no_of_squares_per_side):
            col = self.flooded_grid[col_i]
            for row_i in range(self.bot.no_of_squares_per_side):
                cell = col[row_i]
                top = row_i * self.bot.cell_side_length + 3 * self.bot.cell_side_length // 4
                left = col_i * self.bot.cell_side_length + 1 * self.bot.cell_side_length // 4
                cv2.putText(debug_data, "{:>2} ".format(cell), (left, top), cv2.FONT_HERSHEY_PLAIN,
                            1, (0, 0, 0), 1, cv2.LINE_AA)

        cv2.imshow("debug", debug_data)
