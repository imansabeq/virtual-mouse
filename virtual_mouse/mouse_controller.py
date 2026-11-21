"""Turns gestures into real mouse actions using PyAutoGUI."""

import time

import pyautogui

from . import config
from .gestures import Gesture, INDEX_TIP, THUMB_TIP

pyautogui.PAUSE = 0  # no built-in delay between actions
pyautogui.FAILSAFE = True  # slam the mouse into a screen corner to abort


class MouseController:
    def __init__(self):
        self.screen_w, self.screen_h = pyautogui.size()
        self._cursor = None            # smoothed cursor position
        self._pinch_start = None
        self._dragging = False
        self._last_click = float("-inf")
        self._last_right_click = float("-inf")
        self._prev_gesture = Gesture.IDLE
        self._prev_scroll_y = None

    # -- helpers -----------------------------------------------------------
    def _map_to_screen(self, point):
        """Map a normalized camera point (active region) to screen pixels."""
        m = config.FRAME_MARGIN
        nx = min(max((point[0] - m) / (1 - 2 * m), 0.0), 1.0)
        ny = min(max((point[1] - m) / (1 - 2 * m), 0.0), 1.0)
        # Stay 5px away from the corners so PyAutoGUI's fail-safe isn't triggered by accident
        x = 5 + nx * (self.screen_w - 11)
        y = 5 + ny * (self.screen_h - 11)
        return x, y

    def _move_cursor(self, point):
        tx, ty = self._map_to_screen(point)
        if self._cursor is None:
            self._cursor = (tx, ty)
        else:
            cx, cy = self._cursor
            self._cursor = (cx + (tx - cx) / config.SMOOTHING,
                            cy + (ty - cy) / config.SMOOTHING)
        pyautogui.moveTo(int(self._cursor[0]), int(self._cursor[1]))

    def _finish_pinch(self, now):
        """Called when a pinch ends: either a click or the end of a drag."""
        event = None
        if self._pinch_start is not None:
            if self._dragging:
                pyautogui.mouseUp()
                event = "DROP"
            elif now - self._pinch_start < config.CLICK_MAX_HOLD:
                if now - self._last_click < config.DOUBLE_CLICK_WINDOW:
                    pyautogui.doubleClick()
                    event = "DOUBLE CLICK"
                    self._last_click = float("-inf")
                else:
                    pyautogui.click()
                    event = "CLICK"
                    self._last_click = now
        self._pinch_start = None
        self._dragging = False
        return event

    # -- public API --------------------------------------------------------
    def release_all(self):
        """Safely release anything held (used when the hand is lost or the app pauses)."""
        if self._dragging:
            pyautogui.mouseUp()
        self._pinch_start = None
        self._dragging = False
        self._prev_scroll_y = None
        self._prev_gesture = Gesture.IDLE

    def update(self, gesture, lm, now=None):
        """Apply one frame. Returns a short event label ("CLICK", "SCROLL", ...) or None."""
        now = time.time() if now is None else now

        if lm is None:
            self.release_all()
            return None

        event = None

        if gesture is Gesture.PINCH:
            pinch_point = ((lm[THUMB_TIP][0] + lm[INDEX_TIP][0]) / 2,
                           (lm[THUMB_TIP][1] + lm[INDEX_TIP][1]) / 2)
            if self._pinch_start is None:
                self._pinch_start = now
            elif not self._dragging and now - self._pinch_start >= config.CLICK_MAX_HOLD:
                pyautogui.mouseDown()
                self._dragging = True
                event = "DRAG"
            if self._dragging:
                self._move_cursor(pinch_point)
        else:
            event = self._finish_pinch(now)

            if gesture is Gesture.MOVE:
                self._move_cursor(lm[INDEX_TIP])

            elif gesture is Gesture.RIGHT_CLICK:
                if (self._prev_gesture is not Gesture.RIGHT_CLICK
                        and now - self._last_right_click >= config.RIGHT_CLICK_COOLDOWN):
                    pyautogui.rightClick()
                    self._last_right_click = now
                    event = "RIGHT CLICK"

            elif gesture is Gesture.SCROLL:
                y = lm[INDEX_TIP][1]
                if self._prev_scroll_y is not None:
                    dy = y - self._prev_scroll_y
                    if abs(dy) > config.SCROLL_DEADZONE:
                        pyautogui.scroll(int(-dy * config.SCROLL_GAIN))
                        event = "SCROLL"
                self._prev_scroll_y = y

        if gesture is not Gesture.SCROLL:
            self._prev_scroll_y = None
        self._prev_gesture = gesture
        return event
