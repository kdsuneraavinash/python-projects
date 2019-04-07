import cv2
import numpy as np
import math
import ascii
import os


MAX_ERROR = 25
MIN_RADIUS = 150
MAX_RADIUS = 750
WINDOW_TITLE = 'Camera'

MAT_RED = (40, 40, 198)
MAT_YELLOW = (0, 234, 255)
MAT_L_BLUE = (244, 169, 3)
MAT_BLACK = (0, 0, 0)

TEXT_POSITION = (50, 100)


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


def detectCircle(preprocessedImage, colorImage):
    # Find contours in image
    _, contours, __ = cv2.findContours(preprocessedImage,
                                       cv2.RETR_TREE,
                                       cv2.CHAIN_APPROX_SIMPLE)

    # Get circles and filter out None values
    detectedCircles = map(getCircleFromContour, contours)
    detectedCircles = list(filter(lambda x: x is not None, detectedCircles))

    if len(detectedCircles) == 0:
        # No detected circles
        return None

    # Find the circle with smallest error
    detectedCircle = min(detectedCircles, key=lambda x: x.error)

    # Draw details
    # cv2.circle(colorImage, detectedCircle.center.toIntTuple(), 5, MAT_RED, -1)
    cv2.circle(colorImage, detectedCircle.center.toIntTuple(),
               int(detectedCircle.radius), MAT_RED, 3)
    # cv2.circle(colorImage, detectedCircle.center.toIntTuple(),
    #            10, MAT_L_BLUE, 3)

    return detectedCircle


def detectArrow(regionOfInterest):
    # Process region of interest
    processedROI = preprocessor(regionOfInterest)
    regionOfInterest = cv2.cvtColor(processedROI, cv2.COLOR_GRAY2RGBA)

    # Get all contours
    _, contours, __ = cv2.findContours(processedROI,
                                       cv2.RETR_TREE,
                                       cv2.CHAIN_APPROX_SIMPLE)

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
    w = 5
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


def process(colorImage):
    preprocessedImage = preprocessor(colorImage)
    detectedCircle = detectCircle(preprocessedImage, colorImage)

    if detectedCircle is None:
        cv2.putText(colorImage, "NO CIRCLE", TEXT_POSITION,
                    cv2.FONT_HERSHEY_COMPLEX, 1.0, MAT_BLACK)
        return colorImage, preprocessedImage

    r = cv2.boundingRect(detectedCircle.contour)
    regionOfInterest = colorImage[int(r[1]):int(r[1]+r[3]),
                                  int(r[0]):int(r[0]+r[2])]

    detectedArrow = detectArrow(regionOfInterest)

    if detectedArrow == None:
        cv2.putText(colorImage, "WRONG CIRCLE? - NO ARROW",
                    TEXT_POSITION, cv2.FONT_HERSHEY_COMPLEX,
                    1.0, MAT_BLACK)
        return colorImage, preprocessedImage

    contour = detectedArrow.contour
    print(contour.shape)
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

    cv2.circle(regionOfInterest, p.toIntTuple(), 2, MAT_YELLOW, 3);
    cv2.circle(regionOfInterest, q.toIntTuple(), 2, MAT_YELLOW, 3);
    cv2.circle(regionOfInterest, r.toIntTuple(), 2, MAT_YELLOW, 3);
    cv2.line(regionOfInterest, c.toIntTuple(), r.toIntTuple(), MAT_RED);
    cv2.circle(regionOfInterest, r.toIntTuple(), 5, MAT_RED, -1);

    cv2.putText(colorImage, str(angle), TEXT_POSITION,
                cv2.FONT_HERSHEY_COMPLEX, 1.0, MAT_YELLOW)

    return colorImage, preprocessedImage


cap = None
def getCameraFrame(source=0):
    '''Returns camera video frame from video source'''

    global cap

    if cap is None:
        cap = cv2.VideoCapture(source)

    ret = False
    stuck_counter = 0
    while not ret:
        ret, frame = cap.read()
        stuck_counter += 1

        if stuck_counter > 300:
            # Stuck for 300 frames
            return None

    return frame


def getPhotoFrame(file='snapshot.jpeg'):
    '''Returns a photo from file'''

    return cv2.imread(file, 1)


def main():
    '''Main Entry Point'''
    #cv2.namedWindow(WINDOW_TITLE, cv2.WINDOW_NORMAL)
    #cv2.resizeWindow(WINDOW_TITLE, 600, 430)

    # Create and resize window
    while True:
        frame = getPhotoFrame()

        if frame is None:
            # Frame lag - stop
            break

        frame, threshed = process(frame)
        art = ascii.frame_to_ascii_art(frame, 50, 0.5, False)
        art = '\n'.join(art)
        os.system('clear')
        print(art)
        

        #if cv2.waitKey(60) & 0xff == 27:
        #    # Esc press - stop
        #    break

    # cv2.destroyAllWindows()
    try:
        cap.release()
    except:
        pass


if __name__ == '__main__':
    main()
