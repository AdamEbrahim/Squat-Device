import cv2
import os

file_path = None
success = True

while success:
    success, frame = cv2.imread