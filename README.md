<h1 align="center">🖱️ Virtual Mouse</h1>

<p align="center">
  Control your computer's mouse with hand gestures using a webcam, OpenCV and MediaPipe.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9--3.12-blue?logo=python\&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/OpenCV-5C3EE8?logo=opencv\&logoColor=white" alt="OpenCV">
  <img src="https://img.shields.io/badge/MediaPipe-0097A7?logo=google\&logoColor=white" alt="MediaPipe">
  <img src="https://img.shields.io/badge/PyAutoGUI-333333" alt="PyAutoGUI">
</p>
<img width="1394" height="411" alt="demo" src="https://github.com/user-attachments/assets/46e13ef5-2b39-4ca9-a235-0bc3129b6805" />
</p>

\---

## 📑 Table of Contents

* [Overview](#-overview)
* [Features](#-features)
* [Gestures](#-gestures)
* [How It Works](#-how-it-works)
* [Project Structure](#-project-structure)
* [Getting Started](#-getting-started)
* [Configuration](#️-configuration)
* [Tests](#-tests)
* [Limitations](#-limitations)

\---

## 📌 Overview

The app reads your webcam, detects one hand with **MediaPipe Hands** (21 landmarks), recognizes a small set of gestures, and turns them into real mouse actions with **PyAutoGUI**. A heads-up display (HUD) drawn with OpenCV shows the hand skeleton, the active region, the current mode, and a gesture guide.

## ✨ Features

* 🎯 Cursor control with the index finger, with smoothing for steady movement
* 👆 Left click, double click, and drag and drop using a pinch
* 🖱️ Right click and scrolling with two fingers
* 📏 Gestures are measured relative to hand size, so they work at different distances from the camera
* 🧠 Gesture stabilizer that ignores single-frame flicker
* 🖥️ HUD with FPS, current mode, last action and an on-screen gesture legend
* ⏸️ Pause/resume key and a fail-safe: moving the mouse to a screen corner stops the app
* ✅ Unit tests for the gesture logic, the mouse controller and the UI (no camera needed)

## 🤚 Gestures

|Gesture|Action|
|-|-|
|☝️ Index finger up (other fingers down)|Move the cursor|
|🤏 Pinch thumb and index, then release|Click (two quick pinches = double click)|
|🤏 Pinch and **hold**|Drag, release to drop|
|✌️ Index + middle together|Right click|
|✌️ Index + middle apart, move hand up/down|Scroll|
|✊ Fist / open hand|Idle (nothing happens)|

Keyboard: **P** pause/resume, **Q** or **Esc** quit.

## ⚙️ How It Works

```
Webcam frame ─► MediaPipe Hands ─► 21 landmarks ─► Gesture classifier ─► Stabilizer
                                                                            │
          HUD overlay (OpenCV) ◄─────────────── Mouse controller (PyAutoGUI) ◄┘
```

1. **Tracking:** `hand\_tracker.py` returns the 21 normalized landmarks of the first hand.
2. **Classification:** `gestures.py` checks which fingers are up (tip above the joint) and the thumb-index and index-middle distances divided by the hand size.
3. **Stabilizing:** a gesture only counts after it is seen for a few frames in a row.
4. **Control:** `mouse\_controller.py` maps the index fingertip from an *active region* of the frame to the full screen, smooths it with an exponential moving average, and triggers clicks, drags and scrolls.
5. **UI:** `ui.py` draws everything on top of the mirrored camera feed.

## 📂 Project Structure

```
virtual-mouse/
├── virtual\_mouse/
│   ├── \_\_main\_\_.py          # Entry point (python -m virtual\_mouse)
│   ├── config.py            # All tunable settings
│   ├── hand\_tracker.py      # MediaPipe Hands wrapper
│   ├── gestures.py          # Gesture recognition (pure Python)
│   ├── mouse\_controller.py  # Gestures -> mouse actions
│   └── ui.py                # HUD overlay
├── tests/                   # Unit tests
├── requirements.txt
└── README.md
```

## 🚀 Getting Started

```bash
# 1. Clone
git clone https://github.com/imansabeq/virtual-mouse.git
cd virtual-mouse

# 2. (Recommended) create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\\Scripts\\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run
python -m virtual\_mouse
```

> MediaPipe is pinned to `0.10.14` because newer versions removed the `mp.solutions` API used here. Use Python 3.9 to 3.12.

**Platform notes**

* **macOS:** allow your terminal/IDE to use the camera and the Accessibility (mouse control) permission.
* **Linux:** PyAutoGUI needs an X11 session (it does not work on pure Wayland).

## 🛠️ Configuration

Everything is in `virtual\_mouse/config.py`:

|Setting|What it does|
|-|-|
|`CAMERA\_INDEX`|Which camera to use (try 1 if 0 doesn't work)|
|`FRAME\_MARGIN`|Size of the margin around the active region|
|`SMOOTHING`|Higher = smoother but slower cursor|
|`PINCH\_RATIO`|How close the thumb and index must be to count as a pinch|
|`CLICK\_MAX\_HOLD`|Pinch shorter than this = click, longer = drag|
|`SCROLL\_GAIN`|Scroll speed|

## ✅ Tests

```bash
python -m unittest discover -v
```

The tests use synthetic hand landmarks and a fake PyAutoGUI, so they run without a camera or a screen.

## ⚠️ Limitations

* Tracks one hand and assumes the hand is roughly upright.
* Needs decent lighting and a plain-ish background for stable detection.
* Scroll speed is platform dependent, so adjust `SCROLL\_GAIN` to your system.

## 🛠️ Tech Stack

Python · OpenCV · MediaPipe · PyAutoGUI · NumPy

