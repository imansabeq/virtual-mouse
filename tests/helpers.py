"""Build synthetic hand landmarks for tests (hand upright, wrist at the bottom)."""


def make_hand(index=False, middle=False, ring=False, pinky=False,
              pinch=False, two_gap=0.10):
    """21 (x, y) landmarks. Palm size (wrist to middle base) = 0.30."""
    lm = [(0.5, 0.5)] * 21
    lm = list(lm)
    lm[0] = (0.50, 0.90)    # wrist
    lm[9] = (0.50, 0.60)    # middle finger base  -> hand size 0.30

    def finger(tip, pip, x, up):
        lm[pip] = (x, 0.55)
        lm[tip] = (x, 0.35) if up else (x, 0.62)

    finger(8, 6, 0.44, index)
    finger(12, 10, 0.44 + two_gap, middle)
    finger(16, 14, 0.62, ring)
    finger(20, 18, 0.68, pinky)

    lm[4] = (0.30, 0.65)    # thumb tip, far from the index tip
    if pinch:
        lm[4] = (lm[8][0] + 0.01, lm[8][1] + 0.01)
    return lm
