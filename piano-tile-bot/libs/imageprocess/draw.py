import cv2


def lines(image, lines_list, color=(0, 0, 0), thickness=3):
    """
    draw lines on a image
    lines_list can be either [ [line1], [line2], .. ] or [line1, line2, ...]
    """
    if lines is not None:
        for each_line in lines_list:
            if len(each_line) == 1:
                each_line = each_line[0]
            x1, y1, x2, y2 = each_line
            cv2.line(image, (x1, y1), (x2, y2), color, thickness)
    return image


def line(image, p, q, color=(0, 0, 0), thickness=1):
    """
    Draw a line between P and Q.
    """
    cv2.line(image, p, q, color, thickness)
    return image


def circle(image, position, radius, color=(0, 0, 0), thickness=1):
    """
    Draw a circle.
    If thickness is -1 => filled circle.
    """
    cv2.circle(image, tuple(position), radius, color, thickness)
    return image


def rectangle(image, top_left, bottom_right, color=(0, 0, 0), thickness=1):
    """
    Draw a rectangle.
    If thickness is -1 => filled circle.
    """
    cv2.rectangle(image, top_left, bottom_right, color, thickness)
    return image


def text(image, message, position, font_size=1, color=(0, 0, 0), thickness=2):
    """
    Draw a text on a image.
    """
    position = tuple(position)
    cv2.putText(image, message, position, cv2.FONT_HERSHEY_SIMPLEX, font_size, color, thickness, cv2.LINE_AA)
    return image
