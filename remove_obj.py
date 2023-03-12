import cv2
import os


files = os.listdir("assets")
templs = {}
for file in files:
    path = "assets/"+file
    img = cv2.imread(path)
    templs[file.split(".")[0]] = img





