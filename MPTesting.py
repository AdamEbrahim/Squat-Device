import numpy as np
import math as math
import mediapipe as mp
import cv2

cam = cv2.VideoCapture(0)
windowName = "Camera View"
cv2.namedWindow(windowName, cv2.WINDOW_NORMAL)

drawLimbs = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_holistic = mp.solutions.holistic
model = mp_holistic.Holistic(min_detection_confidence=0.5,
    min_tracking_confidence=0.5)


while cv2.waitKey(1) != 27:
    has_frame, frame = cam.read()
    if has_frame != True:
        break

    frame.flags.writeable = False
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = model.process(frame)


    frame.flags.writeable = True
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    drawLimbs.draw_landmarks(
        frame,
        results.face_landmarks,
        mp_holistic.FACEMESH_CONTOURS,
        landmark_drawing_spec=None,
        connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_contours_style()
    )
    drawLimbs.draw_landmarks(
        frame,
        results.pose_landmarks,
        mp_holistic.POSE_CONNECTIONS,
        landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
    )


    cv2.imshow(windowName, cv2.flip(frame, 1))





cam.release()
cv2.destroyWindow(windowName)

