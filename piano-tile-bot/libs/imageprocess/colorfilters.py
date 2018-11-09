import cv2
import numpy as np


def basic_threshold(original_image, threshold=12, max_val=255):
    """
    Add threshold to coloured/ gray scale image.
    """
    _, filtered_image = cv2.threshold(original_image, threshold, max_val, cv2.THRESH_BINARY)
    return filtered_image


def adaptive_threshold(gray_image, max_val=255, threshold1=115, threshold2=1):
    """
    Add adaptive threshold to gray scale image.
    Great at filtering.
    """
    filtered_image = cv2.adaptiveThreshold(gray_image, max_val, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,
                                           threshold1, threshold2)
    return filtered_image


def otsu_threshold(gray_image, threshold=125, max_val=255):
    """
    Add otsu threshold to gray scale image.
    """
    _, filtered_image = cv2.threshold(gray_image, threshold, max_val, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return filtered_image


def region_of_interest(original_img, vertices):
    """
    Get only a region of interest of an image
    """
    mask = np.zeros_like(original_img)
    cv2.fillPoly(mask, vertices, 255)
    masked = cv2.bitwise_and(original_img, mask)
    return masked


def get_mask(original_img, high_hsv, low_hsv):
    """
    Filter only one color and return filter mask
    Returns filtered mask (Only 255 and 0 pixels) (black and white)
    """
    filtered_mask = cv2.inRange(original_img, low_hsv, high_hsv)
    return filtered_mask


def apply_mask(image, mask, mask_operator="AND"):
    """
    Apply a mask to an image by given operator(AND / OR / XOR)
    """
    masking_methods = {"AND": cv2.bitwise_and,
                       "OR": cv2.bitwise_or,
                       "XOR": cv2.bitwise_xor}
    mask_method = masking_methods[mask_operator.upper()]

    return mask_method(image, mask)


def erode(mask, kernel_size=5):
    """
    Checks blocks of mask and replace block with all 1s iff all pixels are 1.
    So white pixels will reduce.
    """
    kernel = np.array((kernel_size, kernel_size), np.uint8)
    return cv2.erode(mask, kernel, iterations=1)


def dilate(mask, kernel_size=5):
    """
    Checks blocks of mask and replace block with at least one 1 by all 1s.
    So white pixels will increase.
    """
    kernel = np.array((kernel_size, kernel_size), np.uint8)
    return cv2.dilate(mask, kernel, iterations=1)


def remove_false_positives(mask, kernel_size=5):
    """
    Remove white pixels surrounded by black pixels
    """
    kernel = np.array((kernel_size, kernel_size), np.uint8)
    return cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)


def remove_false_negatives(mask, kernel_size=5):
    """
    Remove black pixels surrounded by white pixels
    """
    kernel = np.array((kernel_size, kernel_size), np.uint8)
    return cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
