#--MAIN FUNCTIONS FOR SQUAT ANALYSIS RELATED TO DIFFERENT LIMBS/LANDMARKS--#
from Utils.config import squat_vars
from Analysis_Functions.currentState import squatStateTransitions
from Analysis_Functions.singleRep import checkForAscent

import cv2
import math as m
import numpy as np

#Squat analysis related to back
def backAnalysis(landmarks, frame):
    if landmarks[squat_vars.rightShoulderIndex].shape == (3,) and landmarks[squat_vars.rightHipIndex].shape == (3,):

        #check back angle (forward tilt) based on right shoulder and right hip:
        yDistBack = landmarks[squat_vars.rightShoulderIndex][1] - landmarks[squat_vars.rightHipIndex][1]
        xDistBack = landmarks[squat_vars.rightHipIndex][0] - landmarks[squat_vars.rightShoulderIndex][0]
        angleBack = round(m.degrees(m.atan(xDistBack/yDistBack)))

        #back angle issue #1: too much forward lean
        if angleBack > 45 and not squat_vars.forwardLeanAdded:
            squat_vars.repIssues.append("Excessive forward lean")
            squat_vars.forwardLeanAdded = True
            
        #draw back angle on the frame at the hip
        hipPos = np.array([landmarks[squat_vars.rightHipIndex][0], landmarks[squat_vars.rightHipIndex][1]])
        hipVerticalLineEnd = np.array([landmarks[squat_vars.rightHipIndex][0], landmarks[squat_vars.rightHipIndex][1] - 150])
        cv2.line(frame, tuple(hipPos.astype(int)), tuple(hipVerticalLineEnd.astype(int)), (223, 244, 16), 8)
        cv2.putText(frame, str(angleBack), tuple(hipPos.astype(int)), cv2.FONT_HERSHEY_SIMPLEX, 2.5, (223, 244, 16), 5, cv2.LINE_AA)

#Squat analysis related to upper leg
def upperLegAnalysis(landmarks, frame):
    #check upper leg angle (dist from parallel to ground) based on right hip and right knee:
    if landmarks[squat_vars.rightHipIndex].shape == (3,) and landmarks[squat_vars.rightKneeIndex].shape == (3,):
        yDistUpperLeg = landmarks[squat_vars.rightHipIndex][1] - landmarks[squat_vars.rightKneeIndex][1]
        xDistUpperLeg = landmarks[squat_vars.rightHipIndex][0] - landmarks[squat_vars.rightKneeIndex][0]
        angleUpperLeg = abs(round(m.degrees(m.atan(yDistUpperLeg/xDistUpperLeg))))

        kneePos = np.array([landmarks[squat_vars.rightKneeIndex][0], landmarks[squat_vars.rightKneeIndex][1]])
        kneeHorizontalLineEnd = np.array([landmarks[squat_vars.rightKneeIndex][0] + 150, landmarks[squat_vars.rightKneeIndex][1]])
        cv2.line(frame, tuple(kneePos.astype(int)), tuple(kneeHorizontalLineEnd.astype(int)), (223, 244, 16), 8)
        cv2.putText(frame, str(angleUpperLeg), tuple(kneePos.astype(int)), cv2.FONT_HERSHEY_SIMPLEX, 2.5, (223, 244, 16), 5, cv2.LINE_AA)

        #Things to do after you have started descending:
        if squat_vars.startedDescent: 
            #check for when you start ascending
            checkForAscent(landmarks[squat_vars.rightHipIndex][1])

        #Call function to determine squat state/transitions
        squatStateTransitions(angleUpperLeg, frame)
       
        
#Squat analysis related to lower leg
def lowerLegAnalysis(landmarks, frame):
    #globals

    #check lower leg angle (forward tilt) based on right ankle and right knee:
    if landmarks[squat_vars.rightAnkleIndex].shape == (3,) and landmarks[squat_vars.rightKneeIndex].shape == (3,):
        yDistLowerLeg = landmarks[squat_vars.rightKneeIndex][1] - landmarks[squat_vars.rightAnkleIndex][1]
        xDistLowerLeg = landmarks[squat_vars.rightHipIndex][0] - landmarks[squat_vars.rightShoulderIndex][0]
        angleLowerLeg = round(m.degrees(m.atan(xDistLowerLeg/yDistLowerLeg)))

        anklePos = np.array([landmarks[squat_vars.rightAnkleIndex][0], landmarks[squat_vars.rightAnkleIndex][1]])
        ankleVerticalLineEnd = np.array([landmarks[squat_vars.rightAnkleIndex][0], landmarks[squat_vars.rightAnkleIndex][1] - 150])
        cv2.line(frame, tuple(anklePos.astype(int)), tuple(ankleVerticalLineEnd.astype(int)), (223, 244, 16), 8)
        cv2.putText(frame, str(angleLowerLeg), tuple(anklePos.astype(int)), cv2.FONT_HERSHEY_SIMPLEX, 2.5, (223, 244, 16), 5, cv2.LINE_AA)


#main squat analysis wrapper function using the pose landmarks (current pose analysis)
def squatAnalysis(landmarks, frame):
    backAnalysis(landmarks, frame)
    upperLegAnalysis(landmarks, frame)
    lowerLegAnalysis(landmarks, frame)
