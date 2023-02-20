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

landmark_names = [
        'nose',
        'left_eye_inner', 'left_eye', 'left_eye_outer',
        'right_eye_inner', 'right_eye', 'right_eye_outer',
        'left_ear', 'right_ear',
        'mouth_left', 'mouth_right',
        'left_shoulder', 'right_shoulder',
        'left_elbow', 'right_elbow',
        'left_wrist', 'right_wrist',
        'left_pinky_1', 'right_pinky_1',
        'left_index_1', 'right_index_1',
        'left_thumb_2', 'right_thumb_2',
        'left_hip', 'right_hip',
        'left_knee', 'right_knee',
        'left_ankle', 'right_ankle',
        'left_heel', 'right_heel',
        'left_foot_index', 'right_foot_index',
]

atBottom = False
uprightAngle = True

rightHipIndex = landmark_names.index('right_hip')
rightKneeIndex = landmark_names.index('right_knee')
rightShoulderIndex = landmark_names.index('right_shoulder')
rightAnkleIndex = landmark_names.index('right_ankle')

repCounter = 0
incompleteCounter = 0
goodRep = True

repIssues = [] #list to hold all issues during a rep, prints after the rep

#print summary of squat after each rep
def squatSummary():
    if goodRep:
        print("Summary of Rep #" + (repCounter + incompleteCounter) + " (Complete Rep):")
    else:
        print("Summary of Rep #" + (repCounter + incompleteCounter) + " (Incomplete rep):")

    for i in range(len(repIssues)):
        print("    " + "Issue #" + (i+1) + ": " + repIssues[i])
    repIssues.clear()

currentSquatState = 0 #0 = at top position, 1 = descent, 2 = at bottom, 3 = ascent
currentSquatStateText = "Top Position"
while cv2.waitKey(1) != 27:
    has_frame, frame = cam.read()
    if has_frame != True:
        break

    frame.flags.writeable = False
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = model.process(frame)

    frame.flags.writeable = True
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    #display correct and incorrect rep counters
    cv2.putText(frame, "Complete reps: " + str(repCounter), (900, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (223, 244, 16), 6, cv2.LINE_AA)
    cv2.putText(frame, "Incomplete reps: " + str(incompleteCounter), (900, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (223, 244, 16), 6, cv2.LINE_AA)


    pose_landmarks = results.pose_landmarks

    if pose_landmarks is not None:
      # Get landmarks into np array
      frame_height, frame_width = frame.shape[0], frame.shape[1]
      pose_landmarks = np.array([[lmk.x * frame_width, lmk.y * frame_height, lmk.z * frame_width]
                                 for lmk in pose_landmarks.landmark], dtype=np.float32)
      assert pose_landmarks.shape == (33, 3), 'Unexpected landmarks shape: {}'.format(pose_landmarks.shape)

    landmarks = np.copy(pose_landmarks)
    
    if landmarks.shape == (33, 3):

        #check if hit depth based on rightHip and rightKnee:
        if landmarks[rightHipIndex].shape == (3,) and landmarks[rightKneeIndex].shape == (3,):    
        #for i in range(len(landmarks)):
        #print(i, landmarks[i])
            if abs(landmarks[rightHipIndex][1] - landmarks[rightKneeIndex][1]) < 5 and not atBottom:
                print("you have hit proper depth")
                atBottom = True
            elif landmarks[rightHipIndex][1] - landmarks[rightKneeIndex][1] > 5 and atBottom:
                print("you have exited the bottom position")
                atBottom = False

        #check back angle (forward tilt) based on right shoulder and right hip:
        if landmarks[rightShoulderIndex].shape == (3,) and landmarks[rightHipIndex].shape == (3,):

            #back angle
            yDistBack = landmarks[rightShoulderIndex][1] - landmarks[rightHipIndex][1]
            xDistBack = landmarks[rightHipIndex][0] - landmarks[rightShoulderIndex][0]
            angleBack = round(math.degrees(math.atan(xDistBack/yDistBack)))

            #back angle issue #1: too much forward lean
            if angleBack > 45:
                repIssues.append("Excessive forward lean")
                
            #draw back angle on the frame at the hip
            hipPos = np.array([landmarks[rightHipIndex][0], landmarks[rightHipIndex][1]])
            hipVerticalLineEnd = np.array([landmarks[rightHipIndex][0], landmarks[rightHipIndex][1] - 150])
            cv2.line(frame, tuple(hipPos.astype(int)), tuple(hipVerticalLineEnd.astype(int)), (223, 244, 16), 8)
            cv2.putText(frame, str(angleBack), tuple(hipPos.astype(int)), cv2.FONT_HERSHEY_SIMPLEX, 2.5, (223, 244, 16), 5, cv2.LINE_AA)

        #check upper leg angle (dist from parallel to ground) based on right hip and right knee:
        if landmarks[rightHipIndex].shape == (3,) and landmarks[rightKneeIndex].shape == (3,):
            yDistUpperLeg = landmarks[rightHipIndex][1] - landmarks[rightKneeIndex][1]
            xDistUpperLeg = landmarks[rightHipIndex][0] - landmarks[rightKneeIndex][0]
            angleUpperLeg = round(math.degrees(math.atan(yDistUpperLeg/xDistUpperLeg)))

            kneePos = np.array([landmarks[rightKneeIndex][0], landmarks[rightKneeIndex][1]])
            kneeHorizontalLineEnd = np.array([landmarks[rightKneeIndex][0] + 150, landmarks[rightKneeIndex][1]])
            cv2.line(frame, tuple(kneePos.astype(int)), tuple(kneeHorizontalLineEnd.astype(int)), (223, 244, 16), 8)
            cv2.putText(frame, str(angleUpperLeg), tuple(kneePos.astype(int)), cv2.FONT_HERSHEY_SIMPLEX, 2.5, (223, 244, 16), 5, cv2.LINE_AA)
            

            #state transition diagram for wht position of the squat you are in
            if angleUpperLeg > 70:
                if currentSquatState == 0:
                    print("top position of squat")
                elif currentSquatState == 3:
                    print("Completed rep")
                    if goodRep:
                        repCounter = repCounter + 1
                        squatSummary()
                    else:
                        repIssues.append("Failed rep")
                        incompleteCounter = incompleteCounter + 1
                        squatSummary()
                        goodRep = True
                    currentSquatState = 0
                    currentSquatStateText = "Top Position"
                else:
                    print("Incomplete squat")
                    repIssues.append("Improper depth")
                    goodRep = False
                    incompleteCounter = incompleteCounter + 1
                    squatSummary()

                    goodRep = True
                    currentSquatState = 0
                    currentSquatStateText = "Top Position"

            elif angleUpperLeg > 15: 
                if currentSquatState == 0:
                    print("descending")
                    currentSquatState = 1
                    currentSquatStateText = "Descending"
                elif currentSquatState == 2:
                    print("ascending")
                    currentSquatState = 3
                    currentSquatStateText = "Ascending"

            else:
                if currentSquatState == 1:
                    print("hit parallel")
                    currentSquatState = 2
                    currentSquatStateText = "Bottom Position"
                elif currentSquatState == 3:
                    print("Failed rep")
                    currentSquatStateText = "Failed Rep"
                    currentSquatState = 2
                    goodRep = False

            #Show current squat state on screen
            cv2.putText(frame, currentSquatStateText, (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (223, 244, 16), 6, cv2.LINE_AA)


        #check lower leg angle (forward tilt) based on right ankle and right knee:
        if landmarks[rightAnkleIndex].shape == (3,) and landmarks[rightKneeIndex].shape == (3,):
            yDistLowerLeg = landmarks[rightKneeIndex][1] - landmarks[rightAnkleIndex][1]
            xDistLowerLeg = landmarks[rightHipIndex][0] - landmarks[rightShoulderIndex][0]
            angleLowerLeg = round(math.degrees(math.atan(xDistLowerLeg/yDistLowerLeg)))

            anklePos = np.array([landmarks[rightAnkleIndex][0], landmarks[rightAnkleIndex][1]])
            ankleVerticalLineEnd = np.array([landmarks[rightAnkleIndex][0], landmarks[rightAnkleIndex][1] - 150])
            cv2.line(frame, tuple(anklePos.astype(int)), tuple(ankleVerticalLineEnd.astype(int)), (223, 244, 16), 8)
            cv2.putText(frame, str(angleLowerLeg), tuple(anklePos.astype(int)), cv2.FONT_HERSHEY_SIMPLEX, 2.5, (223, 244, 16), 5, cv2.LINE_AA)
       

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

    #drawLimbs.plot_landmarks(
        #results.pose_landmarks,
        #mp_holistic.POSE_CONNECTIONS

    #)



    cv2.imshow(windowName, frame)





cam.release()
cv2.destroyWindow(windowName)

