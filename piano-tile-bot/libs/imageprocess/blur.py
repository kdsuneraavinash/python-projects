import cv2
import numpy as np


def gaussian_blur(original_image, kernel_size=(15, 15), sigma_x=0):
    """
    Gaussian Blur.
    """
    return cv2.GaussianBlur(original_image, kernel_size, sigma_x)


def median_blur(original_image, kernel_size=15):
    """
    Median Blur.
    Recommended by sentdex
    """
    return cv2.medianBlur(original_image, kernel_size)


def average_blur(original_image, kernel_size=15):
    """
    Average blur.
    Least effect blur
    """
    kernel = np.ones((kernel_size, kernel_size), np.float32) / (kernel_size ** 2)
    return cv2.filter2D(original_image, -1, kernel)


def bilateral_blur(original_image, filter_threshold=5, sigma_color=100, sigma_space=100):
    """
    Bilateral Blur. Slow.
    filter_threshold reduces noise(big values will slow down, recommended 5)
    If sigma values are bigger than 150, gives cartoon look.
    """
    return cv2.bilateralFilter(original_image, filter_threshold, sigma_color, sigma_space)
