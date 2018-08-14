import collections

import numpy

import robot
from datatypes import SimulationRunStatus
from scripts import base_script


class DepthFirstSearch(base_script.UserScript):
    def __init__(self, bot: robot.Robot):
        """Initialize"""
        super().__init__(bot)
        self.visited: set = None
        self.graph: dict = None
        self.stack: list = None
        self.center: tuple = None
        self.was_running_before: bool = None

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
        self.was_running_before = False  # Variable to record whether script just started to run or has been running

    def loop(self, img: numpy.array) -> int:
        """Loop Function"""
        super().loop(img)

        # If just started, position so front is empty
        if not self.was_running_before:
            while self.is_wall_in_front():
                self.turn_right()
            self.was_running_before = True

        if self.stack:
            return self.discover()
        else:
            return self.go_to_center()

    # --------------------------------------------------------------
    # LOOP FUNCTIONS -----------------------------------------------
    # --------------------------------------------------------------

    def discover(self) -> int:
        """First half of loop (discovering maze)"""

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
                return SimulationRunStatus.RESUME_SIMULATION
            choice = self.stack[-1]

        if choice == front_point:
            self.go_forward()
        elif choice == left_point:
            self.go_to_left()
        elif choice == right_point:
            self.go_to_right()
        else:
            self.go_backward()

    def go_to_center(self) -> int:
        """Second half of loop (going to center of maze)"""

        self.bot.set_ball_color((0, 242, 255))
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
                self.turn_right()
            elif node == left_point:
                self.turn_left()
            elif node == back_point:
                self.turn_left()
                self.turn_left()
            self.go_forward()
        self.bot.set_ball_color((0, 255, 0))

        # Refresh screen until user exits
        self.refresh_screen(self.img)
        self.user_pressed_exit(0)
        return SimulationRunStatus.STOP_SIMULATION

    # --------------------------------------------------------------
    # GRAPH THEORY ALGORITHMS --------------------------------------
    # --------------------------------------------------------------

    def bfs(self) -> dict:
        """USe breadth first search algorithm to find shortest distance from center point"""
        distances_graph = {}

        # BFS from middle to the robot start point
        start = self.center
        search = self.start

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
