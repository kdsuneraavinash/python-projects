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
    CROSS_OUT_VISITED = False
    DRAW_DISTANCES_FROM_CENTER = False
    DRAW_SHORTEST_PATH = True
    GO_TO_CENTER = True

    def __init__(self, bot):
        self.bot = bot

    def __right(self, refresh):
        # print("Right")
        self.bot.turnRight()
        refresh()
        self.bot.goForward()

    def __forward(self, refresh):
        # print("Forward")
        self.bot.goForward()

    def __left(self, refresh):
        # print("Left")
        self.bot.turnLeft()
        refresh()
        self.bot.goForward()

    def __back(self, refresh):
        # print("Back")
        self.bot.turnRight()
        refresh()
        self.bot.turnRight()
        refresh()
        self.bot.goForward()

    def __directionPoint(self, direction):
        dirX = self.bot.x
        dirY = self.bot.y
        if (direction == Direction.EAST):
            dirX += 1
        elif (direction == Direction.WEST):
            dirX -= 1
        elif (direction == Direction.NORTH):
            dirY -= 1
        elif (direction == Direction.SOUTH):
            dirY += 1
        return (dirX, dirY)

    def __addToGraph(self, a, b):
        if a not in self.graph:
            self.graph[a] = set()
        if b not in self.graph:
            self.graph[b] = set()
        self.graph[a].add(b)
        self.graph[b].add(a)

    def __crossOutVisitedPoints(self, img):
        for point in self.visited:
            a, b = point
            c, d = a - 1, b - 1
            a *= self.bot.side
            b *= self.bot.side
            c *= self.bot.side
            d *= self.bot.side
            cv2.line(img, (a, b), (c, d), (0, 0, 0), 1)
            cv2.line(img, (c, b), (a, d), (0, 0, 0), 1)

    def setup(self):
        self.visited = set()
        self.graph = {}
        self.stack = [(settingsStartX, settingsStartY)]

    def loop(self, img):
        def refresh():
            if self.CROSS_OUT_VISITED:
                self.__crossOutVisitedPoints(img)
            utils.refreshScreen(img, self.bot)
            cv2.waitKey(kWaitDuration)

        pressedKey = cv2.waitKey(kWaitDuration)

        if not self.stack:
            grid = bfs(self.graph)

            if self.DRAW_DISTANCES_FROM_CENTER:
                for i in range(settingsGridSideSquares):
                    for j in range(settingsGridSideSquares):
                        a = i*self.bot.side + 1*self.bot.side//4
                        b = j*self.bot.side + 3*self.bot.side//4
                        cv2.putText(
                            img, str(grid[i][j]), (a, b), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 1, cv2.LINE_AA)

            path = shortestPath(grid, self.graph)

            if self.DRAW_SHORTEST_PATH:

                def getMiddle(x, y):
                    return (x-1) * self.bot.side + self.bot.side//2, (y-1) * self.bot.side + self.bot.side//2

                c, d = getMiddle(settingsStartX, settingsStartY)
                for node in path:
                    a, b = c, d
                    c, d = getMiddle(node[0], node[1])
                    cv2.line(img, (a, b), (c, d), (0, 0, 255), 5)

            if self.GO_TO_CENTER:
                for node in path:
                    frontPoint = self.__directionPoint(self.bot.direction)
                    rightPoint = self.__directionPoint((self.bot.direction + 1) % 4)
                    leftPoint = self. __directionPoint((self.bot.direction - 1) % 4)
                    if node == rightPoint:
                        self.bot.turnRight()
                        refresh()
                    if node == leftPoint:
                        self.bot.turnLeft()
                        refresh()
                    self.__forward(refresh)
                    refresh()
                cv2.waitKey(0)
                cv2.destroyAllWindows()
                return STOP_SIMULATION

            if cv2.waitKey(kWaitDuration) == 27:
                cv2.destroyAllWindows()
                return STOP_SIMULATION
            return

        if pressedKey == 27:
            cv2.destroyAllWindows()
            return STOP_SIMULATION

        frontObstacleFree = self.bot.frontSensor() >= self.bot.side
        leftObstacleFree = self.bot.leftSensor() >= self.bot.side
        rightObstacleFree = self.bot.rightSensor() >= self.bot.side

        # Get current and neighboring points
        thisPoint = self.stack[-1]
        frontPoint = self.__directionPoint(self.bot.direction)
        rightPoint = self.__directionPoint((self.bot.direction + 1) % 4)
        leftPoint = self. __directionPoint((self.bot.direction - 1) % 4)

        # mark this point as discovered
        self.visited.add(thisPoint)

        # Record all possible turns and ad to the graph
        if frontObstacleFree:
            self.__addToGraph(frontPoint, thisPoint)
        if leftObstacleFree:
            self.__addToGraph(leftPoint, thisPoint)
        if rightObstacleFree:
            self.__addToGraph(rightPoint, thisPoint)

        for choice in self.graph[thisPoint]:
            # If found at least un discovered node, travel in it
            if choice not in self.visited:
                self.stack.append(choice)
                break
        else:
            # No undiscovered nodes near robot
            # Start to backtrack
            self.stack.pop()
            if not self.stack:
                # All done
                return
            choice = self.stack[-1]

        if choice == frontPoint:
            self.__forward(refresh)
        elif choice == leftPoint:
            self.__left(refresh)
        elif choice == rightPoint:
            self.__right(refresh)
        else:
            self.__back(refresh)


def bfs(graph):
    distanceGrid = [
        [float("inf")] * settingsGridSideSquares for _ in range(settingsGridSideSquares)]
    start = (settingsGridSideSquares//2 + 1, settingsGridSideSquares//2 + 1)
    search = (settingsStartX, settingsStartY)

    distanceGrid[start[0]-1][start[0]-1] = 0
    visited = set()
    queue = collections.deque([start])

    while True:
        node = queue.pop()
        visited.add(node)
        a, b = node
        a, b = a-1, b-1

        if node == search:
            break

        neighbors = graph[node]
        for neighbor in neighbors:
            if neighbor not in visited:
                x, y = neighbor
                x, y = x-1, y-1
                queue.appendleft(neighbor)
                distanceGrid[x][y] = distanceGrid[a][b] + 1

    return distanceGrid


def shortestPath(distanceGrid, graph):
    start = (settingsStartX, settingsStartY)
    path = []

    def getDistance(x): return distanceGrid[x[0] - 1][x[1] - 1]

    node = start
    nodeVal = getDistance(start)
    while nodeVal != 0:
        neighbors = graph[node]
        minNode = node
        minVal = getDistance(node)
        for neighbor in neighbors:
            val = getDistance(neighbor)
            if minVal > val:
                minVal = val
                minNode = neighbor
        node = minNode
        nodeVal = minVal
        path.append(node)
    return path


settingsImagePath = "Maze.png"
settingsStartX = 14
settingsStartY = 14
settingsFaceDirection = Direction.EAST
settingsGridSideSquares = 14
settingsSrcClass = DFS
