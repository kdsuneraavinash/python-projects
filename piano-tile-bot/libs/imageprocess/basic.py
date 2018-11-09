import cv2


def convert_image(original_img, source_format, destination_format):
    """
    Change image color format given source color (RGB, BGR) and
    destination_format:destination color (RGB, HSV, GRAY)
    """
    key = (source_format.upper(), destination_format.upper())
    converting_codes = {
        ("RGB", "GRAY"): cv2.COLOR_RGB2GRAY,
        ("RGB", "HSV"): cv2.COLOR_RGB2HSV,
        ("BGR", "RGB"): cv2.COLOR_BGR2RGB
    }

    code = converting_codes[key]
    return cv2.cvtColor(original_img, code)


def resize(original_img, size):
    """
    Resize image
    """
    return cv2.resize(original_img, size)


def overlay_images(image1, image2, image1_opaque):
    """
    Overlay 2 images
    First image opaque must be ( value between 0 and 1)
    Other will be 1 - opaque of image 1
    """
    return cv2.weightedAdd(image1, image1_opaque, image2, 1 - image1_opaque)


def load_image(path, mode=-1):
    """
    Loads a image file.
    mode means how to load that image.
    -1 = unchanged, 0 = black and white, 1 = coloured(RGB)
    """
    return cv2.imread(path, mode)
