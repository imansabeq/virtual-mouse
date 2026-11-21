import importlib
import sys
import types
import unittest

from virtual_mouse import config
from virtual_mouse.gestures import Gesture
from tests.helpers import make_hand


class FakePyAutoGUI(types.ModuleType):
    """Records calls instead of touching the real mouse."""

    class FailSafeException(Exception):
        pass

    def __init__(self):
        super().__init__("pyautogui")
        self.calls = []
        self.PAUSE = 0
        self.FAILSAFE = True

    def size(self):
        return (1920, 1080)

    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        return lambda *a, **k: self.calls.append((name, a))


class TestMouseController(unittest.TestCase):
    def setUp(self):
        self.fake = FakePyAutoGUI()
        self._saved = sys.modules.get("pyautogui")
        sys.modules["pyautogui"] = self.fake
        import virtual_mouse.mouse_controller as mc
        importlib.reload(mc)
        self.ctl = mc.MouseController()

    def tearDown(self):
        if self._saved is None:
            sys.modules.pop("pyautogui", None)
        else:
            sys.modules["pyautogui"] = self._saved

    def names(self):
        return [c[0] for c in self.fake.calls]

    def test_move_moves_cursor_inside_screen(self):
        self.ctl.update(Gesture.MOVE, make_hand(index=True), now=0)
        self.assertEqual(self.names(), ["moveTo"])
        x, y = self.fake.calls[0][1]
        self.assertTrue(0 < x < 1920 and 0 < y < 1080)

    def test_short_pinch_is_a_click(self):
        hand = make_hand(index=True, pinch=True)
        self.ctl.update(Gesture.PINCH, hand, now=0.0)
        self.ctl.update(Gesture.PINCH, hand, now=0.1)
        event = self.ctl.update(Gesture.MOVE, make_hand(index=True), now=0.2)
        self.assertEqual(event, "CLICK")
        self.assertIn("click", self.names())

    def test_two_quick_pinches_make_a_double_click(self):
        hand = make_hand(index=True, pinch=True)
        move = make_hand(index=True)
        self.ctl.update(Gesture.PINCH, hand, now=0.0)
        self.ctl.update(Gesture.MOVE, move, now=0.1)      # first click
        self.ctl.update(Gesture.PINCH, hand, now=0.2)
        event = self.ctl.update(Gesture.MOVE, move, now=0.3)
        self.assertEqual(event, "DOUBLE CLICK")
        self.assertIn("doubleClick", self.names())

    def test_long_pinch_drags_and_drops(self):
        hand = make_hand(index=True, pinch=True)
        self.ctl.update(Gesture.PINCH, hand, now=0.0)
        ev = self.ctl.update(Gesture.PINCH, hand, now=config.CLICK_MAX_HOLD + 0.05)
        self.assertEqual(ev, "DRAG")
        self.assertIn("mouseDown", self.names())
        ev = self.ctl.update(Gesture.MOVE, make_hand(index=True), now=1.0)
        self.assertEqual(ev, "DROP")
        self.assertIn("mouseUp", self.names())
        self.assertNotIn("click", self.names())

    def test_right_click_fires_once_per_gesture(self):
        hand = make_hand(index=True, middle=True, two_gap=0.05)
        for t in (0.0, 0.05, 0.1, 0.15):
            self.ctl.update(Gesture.RIGHT_CLICK, hand, now=t)
        self.assertEqual(self.names().count("rightClick"), 1)

    def test_scroll_follows_vertical_movement(self):
        a = make_hand(index=True, middle=True, two_gap=0.15)
        b = [(x, y - 0.03) if i in (8, 12) else (x, y) for i, (x, y) in enumerate(a)]  # hand up
        self.ctl.update(Gesture.SCROLL, a, now=0)
        self.ctl.update(Gesture.SCROLL, b, now=0.05)
        scrolls = [c for c in self.fake.calls if c[0] == "scroll"]
        self.assertEqual(len(scrolls), 1)
        self.assertGreater(scrolls[0][1][0], 0)   # positive = scroll up

    def test_losing_the_hand_releases_a_drag(self):
        hand = make_hand(index=True, pinch=True)
        self.ctl.update(Gesture.PINCH, hand, now=0.0)
        self.ctl.update(Gesture.PINCH, hand, now=1.0)    # drag started
        self.ctl.update(Gesture.IDLE, None, now=1.1)     # hand disappears
        self.assertIn("mouseUp", self.names())


if __name__ == "__main__":
    unittest.main()
