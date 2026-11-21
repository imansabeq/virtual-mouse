"""Thin wrapper around MediaPipe Hands."""

import cv2

from . import config


class HandTracker:
    def __init__(self):
        # Imported here so the rest of the package (and the tests) work without MediaPipe.
        import mediapipe as mp

        self._hands = mp.solutions.hands.Hands(
            max_num_hands=config.MAX_HANDS,
            min_detection_confidence=config.DETECTION_CONFIDENCE,
            min_tracking_confidence=config.TRACKING_CONFIDENCE,
        )

    def process(self, frame_bgr):
        """Return 21 normalized (x, y) landmarks of the first hand, or None."""
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        result = self._hands.process(rgb)
        if not result.multi_hand_landmarks:
            return None
        return [(p.x, p.y) for p in result.multi_hand_landmarks[0].landmark]

    def close(self):
        self._hands.close()
