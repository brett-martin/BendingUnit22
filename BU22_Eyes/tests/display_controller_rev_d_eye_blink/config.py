"""Rev D 9x16 eye-tile blink-test configuration."""

import board


# Exact Rev D PCB mapping. Each tuple is (clock, data).
CHANNEL_PINS = (
    (board.D8, board.D9),
    (board.D6, board.D7),
    (board.D4, board.D5),
    (board.D2, board.D3),
    (board.A0, board.SCK),
    (board.A2, board.A1),
)

BUFFER_ENABLE = board.MOSI

MODULE_WIDTH = 9
MODULE_HEIGHT = 16
PIXELS_PER_CHANNEL = MODULE_WIDTH * MODULE_HEIGHT

SAFE_START_SECONDS = 5
GLOBAL_BRIGHTNESS = 0.03
TARGET_FPS = 10
OPEN_SECONDS = 3.0
CLOSED_HOLD_FRAMES = 2
