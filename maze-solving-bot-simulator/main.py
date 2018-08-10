import cv2
import numpy as np
from vehicle import Vehicle
from direction import Direction
from point import Point


def main():
        # Open Image File
    img = cv2.imread('Maze.png', 1)

    greyscale = cv2.cvtColor(np.copy(img), cv2.COLOR_BGR2GRAY)
    blurred = cv2.medianBlur(greyscale, 5)
    threshholded = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
    kernel = np.ones((5, 5), np.uint8)
    dilated = cv2.dilate(threshholded, kernel, iterations=1)
    final = cv2.erode(dilated, kernel, iterations=1)

    robot = Vehicle(1, 1, Direction.EAST, final)
    robot.setBoundaries(1, 1, 14, 14)

    # Set False to toggle visited crosses
    DRAW_VISITED = False

    while True:
        edited = np.copy(img)
        edited = robot.drawVehicle(edited)
        robot.traverse()

        if DRAW_VISITED:
            for i in range(1, 15):
                for j in range(1, 15):
                    if (i, j) in robot.visited:
                        a = Point(robot.side * (i-1), robot.side * (j-1))
                        b = Point(robot.side * i, robot.side * j)
                        cv2.line(edited, tuple(a), tuple(b), (0, 0, 0), 1)
                        cv2.line(edited, (b.x, a.y), (a.x, b.y), (0, 0, 0), 1)

        cv2.imshow('image', edited)

        pressedKey = cv2.waitKey(100)
        if pressedKey == 27:
            cv2.destroyAllWindows()
            break
        # elif pressedKey == ord('w'):
        #     robot.goForward()
        # elif pressedKey == ord('a'):
        #     turned = True
        #     robot.turnCounterClockwise()
        # elif pressedKey == ord('d'):
        #     turned = True
        #     robot.turnClockwise()


if __name__ == '__main__':
    main()
