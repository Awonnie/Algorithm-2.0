import os
from dotenv import load_dotenv

load_dotenv()

'''
Robot Constants
'''
TURN_FACTOR = 1
TURN_RADIUS = 1
ROBOT_SPEED =  2 # measured as cells/seconds, in other words, it can reach X amount of cells (1 cell = 10cm) within 1 timestep

'''
Grid Constants
'''
EXPANDED_CELL = 1 # for both agent and obstacles
WIDTH = 20
HEIGHT = 20

'''
Algorithm Constants
'''
ITERATIONS = 2000
SAFE_COST = 1000 # the cost for the turn in case there is a chance that the robot is touch some obstacle
SCREENSHOT_COST = 50 # cost for the robot to take a photo when not directly in line with the image (i.e, camera is too far left/right)

'''
Image Recognition Constants
'''
MODEL_ID = "mdp_grp27/3"
CV_API_KEY = os.getenv("CV_API_KEY")