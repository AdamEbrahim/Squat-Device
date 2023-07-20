#--FUNCTIONS RELATED TO BOTTOM POSITION TIME--#
from Utils.config import squat_vars
import time

#function to start timer for how long in bottom position of squat
def calcBottomStart():
    squat_vars.startBottomTime = time.time()
    squat_vars.hasCalculatedBottomStart = True

def calcBottomEnd():
    squat_vars.endBottomTime = time.time()
    squat_vars.hasCalculatedBottomEnd = True

#function to check if person has held bottom position for input length of time and then do something once they have
def checkHasCompletedBottomHold():
    if time.time() - squat_vars.startBottomTime >= squat_vars.bottomHoldTime:
        print("You have completed the hold")
        squat_vars.hasCompletedBottomHold = True