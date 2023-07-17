#--FUNCTIONS FOR CURRENT SQUAT STATE--#
from Utils.config import squat_vars
from Analysis_Functions.singleRep import calculateAscentEnd
from Analysis_Functions.cleanReset import squatSummary
from Analysis_Functions.bottomPosition import calcBottomEnd, calcBottomStart, checkHasCompletedBottomHold

import cv2

#function for squat state transitions (for wht position of the squat you are in)
def squatStateTransitions(angleUpperLeg, frame):
    if angleUpperLeg > 75:

        squat_vars.startedDescent = False

        if squat_vars.currentSquatState == 0:
            print("top position of squat")
        elif squat_vars.currentSquatState == 3:
            if squat_vars.hasCalculatedAscentStart and not squat_vars.hasCalculatedAscentEnd:
                calculateAscentEnd()

            print("Completed rep")
            if squat_vars.goodRep:
                squat_vars.repCounter += 1
                squatSummary()
            else:
                squat_vars.repIssues.append("Failed rep")
                squat_vars.incompleteCounter += 1
                squatSummary()
                squat_vars.goodRep = True
            squat_vars.currentSquatState = 0
            squat_vars.urrentSquatStateText = "Top Position"
        else:
            if squat_vars.hasCalculatedAscentStart and not squat_vars.hasCalculatedAscentEnd:
                calculateAscentEnd()

            print("Incomplete squat")
            squat_vars.repIssues.append("Improper depth")
            squat_vars.goodRep = False
            squat_vars.incompleteCounter += 1
            squatSummary()

            squat_vars.goodRep = True
            squat_vars.currentSquatState = 0
            squat_vars.currentSquatStateText = "Top Position"

    elif angleUpperLeg > 15: 
        if squat_vars.currentSquatState == 0:
            print("descending")
            squat_vars.currentSquatState = 1
            squat_vars.currentSquatStateText = "Descending"
            squat_vars.startedDescent = True
        elif squat_vars.currentSquatState == 2:
            if not squat_vars.hasCalculatedBottomEnd and squat_vars.hasCalculatedBottomStart:
                calcBottomEnd()

            print("ascending")
            squat_vars.currentSquatState = 3
            squat_vars.currentSquatStateText = "Ascending"

    else:
        #If bottomHolds true, only in bottom position do you need to continue checking if has completed bottom hold
        if squat_vars.bottomHolds and squat_vars.hasCalculatedBottomStart and not squat_vars.hasCalculatedBottomEnd and not squat_vars.hasCompletedBottomHold:
            checkHasCompletedBottomHold()

        if squat_vars.currentSquatState == 1:
            if not squat_vars.hasCalculatedBottomStart:
                calcBottomStart()

            print("hit parallel")
            squat_vars.currentSquatState = 2
            squat_vars.currentSquatStateText = "Bottom Position"
        elif squat_vars.currentSquatState == 3:
            #print("Failed rep")
            #currentSquatStateText = "Failed Rep"
            #currentSquatState = 2
            #goodRep = False
            print("hi")

    #Show current squat state on screen
    cv2.putText(frame, squat_vars.currentSquatStateText, (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (223, 244, 16), 6, cv2.LINE_AA)
