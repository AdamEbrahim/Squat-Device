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
    issue_per_rep = []
    if squat_vars.goodRep:
        complete = "Summary of Rep #" + str(squat_vars.repCounter + squat_vars.incompleteCounter) + " (Complete Rep):"
        issue_per_rep.append(complete)
        print(complete)
    else:
        incomplete = "Summary of Rep #" + str(squat_vars.repCounter + squat_vars.incompleteCounter) + " (Incomplete rep):"
        issue_per_rep.append(incomplete)
        print(incomplete)

    #print ascent time only if start and end time calculated
    if squat_vars.hasCalculatedAscentEnd and squat_vars.hasCalculatedAscentStart:
        ascend = "    Time to ascend: " + str(round(squat_vars.endAscentTime - squat_vars.startAscentTime, 2)) + " seconds"
        issue_per_rep.append(ascend)
        print(ascend)

    #print time at bottom only if start and end time calculated
    if squat_vars.hasCalculatedBottomStart and squat_vars.hasCalculatedBottomEnd:
        bottom = "    Time at bottom: " + str(round(squat_vars.endBottomTime - squat_vars.startBottomTime, 2)) + " seconds"
        issue_per_rep.append
        print(bottom)

    #if user wanted to hold bottom position, print whether successful or not
    if squat_vars.bottomHolds:
        if squat_vars.hasCompletedBottomHold:
            bottomHold = "    Successfully held bottom position for " + str(round(squat_vars.bottomHoldTime, 2)) + " seconds"
            issue_per_rep.append(bottomHold)
            print(bottomHold)
        else:
            failBotHold = "    Failed to hold bottom position for " + str(round(squat_vars.bottomHoldTime, 2)) + " seconds"
            issue_per_rep.append(failBotHold)
            print(failBotHold)

    print("    Issues:")
    issue_per_rep.append("    Issues:")

    for i in range(len(squat_vars.repIssues)):
        issue = "      " + "Issue #" + str(i+1) + ": " + squat_vars.repIssues[i]
        issue_per_rep.append(issue)
        print(issue)

    squat_vars.overallIssues.append(issue_per_rep)
    resetVariables()