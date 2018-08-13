import collections

import robot
from datatypes import SimulationRunStatus, Direction
from optimized import optimized_base_script

DEBUG = True
# Top left = 0, Bottom Left = 1, Bottom Right = 2, Bottom Left = 3
DEBUG_ROTATE = 0


class OptimizedFloodFill(optimized_base_script.OptimizedUserScript):
    def __init__(self, bot: robot.Robot):
        super().__init__(bot)

        self.facing_direction_discovered: bool = None
        self.path_traced_to_center: bool = None
        self.real_run: bool = None

        self.CENTER: int = self.get_pos(self.SIDE_SQUARES // 2, self.SIDE_SQUARES // 2)

        self.flooded_grid: list = None
        self.walls: list = None

    def setup(self):
        super().setup()
        self.facing_direction_discovered = False
        self.path_traced_to_center = False
        self.real_run = False

        self.flooded_grid = [-1] * self.SIDE_SQUARES * self.SIDE_SQUARES
        self.walls = []

    def loop(self, img) -> int:
        super().loop(img)

        if not self.facing_direction_discovered:
            self.discover_facing_direction()
            self.wait_for_user_key(0)

        elif not self.path_traced_to_center:
            self.bot.set_ball_color([53, 216, 255])
            self.add_walls()
            self.flood_fill(self.CENTER)
            self.go_to_best_cell()

            if self.pos == self.CENTER:
                self.path_traced_to_center = True
                self.wait_for_user_key(0)

        elif not self.real_run:
            self.bot.set_ball_color([140, 110, 90])
            self.add_walls()
            self.flood_fill(self.START)
            self.go_to_best_cell()

            if self.pos == self.START:
                self.real_run = True
                self.wait_for_user_key(0)

        else:
            self.bot.set_ball_color([0, 255, 0])
            self.add_walls()
            self.flood_fill(self.CENTER)
            self.go_to_best_cell()

            if self.pos == self.CENTER:
                self.real_run = False
                self.wait_for_user_key(0)

        return SimulationRunStatus.RESUME_SIMULATION

    def encode_wall(self, a, b):
        if b < a:
            a, b = b, a
        return a * self.SIDE_SQUARES * self.SIDE_SQUARES + b

    def decode_wall_a(self, v):
        return v // (self.SIDE_SQUARES * self.SIDE_SQUARES)

    def decode_wall_b(self, v):
        return v % (self.SIDE_SQUARES * self.SIDE_SQUARES)

    def discover_facing_direction(self):
        """Go some distance and identify which side bot is turned"""

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

    def flood_fill(self, search_pos: int):

        # Set all cells to -1 (Unvisited)
        for i in range(self.SIDE_SQUARES * self.SIDE_SQUARES):
            self.flooded_grid[i] = -1

        # Set center cell distance to 0
        self.flooded_grid[search_pos] = 0
        queue = collections.deque([search_pos])

        while queue:
            current = queue.pop()
            current_x = self.get_x_coord(current)
            current_y = self.get_y_coord(current)

            nodes = [self.get_pos(current_x - 1, current_y),
                     self.get_pos(current_x + 1, current_y),
                     self.get_pos(current_x, current_y - 1),
                     self.get_pos(current_x, current_y + 1)]

            for node in nodes:
                # Skip if out of range
                node_x = self.get_x_coord(node)
                node_y = self.get_y_coord(node)
                if not 0 <= node_x < self.bot.no_of_squares_per_side or \
                        not 0 <= node_y < self.bot.no_of_squares_per_side:
                    continue
                # Skip if already visited
                if self.flooded_grid[node] != -1:
                    continue
                # Skip if has a wall
                wall = self.encode_wall(current, node)
                if wall in self.walls:
                    continue
                self.flooded_grid[node] = self.flooded_grid[current] + 1
                queue.appendleft(node)

    def add_wall_between(self, a: int, b: int):
        # Skip if out of range
        a_x = self.get_x_coord(a)
        a_y = self.get_y_coord(a)
        b_x = self.get_x_coord(b)
        b_y = self.get_y_coord(b)
        if not 0 <= a_x < self.SIDE_SQUARES or not 0 <= a_y < self.SIDE_SQUARES:
            return
        if not 0 <= b_x < self.SIDE_SQUARES or not 0 <= b_y < self.SIDE_SQUARES:
            return
        wall = self.encode_wall(a, b)
        self.walls.append(wall)

    def add_walls(self):
        this_node = self.pos
        front_node = self.tile_in_the_direction(self.direction)
        right_node = self.tile_in_the_direction((self.direction + 1) % 4)
        left_node = self.tile_in_the_direction((self.direction - 1) % 4)
        if self.is_wall_in_right():
            self.add_wall_between(this_node, right_node)
        if self.is_wall_in_left():
            self.add_wall_between(this_node, left_node)
        if self.is_wall_in_front():
            self.add_wall_between(this_node, front_node)

    def go_to_best_cell(self) -> int:
        x = self.get_x_coord(self.pos)
        y = self.get_y_coord(self.pos)
        nodes = [self.get_pos(x - 1, y),
                 self.get_pos(x + 1, y),
                 self.get_pos(x, y - 1),
                 self.get_pos(x, y + 1)]

        right_node = self.tile_in_the_direction((self.direction + 1) % 4)
        front_node = self.tile_in_the_direction(self.direction)
        left_node = self.tile_in_the_direction((self.direction - 1) % 4)

        min_val = self.flooded_grid[self.pos]
        min_pos = self.pos
        for node in nodes:
            # Skip if out of range
            node_x = self.get_x_coord(node)
            node_y = self.get_y_coord(node)
            if not 0 <= node_x < self.SIDE_SQUARES or \
                    not 0 <= node_y < self.SIDE_SQUARES:
                continue

            if node == right_node and self.is_wall_in_right():
                continue
            elif node == front_node and self.is_wall_in_front():
                continue
            elif node == left_node and self.is_wall_in_left():
                continue

            val = self.flooded_grid[node]
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
