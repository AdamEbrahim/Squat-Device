# is interpolating necessary if downsampling to 10fps is accurate?
#keep list of issues an what squat rep it was on to finally print
#print total reps attempted to text file
import cv2
import os
import numpy as np
import time

from Utils.config import squat_vars
from Utils.display import showLimbs, displayCounters
from Analysis_Functions.mainSquat import squatAnalysis
from Utils.file_output import file_writer

def squat_post_process(file_path, name, view=False):
    success = True
    video = cv2.VideoCapture(file_path)
    # fourcc = cv2.VideoWriter_fourcc(*'MP4V')
    start_time = time.time()
    frame_counter = 0

    if (video.isOpened()== False): 
        print("Video not open")

    while success:
        frame_counter += 1
        # print("Frame : %d" % frame_counter)
        success, frame = video.read()
        if frame_counter % 3 != 0:
            continue
        if not success:
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
        # if not squat_vars.hasPassedSetupTime:
        # checkSetupPassed()

        #Run entire squat analysis if landmarks array has proper shape and if setup time passed
        landmarks = np.copy(pose_landmarks)
        # if landmarks.shape == (33, 3) and squat_vars.hasPassedSetupTime:
        if landmarks.shape == (33, 3):
            squatAnalysis(landmarks, frame)
        
        #display correct and incorrect rep counters
        displayCounters(frame)
        showLimbs(frame, results)

        if view:
            cv2.imshow("Frame", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    print(frame_counter)
    print("Complete")

    analysis_file = os.path.join(os.path.join(os.getcwd(), "Results_PP"), str(name) + "_results.txt")
    file_writer(analysis_file, start_time, name, file_path)

file_path = r"/Users/dcunhrya/Movies/ekans_squat_side.mp4"
squat_post_process(file_path, 'ekans', view = True)