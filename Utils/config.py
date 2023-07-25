############ CONFIG VARIABLES ############
import time
from collections import deque
import mediapipe as mp

class create_all_squat_variables:
    def __init__(self):
        #var for MediaPipe Holistic ML model + limb tools
        self.drawLimbs = mp.solutions.drawing_utils
        self.mp_holistic = mp.solutions.holistic
        self.model = self.mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.mp_pose = mp.solutions.pose

        #landmark vars
        self.landmark_names = [
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
        self.rightHipIndex = self.landmark_names.index('right_hip')
        self.rightKneeIndex = self.landmark_names.index('right_knee')
        self.rightShoulderIndex = self.landmark_names.index('right_shoulder')
        self.rightAnkleIndex = self.landmark_names.index('right_ankle')

        #rep counter vars
        self.repCounter = 0
        self.incompleteCounter = 0
        self.goodRep = True

        #isse added booleans
        self.forwardLeanAdded = False

        self.startAscentTime = time.time()
        self.endAscentTime = time.time()
        self.hasCalculatedAscentStart = False
        self.hasCalculatedAscentEnd = False
        self.startedDescent = False
        self.prevHipHeight = 10000
        self.ascentQ = deque() #queue to hold last 4 "transitions" between frames with regards to ascent or descent. 1 means ascent, 0 means descent
        self.ascentQ.extend((0,0,0,0)) #initialize to start with all descents. 0 = descent, 1 = ascent.
        self.ascentQTotal = 0 #hold total of ascent queue, once equal to 3 we know ascent started (3 of 4 last frames = ascent)

        #Variables for time in bottom position
        self.startBottomTime = time.time()
        self.endBottomTime = time.time()
        self.hasCalculatedBottomStart = False
        self.hasCalculatedBottomEnd = False

        self.bottomHolds = True
        self.bottomHoldTime = 2
        self.hasCompletedBottomHold = False

        #Current squat state variables
        self.currentSquatState = 0 #0 = at top position, 1 = descent, 2 = at bottom, 3 = ascent
        self.currentSquatStateText = ""
        self.state = [-1]

        #Adjustable time before analysis starts occurring (allows for proper setup, and for the model to adjust to person)
        self.setupTime = 5
        self.hasPassedSetupTime = False
        self.programStartTime = time.time()
        
        #list to hold all issues during a rep, prints after the rep
        self.repIssues = []
        
        #list to write to file all issues
        self.overallIssues = []


squat_vars = create_all_squat_variables()
squat_vars_pp = create_all_squat_variables()