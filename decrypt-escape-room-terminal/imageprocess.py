import cv2
import math
import numpy as np

MAX_ERROR = 25
MIN_RADIUS = 150
MAX_RADIUS = 750


class DetectedCircle:
    def __init__(self, center, radius, error, contour):
        assert((center == None) or (type(center) is Point))

        self.center = center
        self.radius = radius
        self.error = error
        self.contour = contour.reshape((-1, 2))


class DetectedArrow:
    def __init__(self, center, boundingBox, distFromCircleCenter, contour):
        assert((center == None) or (type(center) is Point))

        self.center = center
        self.boundingBox = boundingBox
        self.distFromCircleCenter = distFromCircleCenter
        self.contour = contour.reshape((-1, 2))


class BoundRect:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def toTuple(self):
        return (self.x, self.y)

    def toIntTuple(self):
        return (int(self.x), int(self.y))


def preprocessor(colorImage):
    # Grey-scale image
    monoImage = cv2.cvtColor(colorImage, cv2.COLOR_RGBA2GRAY)

    # Blur image
    blurSize = (7, 7)
    blurredImage = cv2.GaussianBlur(monoImage, blurSize, 2, 2)

    # Threshold image
    _, threshedImage = cv2.threshold(blurredImage, 0, 255, cv2.THRESH_OTSU)
    #_, threshedImage = cv2.threshold(
    #    blurredImage, 100, 255, cv2.THRESH_BINARY_INV)

    # Apply morphological transformations
    morphKernel = np.ones((3, 3))
    transformedImage = cv2.morphologyEx(threshedImage, cv2.MORPH_OPEN,
                                        morphKernel)
    transformedImage = cv2.morphologyEx(transformedImage, cv2.MORPH_CLOSE,
                                        morphKernel)

    return transformedImage


def getCircleFromContour(contour):
    area = cv2.contourArea(contour)

    # Too small
    if area < 50:
        return None

    # Approximate radius using area and perimeter
    arcLength = cv2.arcLength(contour, True)
    radiusByArea = math.sqrt(area / (math.pi))
    radiusByLength = arcLength / (2*math.pi)
    approxRadius = (radiusByArea + radiusByLength)/2
    error = abs(radiusByLength - radiusByArea)

    # Filter out
    if approxRadius < MIN_RADIUS or\
            approxRadius > MAX_RADIUS or\
            error > MAX_ERROR:
        return None

    # Get center point
    mu = cv2.moments(contour)
    center = Point(mu['m10'] / mu['m00'], mu['m01'] / mu['m00'])

    # Add Circle
    detectedCircle = DetectedCircle(center, approxRadius, error, contour)
    return detectedCircle


def getArrowFromContour(contour, regionCenter):
    area = cv2.contourArea(contour)

    # Too small
    if area < 50:
        return None

    mu = cv2.moments(contour)

    arrowCenter = Point(mu['m10'] / mu['m00'], mu['m01']/mu['m00'])

    # Get distance of contour to region center, must be positive
    # contour must be in the middle of region

    distanceFromCenterRegion = cv2.pointPolygonTest(
        contour, regionCenter, True)

    if 0 <= distanceFromCenterRegion < 100:
        arrowBounds = BoundRect(*cv2.boundingRect(contour))
        detectedArrow = DetectedArrow(
            arrowCenter, arrowBounds, distanceFromCenterRegion, contour)
        return detectedArrow
    else:
        return None

def getContours(img):
    v = cv2.findContours(img,
                        cv2.RETR_TREE,
                        cv2.CHAIN_APPROX_SIMPLE)
    try:
        _, contours, __ = v
    except:
        contours, _ = v
    return contours

def detectCircle(preprocessedImage):
    # Find contours in image
    contours = getContours(preprocessedImage)

    # Get circles and filter out None values
    detectedCircles = map(getCircleFromContour, contours)
    detectedCircles = list(filter(lambda x: x is not None, detectedCircles))

    if len(detectedCircles) == 0:
        # No detected circles
        return None

    # Find the circle with smallest error
    detectedCircle = min(detectedCircles, key=lambda x: x.error)

    return detectedCircle


def detectArrow(regionOfInterest):
    # Process region of interest
    processedROI = preprocessor(regionOfInterest)
    regionOfInterest = cv2.cvtColor(processedROI, cv2.COLOR_GRAY2RGBA)

    # Get all contours
    contours = getContours(processedROI)

    regionCenter = (regionOfInterest.shape[0]//2, regionOfInterest.shape[1]//2)

    # Get arrows and filter out None values
    detectedArrows = map(
        lambda x: getArrowFromContour(x, regionCenter), contours)
    detectedArrows = list(filter(lambda x: x is not None, detectedArrows))

    if len(detectedArrows) == 0:
        # No detected arrows
        return None

    detectedArrow = min(detectedArrows, key=lambda x: x.distFromCircleCenter)

    return detectedArrow


def countBlackPoints(contour, a):
    w = 20
    allMidPoints = [(int(a.y + i), int(a.y + j))
                    for j in range(-w, w)
                    for i in range(-w, w)]

    polygonTested = map(lambda x: cv2.pointPolygonTest(
        contour, x, False), allMidPoints)
    # 1 means inside contour
    pointsInsideContour = list(polygonTested).count(1)
    return pointsInsideContour


def findCorrectCombination(p, q, r, arrowContour):
    combinations = [
        [p, q, r],
        [p, r, q],
        [q, r, p]
    ]

    correctCombination = None
    leastBlackPoints = float("inf")
    for combination in combinations:
        cx = (combination[0].x + combination[1].x) / 2
        cy = (combination[0].y + combination[1].y) / 2

        c = Point(cx, cy)
        blackPoints = countBlackPoints(arrowContour, c)
        if blackPoints < leastBlackPoints:
            leastBlackPoints = blackPoints
            correctCombination = combination

    return correctCombination

message_from_image_processor = ""

def process(colorImage):
    global message_from_image_processor
    message_from_image_processor = ""
    
    preprocessedImage = preprocessor(colorImage)
    detectedCircle = detectCircle(preprocessedImage)

    if detectedCircle is None:
        message_from_image_processor = "nothing detected"
        return colorImage, preprocessedImage, float("inf")

    r = cv2.boundingRect(detectedCircle.contour)
    regionOfInterest = colorImage[int(r[1]):int(r[1]+r[3]),
                                  int(r[0]):int(r[0]+r[2])]

    detectedArrow = detectArrow(regionOfInterest)

    if detectedArrow == None:
        message_from_image_processor = "no middle content detected"
        return colorImage, preprocessedImage, float("inf")

    contour = detectedArrow.contour
    # Find bottom most point and top most points
    minPoint = min(contour, key=lambda a: a[1])
    maxPoint = max(contour, key=lambda a: a[1])

    p = Point(*minPoint)
    q = Point(*maxPoint)

    # Find the furthest point from p and q by finding the point r which maximizes
    # the area of the triangle pqr
    def areaOfTriangle(point):
        return 0.5 * abs((p.x - point[0]) * (q.y - p.y) - (p.x - q.x) * (point[1] - p.y))
        
    r = Point(*max(contour, key=areaOfTriangle))

    p, q, r = findCorrectCombination(p, q, r, detectedArrow.contour)
    
    cx = (p.x + q.x) / 2
    cy = (p.y + q.y) / 2
    c = Point(cx, cy)

    if c.y == r.y:
        angle = -90.0
    else:
        angle = math.floor(math.degrees(math.atan((r.x - c.x) / (r.y - c.y))))

    if c.y < r.y:
        if c.x < r.x:
            angle = -180 + angle
        else:
            angle = 180 + angle

    if c.y > r.y:
        if c.x > r.x:
            angle = 90-angle
        else:
            angle = 90-angle
    else:
        if c.x > r.x:
            angle = 90-angle
        else:
            angle = 270 + angle

    message_from_image_processor = "detected angle: {}".format(angle)

    return colorImage, preprocessedImage, angle
