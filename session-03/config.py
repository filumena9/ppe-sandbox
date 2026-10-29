"""Settings for the Ternus experiment.

Everything from Ternus.py, like numbers, colours, sizes, pos... was moved here
so that the foucs in Ternus py is on the experiment, while this file focuses on 
figurations
"""

EXPERIMENT_NAME = "Ternus experiment"

#Colours (RGB)
BACKGROUND_COLOUR = (0, 0, 0)
FOREGROUND_COLOUR = (255, 255, 255)

# Size of each image
IMAGE_SIZE = (600, 300)

#offset pos for the positons of the circles and shapes
X_LEFT = -120
X_CENTER_LEFT = -40
X_CENTER_RIGHT = 40
X_RIGHT = 120
Y_ITEMS = -50


DOT_RADIUS = 20
TRIANGLE_RADIUS = 54
SQUARE_SIZE = (35, 35)

#Fixation cross
FIXATION_SIZE = (20, 20)
FIXATION_LINE_WIDTH = 4

# Time in (ms)
FIXATION_BEFORE_TRIAL_MS = 200
IMAGE_DURATION_MS = 250
INTERTRIAL_INTERVAL_MS = 500

#iteration limit for the for loop, how many times are the images shown as a pair
#on each trial
N_IMAGE_PAIRS = 3
