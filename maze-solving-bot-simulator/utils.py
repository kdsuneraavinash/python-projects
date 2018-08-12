import cv2
import numpy as np
from datatypes import Direction, UndefinedDirectionError


def openImage(filename):
    img = cv2.imread(filename, cv2.IMREAD_COLOR)
    return img


def refreshScreen(img, bot, function=None):
    """
    Refreshes Screen. Adds bot position.

    Arguments:
        img -- Image to edit
        bot -- Bot to draw

    Keyword Arguments:
        function -- Function which takes img as parameter and returns edited image (default: None)
    """

    copy = np.copy(img)
    if function is not None:
        try:
            copy = function(copy)
        except TypeError:
            print("refreshScreen :: Pass a Function(img) as 'function' :: Skipped")
    botAdded = drawRobot(bot, copy)
    cv2.imshow('maze-solving-bot-simulator', botAdded)


def drawRobot(robot, img):
    """
    Draws a robot in the image

    Arguments:
        robot -- Robot instance to draw
        img -- cv2 image denoting original image. This image will be modified

    Raises:
        UndefinedDirectionError -- when direction is not a value which is defined

    Returns:
        image -- Modified image. Note that the original image will be modified and returned
    """

    middle = robot._Robot__centerPoint()

    rectStart = middle - robot.side * 0.3
    rectEnd = middle + robot.side * 0.3

    circleRadius = robot.side * 0.2
    side25p = robot.side * 0.25
    if (robot._direction == Direction.EAST):
        circleCenter = middle + (side25p, 0)
    elif (robot._direction == Direction.WEST):
        circleCenter = middle + (-side25p, 0)
    elif (robot._direction == Direction.NORTH):
        circleCenter = middle + (0, -side25p)
    elif (robot._direction == Direction.SOUTH):
        circleCenter = middle + (0, side25p)
    else:
        raise UndefinedDirectionError()

    colorBlack = (0, 0, 0)
    colorOrange = (23, 74, 230)

    cv2.rectangle(img, tuple(rectStart), tuple(
        rectEnd), colorOrange, cv2.FILLED)
    cv2.rectangle(img, tuple(rectStart), tuple(rectEnd), colorBlack, 1)

    cv2.circle(img, tuple(circleCenter), int(
        circleRadius), colorBlack, cv2.FILLED)

    return img


def applyVisionFilter(img):
    """
    Apply a filtered image to use for sensor functionality

    Arguments:
        img -- original image

    Returns:
        copy of original image after adding the filter
    """

    greyscale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.medianBlur(greyscale, 5)
    threshholded = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 5, 3)
    kernel = np.ones((3, 3), np.uint8)
    dilated = cv2.dilate(threshholded, kernel, iterations=1)
    eroded = cv2.erode(dilated, kernel, iterations=1)
    return eroded


def applyGroundFilter(img):
    """
    Apply a groumd image to use for sensor functionality
    Currently tuned for [255,242,0] (yellow)

    Arguments:
        img -- original image

    Returns:
        mask after adding the filter (Yellow colored will be 255)
    """

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_yellow = np.array([0,200,0])
    upper_yellow = np.array([100,255,255])
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    return mask
