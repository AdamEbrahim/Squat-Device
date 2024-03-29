import numpy as np
import math as math
import mediapipe as mp
import cv2
import logging
import time
import os

from Utils.config import squat_vars
from Utils.display import checkSetupPassed, showLimbs, displayCounters
from Utils.logger_config import Logger
from Analysis_Functions.mainSquat import squatAnalysis
from Utils.file_output import file_writer

if __name__ == "__main__":
    # curr_datetime = time.strftime("%d-%m-%Y %H_%M_%S")
    # path_log = os.path.join(os.getcwd(), "Logger_Scripts", curr_datetime + ".log")
    path_log = os.path.join(os.getcwd(), "Logger_Scripts", "basic.log")
    logger = Logger()

    logger.setup().setLevel(logging.INFO)
    logger.setup().info("Starting")
    start_time = time.time()
    
    #initialize CV2 Video input and output
    # camera_id = "/dev/video0"
    # cam = cv2.VideoCapture(camera_id, cv2.CAP_V4L2)
    cam = cv2.VideoCapture(0)

    cv2.waitKey(100)
    windowName = "Camera View"
    cv2.namedWindow(windowName, cv2.WINDOW_NORMAL)
    #Main while loop to process frames using OpenCV and Mediapipe
    while cv2.waitKey(1) != 27: #esc key
        success, frame = cam.read()
        if success != True:
            print("no has_frame")
            continue
        
        frame.flags.writeable = False
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        #process frame using mediaPipe ML Model
        results = squat_vars.model.process(frame)

        frame.flags.writeable = True
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        #obtain landmarks
        pose_landmarks = results.pose_landmarks

        # Get landmarks into np array
        if pose_landmarks is not None:
            frame_height, frame_width = frame.shape[0], frame.shape[1]
            pose_landmarks = np.array([[lmk.x * frame_width, lmk.y * frame_height, lmk.z * frame_width]
                                        for lmk in pose_landmarks.landmark], dtype=np.float32)
            assert pose_landmarks.shape == (33, 3), 'Unexpected landmarks shape: {}'.format(pose_landmarks.shape)
        
        #check if setup time has finished and the squat analysis can begin
        if not squat_vars.hasPassedSetupTime:
            checkSetupPassed()

        #Run entire squat analysis if landmarks array has proper shape and if setup time passed
        landmarks = np.copy(pose_landmarks)
        if landmarks.shape == (33, 3) and squat_vars.hasPassedSetupTime:
            squatAnalysis(landmarks, frame)
        
        #display correct and incorrect rep counters
        displayCounters(frame)
        #display mediapipe pose estimation limbs
        showLimbs(frame, results)

        #drawLimbs.plot_landmarks(
            #results.pose_landmarks,
            #mp_holistic.POSE_CONNECTIONS

        #)

        #show entire processed frame on output display
        cv2.imshow(windowName, frame)

    #after user presses escape end the output video feed
    cam.release()
    cv2.destroyWindow(windowName)

    if not os.path.exists(os.path.join(os.getcwd(), "Results_RT")): os.mkdir(os.path.join(os.getcwd(), "Results_RT"))

    vid_counter = 0
    analysis_file = os.path.join(os.path.join(os.getcwd(), "Results_RT"), "results_" + str(vid_counter) + ".txt")
    while os.path.exists(analysis_file):
        analysis_file = os.path.join(os.path.join(os.getcwd(), "Results_RT"), "results_" + str(vid_counter) + ".txt")
        vid_counter += 1
    file_writer(analysis_file, start_time, vid_counter)
