import cv2
import numpy as np

from graph.image import CoordinateTransfer
from graph.label import Rectangle


def remove_close_rectangles(rects, existent_rects, threshold):
    result = []
    for r in rects:
        too_close = False
        r = r.sorted()
        for r2 in existent_rects + result:
            r2 = r2.sorted()
            if abs(r.left - r2.left) + abs(r.bottom - r2.bottom) < threshold:
                too_close = True
        if not too_close:
            result.append(r)

    return result


Cv2Image = np.ndarray


def template_matching(image: Cv2Image, template: Cv2Image, method=None, threshold=None) -> list[Rectangle]:
    if method is None:
        method = cv2.TM_CCOEFF_NORMED
    if threshold is None:
        threshold = lambda x: x > 0.8

    h, w, _ = template.shape
    image_grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    template_grey = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    matrix = cv2.matchTemplate(image_grey, template_grey, method)
    matches = np.where(threshold(matrix))
    return [Rectangle(p, (p[0] + w, p[1] + h)) for p in list(zip(*matches[::-1]))]


def crop_matching(image: Cv2Image, crop_rect: Rectangle, method=None, threshold=None):
    left, top = crop_rect.top_left
    right, bottom = crop_rect.bottom_right
    template = image[bottom:top + 1, left:right + 1]
    matches = template_matching(image=image, template=template, method=method, threshold=threshold)
    return matches


def relative_coord_crop_matching(image: Cv2Image, crop_rect: Rectangle, coord: CoordinateTransfer, method=None,
                                 threshold=None):
    absolute_rect = Rectangle(coord.to_absolute(crop_rect.top_left), coord.to_absolute(crop_rect.bottom_right))
    absolute_matches = crop_matching(image=image, crop_rect=absolute_rect, method=method, threshold=threshold)
    return [Rectangle(coord.to_relative(m.top_left), coord.to_relative(m.bottom_right)) for m in absolute_matches]


if __name__ == '__main__':
    hmi = cv2.imread('assets/screen_shot.jpg')
    big_tank = cv2.imread('assets/big tank.png')

    h, w, _ = big_tank.shape
    hmi2 = hmi.copy()
    for rect in template_matching(hmi2, big_tank):
        cv2.rectangle(hmi2, rect.bottom_left, rect.top_right, (0, 0, 255), 2)  # Red rectangles with thickness 2.

    cv2.imshow('Match', hmi2)
    cv2.waitKey(0)

    hmi3 = hmi.copy()
    for rect in crop_matching(hmi3, Rectangle((125, 220), (200, 320))):
        cv2.rectangle(hmi3, rect.bottom_left, rect.top_right, (0, 0, 255), 2)  # Red rectangles with thickness 2.

    cv2.imshow('Crop Match', hmi3)
    cv2.waitKey(0)

    cv2.destroyAllWindows()
