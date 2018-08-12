"""
Define user script here.
All userscripts must,
    - include a setup() and loop(img) function
    - call base.UserScript.setup(self) inside setup method
    - SHOULD NOT include a __init__() method
    - loop must accept one variable as img, but try not to change img value. If you change it change it in-place. Can use img to tasks such as refreshing window

- Setup will run only once at the simulation initialization
- Loop will run each time screen is updated(by default)
- You can force screen refresh by util.refreshScreen(), however note that additional loop() functions will not run at these forced refreshes
- If loop() returns STOP_SIMULATION value, simulation will stop.

Set these global varible values to set bot settings. Place settings at the end of file.
    - settingsImagePath : Image path of maze
    - settingsStartX, settingsStartY : Start position of bot
    - settingsFaceDirection : Direction bot is facing
    - settingsGridSideSquares : Squares per each side in maze grid
    - settingsSrcClass : Default class to load as Src

Since bot has no way of knowing some values in real world,
    - Try not to use bot functions rather than basic movement and sensor
    - Try not to use bot postion variables such as bot.x, bot.direction
    - It is OK to access bot.side because it is known in most situations
    - Try not to use settings values

Use UserScript variables/methods,
    - turnRight, turnLeft, goForward, goToRight, goToLeft, goBackward: Movement
    - isWallInFront, isWallInLeft, isWallInRight: Sensor data
    - tileInTheDirection, refreshScreen, waitForUserKey, sleep, userPressedExit: Helpers
    - self.start, self.x, self.y, self.direction, self.waitDuration
"""
from datatypes import Direction
import collections
import base

STOP_SIMULATION = 0x435


class DeapthFirstSearch(base.UserScript):
    # --------------------------------------------------------------
    # HELPER FUNCTIONS ---------------------------------------------
    # --------------------------------------------------------------

    def addEdgeBetween(self, a, b):
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
        base.UserScript.setup(self)

        self.visited = set()  # variable to record visited nodes
        self.graph = {}  # graph
        self.stack = [self.start]  # Stack to DFS

    def loop(self, img):
        """Loop Function"""

        # Refresh screen with img (to be passed to movement functions)
        def refresh(): self.refreshScreen(img)

        if self.stack:
            return self.discover(refresh)
        else:
            return self.goToCenter(refresh, img)

    # --------------------------------------------------------------
    # LOOP FUNCTIONS -----------------------------------------------
    # --------------------------------------------------------------

    def discover(self, refresh):
        """First half of loop (discovering maze)"""

        # Wait and get pressed key (if key is pressed)
        if self.userPressedExit(10):
            return STOP_SIMULATION

        # Get sensor data
        noWallInFront = not self.isWallInFront()
        noWallInLeft = not self.isWallInLeft()
        noWallInRight = not self.isWallInRight()

        # get neighboring tiles
        # Get current and neighboring points
        thisPoint = self.stack[-1]
        frontPoint = self.tileInTheDirection(self.direction)
        rightPoint = self.tileInTheDirection((self.direction + 1) % 4)
        leftPoint = self. tileInTheDirection((self.direction - 1) % 4)

        # mark this point as discovered
        self.visited.add(thisPoint)

        # Check if this is center tile
        if self.isGroundCenter():
            self.center = thisPoint

        # Record all possible turns and add to the graph
        if noWallInFront:
            self.addEdgeBetween(frontPoint, thisPoint)
        if noWallInLeft:
            self.addEdgeBetween(leftPoint, thisPoint)
        if noWallInRight:
            self.addEdgeBetween(rightPoint, thisPoint)

        # For each choice it can take
        for choice in self.graph[thisPoint]:
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
                return
            choice = self.stack[-1]

        if choice == frontPoint:
            self.goForward(refresh)
        elif choice == leftPoint:
            self.goToLeft(refresh)
        elif choice == rightPoint:
            self.goToRight(refresh)
        else:
            self.goBackward(refresh)

    def goToCenter(self, refresh, img):
        """Second half of loop (going to center of maze)"""

        # Compute distance Grid and shortest path
        grid = self.bfs()
        path = self.shortestPath(grid)

        # For each node
        for node in path:
            # Get points near it (front one is not needed)
            backPoint = self.tileInTheDirection((self.direction + 2) % 4)
            rightPoint = self.tileInTheDirection((self.direction + 1) % 4)
            leftPoint = self. tileInTheDirection((self.direction - 1) % 4)

            # Go to the next node in path
            if node == rightPoint:
                self.turnRight(refresh)
            elif node == leftPoint:
                self.turnLeft(refresh)
            elif node == backPoint:
                self.turnLeft(refresh)
                self.turnLeft(refresh)
            self.goForward(refresh)

        # Wait for Esc press and Exit
        while not self.userPressedExit(10):
            pass
        return STOP_SIMULATION

    # --------------------------------------------------------------
    # GRAPH THEORY ALGORITHMS --------------------------------------
    # --------------------------------------------------------------

    def bfs(self):
        """USe breadth first seach algorithm to find shotest distance from center point"""
        distancesGraph = {}

        # BFS from middle to the robot start point
        start = self.center
        search = (0, 0)

        distancesGraph[start] = 0
        queue = collections.deque([start])

        while True:
            # Get next node
            node = queue.pop()

            if node == search:
                # If this is the one we need, seach no more
                break

            for neighbor in self.graph[node]:
                if neighbor not in distancesGraph:
                    # If distance to neighbor hasn't been calculated, calculate it
                    queue.appendleft(neighbor)
                    distancesGraph[neighbor] = distancesGraph[node] + 1

        return distancesGraph

    def shortestPath(self, distanceGraph):
        """USe dynamic programming to to find shotest distance path"""
        # Start from start pos
        start = self.start
        path = []

        node = start
        while True:
            # Default min point is point itself
            minNode = node
            minVal = distanceGraph[node]
            # Find a neighbor that has lowest distance from center
            for neighbor in self.graph[node]:
                # If neighbor is not mapped in distanceGraph then it is a memeber that is far away
                if neighbor not in distanceGraph:
                    continue
                val = distanceGraph[neighbor]
                if minVal > val:
                    minVal = val
                    minNode = neighbor
            node = minNode
            # Add node to path
            path.append(node)

            if minVal == 0:
                # Center found
                break
        return path


settingsImagePath = "Maze.png"
settingsStartX = 1
settingsStartY = 1
settingsFaceDirection = Direction.EAST
settingsGridSideSquares = 14
settingsSrcClass = DeapthFirstSearch
