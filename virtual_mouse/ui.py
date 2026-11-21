"""On-screen HUD drawn on top of the camera feed (OpenCV only)."""

import time

import cv2

from . import config
from .gestures import Gesture, INDEX_TIP, THUMB_TIP

# BGR colors
CYAN = (255, 229, 0)
GREEN = (120, 255, 120)
ORANGE = (0, 170, 255)
RED = (80, 80, 255)
GRAY = (170, 170, 170)
WHITE = (240, 240, 240)
DARK = (25, 25, 25)

GESTURE_COLORS = {
    Gesture.IDLE: GRAY,
    Gesture.MOVE: CYAN,
    Gesture.PINCH: GREEN,
    Gesture.RIGHT_CLICK: ORANGE,
    Gesture.SCROLL: (255, 120, 200),
}

# Standard MediaPipe hand skeleton
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17),
]

LEGEND = [
    ("Index finger up", "Move cursor"),
    ("Thumb + index pinch", "Click (hold = drag)"),
    ("2 fingers together", "Right click"),
    ("2 fingers apart + move", "Scroll"),
    ("Fist / open hand", "Idle"),
]


def _overlay_rect(frame, p1, p2, alpha=0.55):
    """Semi-transparent dark rectangle."""
    layer = frame.copy()
    cv2.rectangle(layer, p1, p2, DARK, -1)
    cv2.addWeighted(layer, alpha, frame, 1 - alpha, 0, frame)


def _px(point, w, h):
    return int(point[0] * w), int(point[1] * h)


def draw_hud(frame, lm, gesture, fps, active, event=None, event_time=0.0):
    h, w = frame.shape[:2]
    color = GESTURE_COLORS[gesture] if active else RED

    # Active region: the area that maps to the full screen
    m = config.FRAME_MARGIN
    cv2.rectangle(frame, (int(m * w), int(m * h)), (int((1 - m) * w), int((1 - m) * h)),
                  CYAN, 1)

    # Hand skeleton + cursor marker
    if lm is not None:
        for a, b in HAND_CONNECTIONS:
            cv2.line(frame, _px(lm[a], w, h), _px(lm[b], w, h), WHITE, 1)
        for point in lm:
            cv2.circle(frame, _px(point, w, h), 3, color, -1)
        tip = _px(lm[INDEX_TIP], w, h)
        cv2.circle(frame, tip, 12, color, 2)
        if gesture is Gesture.PINCH:
            cv2.line(frame, tip, _px(lm[THUMB_TIP], w, h), GREEN, 3)

    # Status panel
    _overlay_rect(frame, (10, 10), (250, 92))
    cv2.putText(frame, "VIRTUAL MOUSE", (20, 34), cv2.FONT_HERSHEY_SIMPLEX, 0.6, CYAN, 2)
    status = "ACTIVE" if active else "PAUSED"
    cv2.putText(frame, status, (20, 58), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)
    cv2.putText(frame, f"FPS {fps:4.0f}", (150, 58), cv2.FONT_HERSHEY_SIMPLEX, 0.55, WHITE, 1)
    cv2.putText(frame, f"Mode: {gesture.value}", (20, 82), cv2.FONT_HERSHEY_SIMPLEX, 0.55,
                color, 1)

    # Last event flash (visible for 0.8 s)
    if event and time.time() - event_time < 0.8:
        cv2.putText(frame, event, (w // 2 - 80, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, GREEN, 2)

    # Gesture legend
    box_h = 20 * len(LEGEND) + 14
    _overlay_rect(frame, (10, h - box_h - 24), (370, h - 24))
    for i, (gesture_text, action_text) in enumerate(LEGEND):
        y = h - box_h - 24 + 22 + i * 20
        cv2.putText(frame, gesture_text, (18, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, WHITE, 1)
        cv2.putText(frame, action_text, (220, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, CYAN, 1)

    cv2.putText(frame, "[P] pause   [Q] quit", (10, h - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.45,
                GRAY, 1)
    return frame
