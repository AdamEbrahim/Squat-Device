#--FUNCTIONS RELATED TO SINGLE REP ASCENT TIME--#
from Utils.config import squat_vars
import time

#function to check for when we start ascent
def checkForAscent(rightHipHeight):
    #calculate ascent start time based on if our hip height has been found to be increasing for at least 3 of 4 last frames. Queue
    if rightHipHeight > squat_vars.prevHipHeight and not squat_vars.hasCalculatedAscentStart:
        squat_vars.ascentQ.append(1)
        squat_vars.ascentQTotal = squat_vars.ascentQTotal - squat_vars.ascentQ.popleft() + 1 #maintain queue total
        if squat_vars.ascentQTotal == 3:
            startAscentTime = time.time()
            squat_vars.hasCalculatedAscentStart = True
        else:
            squat_vars.prevHipHeight = rightHipHeight
    elif not squat_vars.hasCalculatedAscentStart:
        squat_vars.ascentQ.append(0)
        squat_vars.ascentQTotal = squat_vars.ascentQTotal - squat_vars.ascentQ.popleft() #maintain queue total
        squat_vars.prevHipHeight = rightHipHeight

#Function to calculate end ascent time even if improper depth
def calculateAscentEnd():
    squat_vars.endAscentTime = time.time()
    squat_vars.hasCalculatedAscentEnd = True