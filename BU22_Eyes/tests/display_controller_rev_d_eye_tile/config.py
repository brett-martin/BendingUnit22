"""Rev D 9x16 eye-tile visual-test configuration."""

import board


# Exact Rev D PCB mapping. Each tuple is (clock, data).
CHANNEL_PINS = (
    (board.D3, board.D2),
    (board.D5, board.D4),
    (board.D7, board.D6),
    (board.D9, board.D8),
    (board.A0, board.SCK),
    (board.A2, board.A1),
)

BUFFER_ENABLE = board.MOSI

MODULE_WIDTH = 9
MODULE_HEIGHT = 16
PIXELS_PER_CHANNEL = MODULE_WIDTH * MODULE_HEIGHT

SAFE_START_SECONDS = 5
GLOBAL_BRIGHTNESS = 0.03
CHASE_SECONDS = 0.0
SWEEP_SECONDS = 0.10
ALL_ON_SECONDS = 1.0
BLACKOUT_SECONDS = 1.0

TARGET_FPS = 10
PERFORMANCE_FRAMES = 30
