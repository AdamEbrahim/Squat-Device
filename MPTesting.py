import numpy as np
import math as math
import mediapipe as mp
import cv2
import time
from collections import deque

#--GLOBAL VARIABLES--#

#Variables for MediaPipe Holistic ML model + limb drawing tools
drawLimbs = mp.solutions.drawing_utils
#mp_drawing_styles = mp.solutions.drawing_styles
mp_holistic = mp.solutions.holistic
model = mp_holistic.Holistic(min_detection_confidence=0.5,
                            min_tracking_confidence=0.5)

#Landmark variables
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

rightHipIndex = landmark_names.index('right_hip')
rightKneeIndex = landmark_names.index('right_knee')
rightShoulderIndex = landmark_names.index('right_shoulder')
rightAnkleIndex = landmark_names.index('right_ankle')

#Rep counter variables
repCounter = 0
incompleteCounter = 0
goodRep = True

#Issue added booleans
forwardLeanAdded = False

#Variables for ascent time calculations:
startAscentTime = time.time()
endAscentTime = time.time()
hasCalculatedAscentStart = False
hasCalculatedAscentEnd = False
startedDescent = False
prevHipHeight = 10000
ascentQ = deque() #queue to hold last 4 "transitions" between frames with regards to ascent or descent. 1 means ascent, 0 means descent
ascentQ.append(0) #initialize to start with all descents. 0 = descent, 1 = ascent.
ascentQ.append(0)
ascentQ.append(0)
ascentQ.append(0)
ascentQTotal = 0 #hold total of ascent queue, once equal to 3 we know ascent started (3 of 4 last frames = ascent)


#Variables for time in bottom position
startBottomTime = time.time()
endBottomTime = time.time()
hasCalculatedBottomStart = False
hasCalculatedBottomEnd = False

bottomHolds = True
bottomHoldTime = 3
hasCompletedBottomHold = False

#Current squat state variables
currentSquatState = 0 #0 = at top position, 1 = descent, 2 = at bottom, 3 = ascent
currentSquatStateText = "Top Position"

#Adjustable time before analysis starts occurring (allows for proper setup, and for the model to adjust to person)
setupTime = 5
hasPassedSetupTime = False
programStartTime = time.time()

#--------------------#


#--FUNCTIONS FOR OVERALL SQUAT FEEDBACK AND CLEANUP ONCE REP DONE--#

#Resetting many squat variables (per rep state)
def resetVariables(repIssues):
    #globals
    global hasCalculatedAscentStart, hasCalculatedAscentEnd, hasCalculatedBottomStart, hasCalculatedBottomEnd, hasCompletedBottomHold, forwardLeanAdded, ascentQ, ascentQTotal

    #reset list of current rep issues
    repIssues.clear()

    hasCalculatedAscentStart = False
    hasCalculatedAscentEnd = False
    hasCalculatedBottomStart = False
    hasCalculatedBottomEnd = False
    hasCompletedBottomHold = False

    #reset queue and variables used to determine when we start ascending. 
    ascentQ.clear()
    ascentQ.append(0) 
    ascentQ.append(0)
    ascentQ.append(0)
    ascentQ.append(0)
    ascentQTotal = 0 #hold total of ascent queue, once equal to 3 we know ascent started

    #reset issue added booleans
    forwardLeanAdded = False

#print summary of squat after each rep
def squatSummary(repIssues):
    #globals
    global startAscentTime, endAscentTime, hasCalculatedAscentStart, hasCalculatedAscentEnd, forwardLeanAdded, has

    if goodRep:
        print("Summary of Rep #" + str(repCounter + incompleteCounter) + " (Complete Rep):")
    else:
        print("Summary of Rep #" + str(repCounter + incompleteCounter) + " (Incomplete rep):")

    #print ascent time only if start and end time calculated
    if hasCalculatedAscentEnd and hasCalculatedAscentStart:
        print("    Time to ascend: " + str(endAscentTime - startAscentTime) + " seconds")

    #print time at bottom only if start and end time calculated
    if hasCalculatedBottomStart and hasCalculatedBottomEnd:
        print("    Time at bottom: " + str(endBottomTime - startBottomTime) + " seconds")

    #if user wanted to hold bottom position, print whether successful or not
    if bottomHolds:
        if hasCompletedBottomHold:
            print("    Successfully held bottom position for " + str(bottomHoldTime) + " seconds")
        else:
            print("    Failed to hold bottom position for " + str(bottomHoldTime) + " seconds")

    print("    Issues:")
    for i in range(len(repIssues)):
        print("      " + "Issue #" + str(i+1) + ": " + repIssues[i])

    resetVariables(repIssues)

#------------------------------------------------------------------#


#--FUNCTIONS RELATED TO BOTTOM POSITION TIME--#

#function to start timer for how long in bottom position of squat
def calcBottomStart():
    #globals
    global startBottomTime, hasCalculatedBottomStart

    startBottomTime = time.time()
    hasCalculatedBottomStart = True

def calcBottomEnd():
    #globals
    global hasCalculatedBottomEnd, endBottomTime

    endBottomTime = time.time()
    hasCalculatedBottomEnd = True

#function to check if person has held bottom position for input length of time and then do something once they have
def checkHasCompletedBottomHold():
    #globals
    global hasCompletedBottomHold

    if time.time() - startBottomTime >= bottomHoldTime:
        print("You have completed the hold")
        hasCompletedBottomHold = True

#----------------------------------------------#


#--FUNCTIONS RELATED TO SINGLE REP ASCENT TIME--#

#function to check for when we start ascent
def checkForAscent(rightHipHeight):
    #globals
    global prevHipHeight, hasCalculatedAscentStart, startAscentTime, ascentQTotal, ascentQ

    #calculate ascent start time based on if our hip height has been found to be increasing for at least 3 of 4 last frames. Queue
    if rightHipHeight > prevHipHeight and not hasCalculatedAscentStart:
        ascentQ.append(1)
        ascentQTotal = ascentQTotal - ascentQ.popleft() + 1 #maintain queue total
        if ascentQTotal == 3:
            startAscentTime = time.time()
            hasCalculatedAscentStart = True
        else:
            prevHipHeight = rightHipHeight
    elif not hasCalculatedAscentStart:
        ascentQ.append(0)
        ascentQTotal = ascentQTotal - ascentQ.popleft() #maintain queue total
        prevHipHeight = rightHipHeight

#Function to calculate end ascent time even if improper depth
def calculateAscentEnd():
    #globals
    global hasCalculatedAscentEnd, endAscentTime

    endAscentTime = time.time()
    hasCalculatedAscentEnd = True

#-----------------------------------------------#


#--FUNCTIONS FOR CURRENT SQUAT STATE--#

#function for squat state transitions (for wht position of the squat you are in)
def squatStateTransitions(angleUpperLeg, frame, repIssues):
    #globals
    global startedDescent, currentSquatState, currentSquatStateText, goodRep, repCounter, incompleteCounter
    
    if angleUpperLeg > 75:

        startedDescent = False

        if currentSquatState == 0:
            print("top position of squat")
        elif currentSquatState == 3:
            if hasCalculatedAscentStart and not hasCalculatedAscentEnd:
                calculateAscentEnd()

            print("Completed rep")
            if goodRep:
                repCounter = repCounter + 1
                squatSummary(repIssues)
            else:
                repIssues.append("Failed rep")
                incompleteCounter = incompleteCounter + 1
                squatSummary(repIssues)
                goodRep = True
            currentSquatState = 0
            currentSquatStateText = "Top Position"
        else:
            if hasCalculatedAscentStart and not hasCalculatedAscentEnd:
                calculateAscentEnd()

            print("Incomplete squat")
            repIssues.append("Improper depth")
            goodRep = False
            incompleteCounter = incompleteCounter + 1
            squatSummary(repIssues)

            goodRep = True
            currentSquatState = 0
            currentSquatStateText = "Top Position"

    elif angleUpperLeg > 15: 
        if currentSquatState == 0:
            print("descending")
            currentSquatState = 1
            currentSquatStateText = "Descending"
            startedDescent = True
        elif currentSquatState == 2:
            if not hasCalculatedBottomEnd and hasCalculatedBottomStart:
                calcBottomEnd()

            print("ascending")
            currentSquatState = 3
            currentSquatStateText = "Ascending"

    else:
        #If bottomHolds true, only in bottom position do you need to continue checking if has completed bottom hold
        if bottomHolds and hasCalculatedBottomStart and not hasCalculatedBottomEnd and not hasCompletedBottomHold:
            checkHasCompletedBottomHold()

        if currentSquatState == 1:
            if not hasCalculatedBottomStart:
                calcBottomStart()

            print("hit parallel")
            currentSquatState = 2
            currentSquatStateText = "Bottom Position"
        elif currentSquatState == 3:
            #print("Failed rep")
            #currentSquatStateText = "Failed Rep"
            #currentSquatState = 2
            #goodRep = False
            print("hi")

    #Show current squat state on screen
    cv2.putText(frame, currentSquatStateText, (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (223, 244, 16), 6, cv2.LINE_AA)

#-------------------------------------#


#--MAIN FUNCTIONS FOR SQUAT ANALYSIS RELATED TO DIFFERENT LIMBS/LANDMARKS--#

#Squat analysis related to back
def backAnalysis(landmarks, frame, repIssues):
    #globals
    global forwardLeanAdded

    if landmarks[rightShoulderIndex].shape == (3,) and landmarks[rightHipIndex].shape == (3,):

        #check back angle (forward tilt) based on right shoulder and right hip:
        yDistBack = landmarks[rightShoulderIndex][1] - landmarks[rightHipIndex][1]
        xDistBack = landmarks[rightHipIndex][0] - landmarks[rightShoulderIndex][0]
        angleBack = round(math.degrees(math.atan(xDistBack/yDistBack)))

        #back angle issue #1: too much forward lean
        if angleBack > 45 and not forwardLeanAdded:
            repIssues.append("Excessive forward lean")
            forwardLeanAdded = True
            
        #draw back angle on the frame at the hip
        hipPos = np.array([landmarks[rightHipIndex][0], landmarks[rightHipIndex][1]])
        hipVerticalLineEnd = np.array([landmarks[rightHipIndex][0], landmarks[rightHipIndex][1] - 150])
        cv2.line(frame, tuple(hipPos.astype(int)), tuple(hipVerticalLineEnd.astype(int)), (223, 244, 16), 8)
        cv2.putText(frame, str(angleBack), tuple(hipPos.astype(int)), cv2.FONT_HERSHEY_SIMPLEX, 2.5, (223, 244, 16), 5, cv2.LINE_AA)

#Squat analysis related to upper leg
def upperLegAnalysis(landmarks, frame, repIssues):
    #globals
    global startedDescent

    #check upper leg angle (dist from parallel to ground) based on right hip and right knee:
    if landmarks[rightHipIndex].shape == (3,) and landmarks[rightKneeIndex].shape == (3,):
        yDistUpperLeg = landmarks[rightHipIndex][1] - landmarks[rightKneeIndex][1]
        xDistUpperLeg = landmarks[rightHipIndex][0] - landmarks[rightKneeIndex][0]
        angleUpperLeg = round(math.degrees(math.atan(yDistUpperLeg/xDistUpperLeg)))

        kneePos = np.array([landmarks[rightKneeIndex][0], landmarks[rightKneeIndex][1]])
        kneeHorizontalLineEnd = np.array([landmarks[rightKneeIndex][0] + 150, landmarks[rightKneeIndex][1]])
        cv2.line(frame, tuple(kneePos.astype(int)), tuple(kneeHorizontalLineEnd.astype(int)), (223, 244, 16), 8)
        cv2.putText(frame, str(angleUpperLeg), tuple(kneePos.astype(int)), cv2.FONT_HERSHEY_SIMPLEX, 2.5, (223, 244, 16), 5, cv2.LINE_AA)

        #Things to do after you have started descending:
        if startedDescent: 
            #check for when you start ascending
            checkForAscent(landmarks[rightHipIndex][1])

        #Call function to determine squat state/transitions
        squatStateTransitions(angleUpperLeg, frame, repIssues)
       
        
#Squat analysis related to lower leg
def lowerLegAnalysis(landmarks, frame, repIssues):
    #globals

    #check lower leg angle (forward tilt) based on right ankle and right knee:
    if landmarks[rightAnkleIndex].shape == (3,) and landmarks[rightKneeIndex].shape == (3,):
        yDistLowerLeg = landmarks[rightKneeIndex][1] - landmarks[rightAnkleIndex][1]
        xDistLowerLeg = landmarks[rightHipIndex][0] - landmarks[rightShoulderIndex][0]
        angleLowerLeg = round(math.degrees(math.atan(xDistLowerLeg/yDistLowerLeg)))

        anklePos = np.array([landmarks[rightAnkleIndex][0], landmarks[rightAnkleIndex][1]])
        ankleVerticalLineEnd = np.array([landmarks[rightAnkleIndex][0], landmarks[rightAnkleIndex][1] - 150])
        cv2.line(frame, tuple(anklePos.astype(int)), tuple(ankleVerticalLineEnd.astype(int)), (223, 244, 16), 8)
        cv2.putText(frame, str(angleLowerLeg), tuple(anklePos.astype(int)), cv2.FONT_HERSHEY_SIMPLEX, 2.5, (223, 244, 16), 5, cv2.LINE_AA)


#main squat analysis wrapper function using the pose landmarks (current pose analysis)
def squatAnalysis(landmarks, frame, repIssues):
    backAnalysis(landmarks, frame, repIssues)
    upperLegAnalysis(landmarks, frame, repIssues)
    lowerLegAnalysis(landmarks, frame, repIssues)

#--------------------------------------------------------------------------#


#--FUNCTIONS FOR STUFF DISPLAYED ON SCREEN BY OPENCV--#

#function to display correct and incorrect rep counters
def displayCounters(frame):
    #globals
    global repCounter, incompleteCounter

    cv2.putText(frame, "Complete reps: " + str(repCounter), (900, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (223, 244, 16), 6, cv2.LINE_AA)
    cv2.putText(frame, "Incomplete reps: " + str(incompleteCounter), (900, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (223, 244, 16), 6, cv2.LINE_AA)

#function to display mediapipe pose estimation limbs
def showLimbs(frame, results):
    drawLimbs.draw_landmarks(
        frame,
        results.face_landmarks,
        mp_holistic.FACEMESH_CONTOURS,
        landmark_drawing_spec=None,
        #connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_contours_style()
    )
    drawLimbs.draw_landmarks(
        frame,
        results.pose_landmarks,
        mp_holistic.POSE_CONNECTIONS,
        #landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
    )

#----------------------------------------------------------#


#--FUNCTIONS FOR STUFF DISPLAYED ON SCREEN BY OPENCV--#

def checkSetupPassed():
    global hasPassedSetupTime
    if time.time() - programStartTime >= setupTime:
        hasPassedSetupTime = True
        print("squat analysis started")

#-----------------------------------------------------#


#--MAIN FUNCTION--#

def main():
    #globals

    #initialize CV2 Video input and output
    cam = cv2.VideoCapture(0)
    windowName = "Camera View"
    cv2.namedWindow(windowName, cv2.WINDOW_NORMAL)
    
    #initialize important squat analysis non-global variables
    repIssues = [] #list to hold all issues during a rep, prints after the rep

    #Main while loop to process frames using OpenCV and Mediapipe
    while cv2.waitKey(1) != 27:
        has_frame, frame = cam.read()
        if has_frame != True:
            break

        frame.flags.writeable = False
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        #process frame using mediaPipe ML Model
        results = model.process(frame)

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
        if not hasPassedSetupTime:
            checkSetupPassed()

        #Run entire squat analysis if landmarks array has proper shape and if setup time passed
        landmarks = np.copy(pose_landmarks)
        if landmarks.shape == (33, 3) and hasPassedSetupTime:
            squatAnalysis(landmarks, frame, repIssues)
        
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

#-----------------#

main()