import unittest

import numpy as np

from virtual_mouse.gestures import Gesture
from virtual_mouse.ui import draw_hud
from tests.helpers import make_hand


class TestHud(unittest.TestCase):
    def test_draws_for_every_gesture(self):
        for g in Gesture:
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            out = draw_hud(frame, make_hand(index=True), g, 30.0, True, "CLICK", 1e18)
            self.assertEqual(out.shape, (480, 640, 3))
            self.assertTrue(out.any())

    def test_handles_no_hand_and_paused(self):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        draw_hud(frame, None, Gesture.IDLE, 0.0, False)


if __name__ == "__main__":
    unittest.main()
