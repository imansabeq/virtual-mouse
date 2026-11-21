import unittest

from virtual_mouse.gestures import Gesture, GestureStabilizer, classify, fingers_up
from tests.helpers import make_hand


class TestClassify(unittest.TestCase):
    def test_index_only_is_move(self):
        self.assertIs(classify(make_hand(index=True)), Gesture.MOVE)

    def test_fist_is_idle(self):
        self.assertIs(classify(make_hand()), Gesture.IDLE)

    def test_open_hand_is_idle(self):
        self.assertIs(classify(make_hand(True, True, True, True)), Gesture.IDLE)

    def test_pinch(self):
        self.assertIs(classify(make_hand(index=True, pinch=True)), Gesture.PINCH)

    def test_two_fingers_together_is_right_click(self):
        hand = make_hand(index=True, middle=True, two_gap=0.05)
        self.assertIs(classify(hand), Gesture.RIGHT_CLICK)

    def test_two_fingers_apart_is_scroll(self):
        hand = make_hand(index=True, middle=True, two_gap=0.15)
        self.assertIs(classify(hand), Gesture.SCROLL)

    def test_fingers_up_detection(self):
        self.assertEqual(fingers_up(make_hand(index=True, pinky=True)),
                         [True, False, False, True])

    def test_gesture_is_scale_independent(self):
        """Same hand shape farther from the camera gives the same gesture."""
        hand = make_hand(index=True, middle=True, two_gap=0.05)
        cx, cy, s = 0.5, 0.6, 0.5
        small = [(cx + (x - cx) * s, cy + (y - cy) * s) for x, y in hand]
        self.assertIs(classify(small), Gesture.RIGHT_CLICK)


class TestStabilizer(unittest.TestCase):
    def test_ignores_single_frame_flicker(self):
        st = GestureStabilizer(frames=3)
        for _ in range(4):
            st.update(Gesture.MOVE)
        self.assertIs(st.stable, Gesture.MOVE)
        st.update(Gesture.PINCH)   # one noisy frame
        st.update(Gesture.MOVE)
        self.assertIs(st.stable, Gesture.MOVE)

    def test_switches_after_n_frames(self):
        st = GestureStabilizer(frames=3)
        for _ in range(4):
            st.update(Gesture.MOVE)
        for _ in range(3):
            st.update(Gesture.PINCH)
        self.assertIs(st.stable, Gesture.PINCH)


if __name__ == "__main__":
    unittest.main()
