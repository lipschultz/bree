# Bree

A library for automating GUI interactions:

* Use image recognition to find objects on the screen
* Use OCR to find text
* Control the mouse and keyboard

Bree is like [SikuliX](https://github.com/RaiMan/SikuliX1), except:

1. it doesn't rely on Jython
2. it doesn't provide a friendly IDE for developing scripts
3. it has a different API

## Installation

1. This package depends on the following, which may have non-Python dependencies that you'll need to install first:
    - [PyAutoGUI](https://pyautogui.readthedocs.io/en/latest/install.html)
    - [Python Tesseract](https://github.com/madmaze/pytesseract#installation)
2. Run `poetry install`
