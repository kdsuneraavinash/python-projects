import cv2
import numpy

import robot
from datatypes import Direction


def open_image(filename):
    """"Opens an image in disk"""
    img = cv2.imread(filename, cv2.IMREAD_COLOR)
    return img


def refresh_screen(img: numpy.array, bot: robot.Robot, edit_function=None):
    """Refreshes Screen. Adds bot position."""

    copy = numpy.copy(img)
    if edit_function is not None:
        copy = edit_function(copy)
    bot_added = draw_robot(bot, copy)
    cv2.imshow('maze-solving-bot-simulator', bot_added)


def draw_robot(bot: robot.Robot, img: numpy.array):
    """Draws a robot in the image"""

    middle = bot._center_point()

    rect_start = middle - bot.side * 0.3
    rect_end = middle + bot.side * 0.3

    circle_radius = bot.side * 0.2
    side25p = bot.side * 0.25
    if bot._direction == Direction.EAST:
        circle_center = middle + (side25p, 0)
    elif bot._direction == Direction.WEST:
        circle_center = middle + (-side25p, 0)
    elif bot._direction == Direction.NORTH:
        circle_center = middle + (0, -side25p)
    elif bot._direction == Direction.SOUTH:
        circle_center = middle + (0, side25p)
    else:
        # This never happens
        circle_center = middle

    color_black = (0, 0, 0)
    color_orange = (23, 74, 230)

    cv2.rectangle(img, tuple(rect_start), tuple(rect_end), color_orange, cv2.FILLED)
    cv2.rectangle(img, tuple(rect_start), tuple(rect_end), color_black, 1)

    cv2.circle(img, tuple(circle_center), int(circle_radius), bot._ball_color, cv2.FILLED)
    cv2.circle(img, tuple(circle_center), int(circle_radius), color_black, 1)

    return img


def apply_vision_filter(img):
    """Apply a filtered image to use for sensor functionality"""

    greyscale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.medianBlur(greyscale, 5)
    threshholded = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 5, 3)
    kernel = numpy.ones((3, 3), numpy.uint8)
    dilated = cv2.dilate(threshholded, kernel, iterations=1)
    eroded = cv2.erode(dilated, kernel, iterations=1)
    return eroded


def apply_ground_filter(img):
    """ Apply a ground image to use for sensor functionality. Currently tuned for [255,242,0] (yellow)"""

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_yellow = numpy.array([0, 200, 0])
    upper_yellow = numpy.array([100, 255, 255])
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    return mask
