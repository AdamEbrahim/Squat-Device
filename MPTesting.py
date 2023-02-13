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

currentSquatState = 0 #0 = at top position, 1 = descent, 2 = at bottom, 3 = ascent
while cv2.waitKey(1) != 27:
    has_frame, frame = cam.read()
    if has_frame != True:
        break

    frame.flags.writeable = False
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = model.process(frame)

    frame.flags.writeable = True
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    pose_landmarks = results.pose_world_landmarks

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
            xDistBack = landmarks[rightShoulderIndex][0] - landmarks[rightHipIndex][0]
            angleBack = round(math.degrees(math.atan(xDistBack/yDistBack)))
            #print(angleBack)
            #if angle > 60 and uprightAngle:
                
            #draw back angle on the frame at the hip
            hipPos = np.array(landmarks[rightHipIndex][0], landmarks[rightHipIndex][1])
            hipVerticalLineEnd = np.array(landmarks[rightHipIndex][0], landmarks[rightHipIndex][1] + 5)
            cv2.line(frame, tuple(hipPos), tuple(hipVerticalLineEnd), (255, 0, 0), 2)
            cv2.putText(frame, str(angleBack), tuple(hipPos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2, cv2.LINE_AA)

        #check upper leg angle (dist from parallel to ground) based on right hip and right knee:
        if landmarks[rightHipIndex].shape == (3,) and landmarks[rightKneeIndex].shape == (3,):
            yDistUpperLeg = landmarks[rightHipIndex][1] - landmarks[rightKneeIndex][1]
            xDistUpperLeg = landmarks[rightKneeIndex][0] - landmarks[rightHipIndex][0]
            angleUpperLeg = round(math.degrees(math.atan(yDistUpperLeg/xDistUpperLeg)))

            kneePos = np.array(landmarks[rightKneeIndex][0], landmarks[rightKneeIndex][1])
            kneeHorizontalLineEnd = np.array(landmarks[rightKneeIndex][0] - 5, landmarks[rightKneeIndex][1])
            cv2.line(frame, tuple(kneePos), tuple(kneeHorizontalLineEnd), (255, 0, 0), 2)
            cv2.putText(frame, str(angleUpperLeg), tuple(kneePos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2, cv2.LINE_AA)

            #state transition diagram for wht position of the squat you are in
            if angleUpperLeg > 70:
                if currentSquatState == 0:
                    print("still in top position of squat")
                elif currentSquatState == 3:
                    print("Completed rep")
                    currentSquatState = 0
            elif angleUpperLeg > 15: 
                if currentSquatState == 0:
                    print("descending")
                    currentSquatState = 1
                elif currentSquatState == 2:
                    print("ascending")
                    currentSquatState = 3
            elif angleUpperLeg > -5:
                if currentSquatState == 1:
                    print("hit parallel")
                    currentSquatState = 2
            else:
                print("deeper than parallel")


        #check lower leg angle (forward tilt) based on right ankle and right knee:
        if landmarks[rightAnkleIndex].shape == (3,) and landmarks[rightKneeIndex].shape == (3,):
            yDistLowerLeg = landmarks[rightKneeIndex][1] - landmarks[rightAnkleIndex][1]
            xDistLowerLeg = landmarks[rightShoulderIndex][0] - landmarks[rightHipIndex][0]
            angleLowerLeg = round(math.degrees(math.atan(xDistLowerLeg/yDistLowerLeg)))

            anklePos = np.array(landmarks[rightAnkleIndex][0], landmarks[rightAnkleIndex][1])
            ankleVerticalLineEnd = np.array(landmarks[rightAnkleIndex][0], landmarks[rightAnkleIndex][1] + 5)
            cv2.line(frame, tuple(anklePos), tuple(ankleVerticalLineEnd), (255, 0, 0), 2)
            cv2.putText(frame, str(angleLowerLeg), tuple(anklePos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2, cv2.LINE_AA)
       


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



    cv2.imshow(windowName, cv2.flip(frame, 1))





cam.release()
cv2.destroyWindow(windowName)

