import cv2
import numpy as np


def get_edges(original_img, threshold1=200, threshold2=300, image_converting_function=None):
    """
    Get edged image (algorithm used will be Canny algorithm)
    """
    if image_converting_function:
        original_img = image_converting_function(original_img)
    else:
        original_img = cv2.cvtColor(original_img, cv2.COLOR_RGB2GRAY)
    edge_image = cv2.Canny(original_img, threshold1=threshold1, threshold2=threshold2)
    return edge_image


def get_corners(original_img, n_points=100, quality=0.01, min_gap=10, image_converting_function=None):
    """
    Detect Corners.
    """
    if image_converting_function:
        original_img = image_converting_function(original_img)
    else:
        original_img = cv2.cvtColor(original_img, cv2.COLOR_RGB2GRAY)
    original_img = np.float32(original_img)
    corners = cv2.goodFeaturesToTrack(original_img, n_points, quality, min_gap)
    corners = np.array(corners, np.int0)
    return [corner.ravel() for corner in corners]


def get_hough_lines(edge_img, rho=1, theta=np.pi / 180, threshold=180,
                    min_line_length=50, max_line_gap=50):
    """
    Use edge image to add lines to the image using hough lines algorithm.
    Returns lines list in format [ [line1], [line2], [line3], ... ]
    """
    return cv2.HoughLinesP(edge_img, rho=rho, theta=theta, threshold=threshold, minLineLength=min_line_length,
                           maxLineGap=max_line_gap)


def template_matching(main_image, template_images, threshold=0.9, draw_boxes=False, draw_image=None, color=(0, 0, 0)):
    """
    Match a template image list with given image.
    Not much accurate if threshold is low.
    Does not detect from different angles
    """
    points = []
    for template in template_images:
        h, w = template.shape[-2:]
        res = cv2.matchTemplate(main_image, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= threshold)

        for pt in zip(*loc[::-1]):
            if draw_boxes:
                if draw_image is None:
                    draw_image = main_image
                cv2.rectangle(draw_image, pt, (pt[0] + w, pt[1] + h), color, 1)
            points.append(pt)
    return points


def foreground_extraction():
    # TODO : Write this Function. OpenCV 12 Tutorial
    return
