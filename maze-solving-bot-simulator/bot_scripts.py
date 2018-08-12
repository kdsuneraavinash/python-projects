"""
Define user script here.
All userscripts must,
    - include a setup() and loop(img) function
    - include a __init__() method which takes 'bot' parameter
    - Should NOT include any methods which affects the value of bot in __init__()
    - loop must accept one variable as img, but try not to change img value. If you change it change it in-place. Can use img to tasks such as refreshing window

- Setup will run only once at the simulation initialization
- Loop will run each time screen is updated(by default)
- You can force screen refresh by util.refreshScreen(), however note that additional loop() functions will not run at these forced refreshes
- If loop() returns STOP_SIMULATION value, simulation will stop.
- Call cv2.destroyAllWindows() to close current window. However if not STOP_SIMULATION is issued, new refresh will cause a new window to load.
- Use cv2.waitKey(0) to wait for a KeyPress

Set these global varible values to set bot settings. Place settings at the end of file.
    - settingsImagePath : Image path of maze
    - settingsStartX, settingsStartY : Start position of bot
    - settingsFaceDirection : Direction bot is facing
    - settingsGridSideSquares : Squares per each side in maze grid
    - settingsSrcClass : Default class to load as Src
"""
import cv2
from datatypes import Direction
import utils
import collections

STOP_SIMULATION = 0x435

kWaitDuration = 200


class DFS:

    def __init__(self, bot):
        self.bot = bot

    # --------------------------------------------------------------
    # ROBOT MOVEMENT -----------------------------------------------
    # --------------------------------------------------------------

    def turnRight(self,  refresh):
        """Turn the bot 90' right"""
        self.direction += 1
        self.direction %= 4
        self.bot.turnRight()
        refresh()

    def turnLeft(self,  refresh):
        """Turn the bot 90' right"""
        self.direction -= 1
        self.direction %= 4
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

    # --------------------------------------------------------------
    # HELPER FUNCTIONS ---------------------------------------------
    # --------------------------------------------------------------

    def tileInTheDirection(self, direction):
        """ Get the coordinates if the tile in the 'direction'"""
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

    def addEdgeBetween(self, a, b):
        """Adds an edge between A and B"""
        if a not in self.graph:
            self.graph[a] = set()
        if b not in self.graph:
            self.graph[b] = set()
        self.graph[a].add(b)
        self.graph[b].add(a)

    def refreshScreen(self, img):
        """Refreshes Screen"""
        utils.refreshScreen(img, self.bot)
        cv2.waitKey(kWaitDuration)

    # --------------------------------------------------------------
    # RUNNING ENTRY POINTS -----------------------------------------
    # --------------------------------------------------------------

    def setup(self):
        """SETUP function"""
        self.visited = set()  # variable to record visited nodes
        self.graph = {}  # graph
        self.stack = [(settingsStartX, settingsStartY)]  # Stack to DFS

        # Have SOME initial values, doesn't matter what the values are
        self.x = settingsStartX
        self.y = settingsStartY
        self.direction = settingsFaceDirection

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
        """Second half of loop (discovering maze)"""

        # Wait and get pressed key (if key is pressed)
        pressedKey = cv2.waitKey(kWaitDuration)
        # If ESC is pressed Exit
        if pressedKey == 27:
            cv2.destroyAllWindows()
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
            backPoint = self.tileInTheDirection((self.bot.direction + 2) % 4)
            rightPoint = self.tileInTheDirection((self.bot.direction + 1) % 4)
            leftPoint = self. tileInTheDirection((self.bot.direction - 1) % 4)

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
        while cv2.waitKey(kWaitDuration) != 27:
            pass
        cv2.destroyAllWindows()
        return STOP_SIMULATION

    # --------------------------------------------------------------
    # GRAPH THEORY ALGORITHMS --------------------------------------
    # --------------------------------------------------------------

    def bfs(self):
        """USe breadth first seach algorithm to find shotest distance from center point"""
        distancesGraph = {}

        # BFS from middle to the robot start point
        start = (settingsGridSideSquares//2 + 1,
                 settingsGridSideSquares//2 + 1)
        search = (settingsStartX, settingsStartY)

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
        start = (settingsStartX, settingsStartY)
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
settingsStartX = 14
settingsStartY = 14
settingsFaceDirection = Direction.EAST
settingsGridSideSquares = 14
settingsSrcClass = DFS
