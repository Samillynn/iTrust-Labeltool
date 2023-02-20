import time

# noinspection PyUnresolvedReferences,PyPep8Naming
import PySimpleGUI as sg
import cv2 as cv


def current_milli_time():
    return round(time.time() * 1000)


def preprocess(img):
    img = cv.resize(img, (600,800), interpolation=cv.INTER_CUBIC)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    blur = cv.GaussianBlur(gray, (1,1), 1)
    # blur = cv.bilateralFilter(gray, 3, 7, 7)

    kernel = cv.getStructuringElement(cv.MORPH_RECT, (1,1))
    dilate = cv.dilate(blur, kernel, iterations=1)  
    dilate = cv.erode(dilate, kernel, iterations=2)  
    # thresh = cv.threshold(dilate, 120, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)[1]

    # cv.imshow("result",dilate)
    # cv.waitKey(0)
    # cv.destroyAllWindows()
    
    return dilate


def align_center(coord: tuple, x_set:list, y_set:list):
    threshold = 0.004
    x = coord[0]
    y = coord[1]
    similar_x = False
    similar_y = False
    for x_r in x_set:
        if abs(x-x_r) < threshold:
            x = x_r
            break
    if not similar_x:
        x_set.append(x)
    for y_r in y_set:
        if abs(y-y_r) < threshold:
            y = y_r
            break
    if not similar_y:
        y_set.append(y)
    return (x,y)
    

