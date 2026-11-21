"""Gesture recognition from 21 hand landmarks.

Pure Python logic with no MediaPipe, OpenCV or PyAutoGUI dependency,
so it can be unit-tested without a camera.

Landmarks are a list of 21 (x, y) tuples, normalized to 0..1 (MediaPipe Hands format).
"""

from enum import Enum
from math import hypot

from . import config

# MediaPipe hand landmark indices
WRIST = 0
THUMB_TIP = 4
INDEX_TIP = 8
MIDDLE_MCP = 9
MIDDLE_TIP = 12

FINGER_TIPS = (8, 12, 16, 20)   # index, middle, ring, pinky
FINGER_PIPS = (6, 10, 14, 18)


class Gesture(Enum):
    IDLE = "IDLE"
    MOVE = "MOVE"
    PINCH = "CLICK / DRAG"
    RIGHT_CLICK = "RIGHT CLICK"
    SCROLL = "SCROLL"


def distance(a, b):
    return hypot(a[0] - b[0], a[1] - b[1])


def hand_size(lm):
    """Wrist to middle-finger base. Used to make distances scale-independent."""
    return max(distance(lm[WRIST], lm[MIDDLE_MCP]), 1e-6)


def fingers_up(lm):
    """[index, middle, ring, pinky] -> True if the finger is extended (hand upright)."""
    return [lm[tip][1] < lm[pip][1] for tip, pip in zip(FINGER_TIPS, FINGER_PIPS)]


def pinch_ratio(lm):
    return distance(lm[THUMB_TIP], lm[INDEX_TIP]) / hand_size(lm)


def two_finger_ratio(lm):
    return distance(lm[INDEX_TIP], lm[MIDDLE_TIP]) / hand_size(lm)


def classify(lm):
    """Return the Gesture for one frame of landmarks."""
    if pinch_ratio(lm) < config.PINCH_RATIO:
        return Gesture.PINCH

    index, middle, ring, pinky = fingers_up(lm)

    if index and middle and not ring and not pinky:
        if two_finger_ratio(lm) < config.TWO_FINGER_CLOSE_RATIO:
            return Gesture.RIGHT_CLICK
        return Gesture.SCROLL

    if index and not middle and not ring and not pinky:
        return Gesture.MOVE

    return Gesture.IDLE


class GestureStabilizer:
    """Only switch gesture after it has been seen for N consecutive frames."""

    def __init__(self, frames=None):
        self.frames = frames or config.STABLE_FRAMES
        self.stable = Gesture.IDLE
        self._candidate = Gesture.IDLE
        self._count = 0

    def update(self, gesture):
        if gesture == self.stable:
            self._candidate, self._count = gesture, 0
        elif gesture == self._candidate:
            self._count += 1
            if self._count >= self.frames:
                self.stable, self._count = gesture, 0
        else:
            self._candidate, self._count = gesture, 1
            if self.frames <= 1:
                self.stable, self._count = gesture, 0
        return self.stable
