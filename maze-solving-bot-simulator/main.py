import cv2
import numpy as np
from datatypes import Point, Direction
import utils
import robot
import bot_scripts


def main():
    # Open Image File
    img = cv2.imread('Maze.png', 1)
    threshholded = utils.applyVisionFilter(img)
    bot = robot.Robot(1, 1, Direction.EAST, threshholded)

    src = bot_scripts.UserKeyRobot(bot)

    src.setup()
    while True:
        edited = np.copy(img)
        edited = utils.drawRobot(bot, edited)
        cv2.imshow('image', edited)
        ret = src.loop()
        if ret == bot_scripts.STOP_SIMULATION:
            break


if __name__ == '__main__':
    main()
