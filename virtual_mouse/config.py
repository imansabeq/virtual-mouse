"""Tunable settings. Adjust these to fit your camera and your hand."""

# Camera
CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Active region: the part of the camera frame that maps to the whole screen.
# 0.15 means a 15% margin on every side, so you never have to reach the frame edges.
FRAME_MARGIN = 0.15

# Cursor smoothing: higher = smoother but slower to react.
SMOOTHING = 5.0

# Gesture thresholds (distances are divided by hand size, so distance from the camera doesn't matter)
PINCH_RATIO = 0.30            # thumb tip to index tip below this = pinch
TWO_FINGER_CLOSE_RATIO = 0.35  # index tip to middle tip below this = fingers together

# Gesture timing (seconds)
CLICK_MAX_HOLD = 0.35         # a pinch shorter than this is a click, longer starts a drag
DOUBLE_CLICK_WINDOW = 0.40    # two clicks within this time = double click
RIGHT_CLICK_COOLDOWN = 0.80
STABLE_FRAMES = 3             # frames a gesture must hold before it counts (reduces flicker)

# Scrolling
SCROLL_GAIN = 3000            # bigger = faster scrolling
SCROLL_DEADZONE = 0.004       # ignore tiny vertical movements

# MediaPipe
MAX_HANDS = 1
DETECTION_CONFIDENCE = 0.7
TRACKING_CONFIDENCE = 0.6
