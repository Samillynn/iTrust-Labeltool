import cv2
import numpy as np

img = cv2.resize(cv2.imread('assets/screen_shot.jpg', 0), (0, 0), fx=0.8, fy=0.8)
template = cv2.resize(cv2.imread('assets/big tank.png', 0), (0, 0), fx=0.8, fy=0.8)
h, w = template.shape

method = cv2.TM_CCOEFF_NORMED
result = cv2.matchTemplate(img, template, method)
threshold = 0.9

location = np.where(result > threshold)
location = list(zip(*location[::-1]))

unique_location = []
for loc in location:
    unique = True
    for loc2 in unique_location:
        if abs(loc[0] - loc2[0]) + abs(loc[1] - loc2[1]) < min(h, w):
            unique = False
    if unique:
        unique_location.append(loc)

for pt in unique_location:  # -1 to swap the values as we assign x and y coordinate to draw the rectangle.
    cv2.rectangle(img, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)  # Red rectangles with thickness 2.

# bottom_right = (location[0] + w, location[1] + h)
# cv2.rectangle(img2, location, bottom_right, 255, 5)
cv2.imshow('Match', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
