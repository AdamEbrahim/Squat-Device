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

while cv2.waitKey(1) != 27:
    has_frame, frame = cam.read()
    if has_frame != True:
        break

    frame.flags.writeable = False
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = model.process(frame)
    pose_landmarks = results.pose_world_landmarks

    if pose_landmarks is not None:
      # Get landmarks.
      frame_height, frame_width = frame.shape[0], frame.shape[1]
      pose_landmarks = np.array([[lmk.x * frame_width, lmk.y * frame_height, lmk.z * frame_width]
                                 for lmk in pose_landmarks.landmark], dtype=np.float32)
      assert pose_landmarks.shape == (33, 3), 'Unexpected landmarks shape: {}'.format(pose_landmarks.shape)

    landmarks = np.copy(pose_landmarks)
    
    if landmarks.shape == (33, 3):
        if landmarks[rightHipIndex].shape == (3,) and landmarks[rightKneeIndex].shape == (3,):    
        #for i in range(len(landmarks)):
        #print(i, landmarks[i])
            if abs(landmarks[rightHipIndex][1] - landmarks[rightKneeIndex][1]) < 5 and not atBottom:
                print("you have hit proper depth")
                atBottom = True
            elif landmarks[rightHipIndex][1] - landmarks[rightKneeIndex][1] > 5 and atBottom:
                print("you have exited the bottom position")
                atBottom = False

        if landmarks[rightShoulderIndex].shape == (3,) and landmarks[rightHipIndex].shape == (3,):
            #back angle
            yDist = landmarks[rightShoulderIndex][1] - landmarks[rightHipIndex][1]
            xDist = landmarks[rightShoulderIndex][0] - landmarks[rightHipIndex][0]
            angle = math.degrees(math.atan(yDist/xDist))
            print(angle)
            #if angle > 60 and uprightAngle:
       



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

