"""
Define user script here.
All 'userscripts must,
    - include a setup() and loop(img) function
    - call super().setup() inside setup method
    - include a __init__() method and initialize instance attributes
    - call super().__init__(bot) inside __init__() method
    - loop must accept one variable as img, but try not to change img value. If you change it change it in-place. Can
    use img to tasks such as refreshing window

- Setup will run only once at the simulation initialization
- Loop will run each time screen is updated(by default)
- You can force screen refresh by util.refreshScreen(), however note that additional loop() functions will not run at
these forced refreshes
- If loop() returns STOP_SIMULATION value, simulation will stop.

Set these global variable values to set bot settings. Place settings at the end of file.
    - settingsImagePath : Image path of maze
    - settingsStartX, settingsStartY : Start position of bot
    - settingsFaceDirection : Direction bot is facing
    - settingsGridSideSquares : Squares per each side in maze grid
    - settingsSrcClass : Default class to load as Src

Since bot has no way of knowing some values in real world,
    - Try not to use bot functions rather than basic movement and sensor
    - Try not to use bot position variables such as bot.x, bot.direction
    - It is OK to access bot.side because it is known in most situations
    - Try not to use settings values

Use UserScript variables/methods,
    - turn_right, turn_left, go_forward, go_to_right, go_to_left, go_backward: Movement
    - is_wall_in_front, is_wall_in_left, is_wall_in_right: Sensor data
    - tile_in_the_direction, refresh_screen, wait_for_user_key, sleep, user_pressed_exit: Helpers
    - self.start, self.x, self.y, self.direction, self.wait_duration
"""
import collections

import numpy

import base_script
import robot
from datatypes import Direction

STOP_SIMULATION = 0x542
RESUME_LOOP = 0x546


class DepthFirstSearch(base_script.UserScript):
    def __init__(self, bot: robot.Robot):
        """Initialize"""
        super().__init__(bot)
        self.visited: set = None
        self.graph: dict = None
        self.stack: list = None
        self.center: tuple = None

    # --------------------------------------------------------------
    # HELPER FUNCTIONS ---------------------------------------------
    # --------------------------------------------------------------

    def add_edge_between(self, a: tuple, b: tuple):
        """Adds an edge between A and B"""
        if a not in self.graph:
            self.graph[a] = set()
        if b not in self.graph:
            self.graph[b] = set()
        self.graph[a].add(b)
        self.graph[b].add(a)

    # --------------------------------------------------------------
    # RUNNING ENTRY POINTS -----------------------------------------
    # --------------------------------------------------------------

    def setup(self):
        """Setup function"""
        super().setup()

        self.visited = set()  # variable to record visited nodes
        self.graph = dict()  # graph
        self.stack = [self.start]  # Stack to DFS

    def loop(self, img: numpy.array) -> int:
        """Loop Function"""

        # Refresh screen with img (to be passed to movement functions)
        def refresh():
            self.refresh_screen(img)

        if self.stack:
            return self.discover(refresh)
        else:
            return self.go_to_center(refresh)

    # --------------------------------------------------------------
    # LOOP FUNCTIONS -----------------------------------------------
    # --------------------------------------------------------------

    def discover(self, refresh) -> int:
        """First half of loop (discovering maze)"""

        # Wait and get pressed key (if key is pressed)
        if self.user_pressed_exit(10):
            return STOP_SIMULATION

        # Get sensor data
        no_wall_in_front = not self.is_wall_in_front()
        no_wall_in_left = not self.is_wall_in_left()
        no_wall_in_right = not self.is_wall_in_right()

        # get neighboring tiles
        # Get current and neighboring points
        this_point: tuple = self.stack[-1]
        front_point = self.tile_in_the_direction(self.direction)
        right_point = self.tile_in_the_direction((self.direction + 1) % 4)
        left_point = self.tile_in_the_direction((self.direction - 1) % 4)

        # mark this point as discovered
        self.visited.add(this_point)

        # Check if this is center tile
        if self.is_ground_center():
            self.center = this_point

        # Record all possible turns and add to the graph
        if no_wall_in_front:
            self.add_edge_between(front_point, this_point)
        if no_wall_in_left:
            self.add_edge_between(left_point, this_point)
        if no_wall_in_right:
            self.add_edge_between(right_point, this_point)

        # For each choice it can take
        for choice in self.graph[this_point]:
            # If choice was not discovered before, do it
            if choice not in self.visited:
                self.stack.append(choice)
                break
        else:
            # No undiscovered nodes near robot (No choice to make)
            # Start to backtrack
            self.stack.pop()
            if not self.stack:
                # Came back to initial position
                # Start second half
                return RESUME_LOOP
            choice = self.stack[-1]

        if choice == front_point:
            self.go_forward(refresh)
        elif choice == left_point:
            self.go_to_left(refresh)
        elif choice == right_point:
            self.go_to_right(refresh)
        else:
            self.go_backward(refresh)

    def go_to_center(self, refresh) -> int:
        """Second half of loop (going to center of maze)"""

        # Compute distance Grid and shortest path
        grid = self.bfs()
        path = self.shortest_path(grid)

        # For each node
        for node in path:
            # Get points near it (front one is not needed)
            back_point = self.tile_in_the_direction((self.direction + 2) % 4)
            right_point = self.tile_in_the_direction((self.direction + 1) % 4)
            left_point = self.tile_in_the_direction((self.direction - 1) % 4)

            # Go to the next node in path
            if node == right_point:
                self.turn_right(refresh)
            elif node == left_point:
                self.turn_left(refresh)
            elif node == back_point:
                self.turn_left(refresh)
                self.turn_left(refresh)
            self.go_forward(refresh)

        # Wait for Esc press and Exit
        while not self.user_pressed_exit(10):
            pass
        return STOP_SIMULATION

    # --------------------------------------------------------------
    # GRAPH THEORY ALGORITHMS --------------------------------------
    # --------------------------------------------------------------

    def bfs(self) -> dict:
        """USe breadth first search algorithm to find shortest distance from center point"""
        distances_graph = {}

        # BFS from middle to the robot start point
        start = self.center
        search = (0, 0)

        distances_graph[start] = 0
        queue = collections.deque([start])

        while True:
            # Get next node
            node = queue.pop()

            if node == search:
                # If this is the one we need, search no more
                break

            for neighbor in self.graph[node]:
                if neighbor not in distances_graph:
                    # If distance to neighbor hasn't been calculated, calculate it
                    queue.appendleft(neighbor)
                    distances_graph[neighbor] = distances_graph[node] + 1

        return distances_graph

    def shortest_path(self, distance_graph: dict) -> list:
        """USe dynamic programming to to find shortest distance path"""
        # Start from start pos
        start = self.start
        path = []

        node = start
        while True:
            # Default min point is point itself
            min_node = node
            min_val = distance_graph[node]
            # Find a neighbor that has lowest distance from center
            for neighbor in self.graph[node]:
                # If neighbor is not mapped in distanceGraph then it is a member that is far away
                if neighbor not in distance_graph:
                    continue
                val = distance_graph[neighbor]
                if min_val > val:
                    min_val = val
                    min_node = neighbor
            node = min_node
            # Add node to path
            path.append(node)

            if min_val == 0:
                # Center found
                break
        return path


settingsImagePath = "Maze.png"
settingsStartX = 1
settingsStartY = 1
settingsFaceDirection = Direction.EAST
settingsGridSideSquares = 14
settingsSrcClass = DepthFirstSearch
