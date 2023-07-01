#--FUNCTIONS FOR STUFF DISPLAYED ON SCREEN BY OPENCV--#
from Utils.config import squat_vars

import cv2
import time

#function to display correct and incorrect rep counters
def displayCounters(frame):
    cv2.putText(frame, "Complete reps: " + str(squat_vars.repCounter), (900, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (223, 244, 16), 6, cv2.LINE_AA)
    cv2.putText(frame, "Incomplete reps: " + str(squat_vars.incompleteCounter), (900, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (223, 244, 16), 6, cv2.LINE_AA)

#function to display mediapipe pose estimation limbs
def showLimbs(frame, results):
    squat_vars.drawLimbs.draw_landmarks(
        frame,
        results.face_landmarks,
        squat_vars.mp_holistic.FACEMESH_CONTOURS,
        landmark_drawing_spec=None,
        #connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_contours_style()
    )
    squat_vars.drawLimbs.draw_landmarks(
        frame,
        results.pose_landmarks,
        squat_vars.mp_holistic.POSE_CONNECTIONS,
        #landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
    )

def checkSetupPassed():
    if time.time() - squat_vars.programStartTime >= squat_vars.setupTime:
        squat_vars.hasPassedSetupTime = True
        print("squat analysis started")