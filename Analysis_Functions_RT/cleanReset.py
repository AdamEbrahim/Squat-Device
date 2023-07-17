#--FUNCTIONS FOR OVERALL SQUAT FEEDBACK AND CLEANUP ONCE REP DONE--#
from Utils.config import squat_vars 

#Resetting many squat variables (per rep state)
def resetVariables():
    #reset list of current rep issues
    squat_vars.repIssues.clear()

    squat_vars.hasCalculatedAscentStart = True
    squat_vars.hasCalculatedAscentEnd = False
    squat_vars.hasCalculatedBottomStart = False
    squat_vars.hasCalculatedBottomEnd = False
    squat_vars.hasCompletedBottomHold = False

    #reset queue and variables used to determine when we start ascending. 
    squat_vars.ascentQ.clear()
    squat_vars.ascentQ.extend((0, 0, 0, 0)) 
    squat_vars.ascentQTotal = 0 #hold total of ascent queue, once equal to 3 we know ascent started

    #reset issue added booleans
    squat_vars.forwardLeanAdded = False

#print summary of squat after each rep
def squatSummary():
    if squat_vars.goodRep:
        print("Summary of Rep #" + str(squat_vars.repCounter + squat_vars.incompleteCounter) + " (Complete Rep):")
    else:
        print("Summary of Rep #" + str(squat_vars.repCounter + squat_vars.incompleteCounter) + " (Incomplete rep):")

    #print ascent time only if start and end time calculated
    if squat_vars.hasCalculatedAscentEnd and squat_vars.hasCalculatedAscentStart:
        print("    Time to ascend: " + str(squat_vars.endAscentTime - squat_vars.startAscentTime) + " seconds")

    #print time at bottom only if start and end time calculated
    if squat_vars.hasCalculatedBottomStart and squat_vars.hasCalculatedBottomEnd:
        print("    Time at bottom: " + str(squat_vars.endBottomTime - squat_vars.startBottomTime) + " seconds")

    #if user wanted to hold bottom position, print whether successful or not
    if squat_vars.bottomHolds:
        if squat_vars.hasCompletedBottomHold:
            print("    Successfully held bottom position for " + str(squat_vars.bottomHoldTime) + " seconds")
        else:
            print("    Failed to hold bottom position for " + str(squat_vars.bottomHoldTime) + " seconds")

    print("    Issues:")
    for i in range(len(squat_vars.repIssues)):
        print("      " + "Issue #" + str(i+1) + ": " + squat_vars.repIssues[i])

    resetVariables()