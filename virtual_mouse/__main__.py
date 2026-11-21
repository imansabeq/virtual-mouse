"""Run with:  python -m virtual_mouse"""

import time

import cv2
import pyautogui

from . import config
from .gestures import Gesture, GestureStabilizer, classify
from .hand_tracker import HandTracker
from .mouse_controller import MouseController
from .ui import draw_hud

WINDOW = "Virtual Mouse"


def main():
    cap = cv2.VideoCapture(config.CAMERA_INDEX)
    if not cap.isOpened():
        raise SystemExit("Could not open the camera. Check config.CAMERA_INDEX.")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)

    tracker = HandTracker()
    controller = MouseController()
    stabilizer = GestureStabilizer()

    active = True
    last_event, last_event_time = None, 0.0
    fps, prev_time = 0.0, time.time()

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            frame = cv2.flip(frame, 1)  # mirror view so movement feels natural

            lm = tracker.process(frame)
            gesture = stabilizer.update(classify(lm) if lm else Gesture.IDLE)

            if active:
                event = controller.update(gesture, lm)
                if event:
                    last_event, last_event_time = event, time.time()

            now = time.time()
            fps = 0.9 * fps + 0.1 * (1 / max(now - prev_time, 1e-6))
            prev_time = now

            draw_hud(frame, lm, gesture, fps, active, last_event, last_event_time)
            cv2.imshow(WINDOW, frame)

            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break
            if key == ord("p"):
                active = not active
                controller.release_all()
    except pyautogui.FailSafeException:
        print("Fail-safe triggered (mouse moved to a screen corner). Exiting.")
    finally:
        controller.release_all()
        tracker.close()
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
