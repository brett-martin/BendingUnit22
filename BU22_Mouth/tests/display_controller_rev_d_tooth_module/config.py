"""Rev D 5x11 tooth-module test configuration."""

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

MODULE_WIDTH = 5
MODULE_HEIGHT = 11
PIXELS_PER_CHANNEL = MODULE_WIDTH * MODULE_HEIGHT

SAFE_START_SECONDS = 5
GLOBAL_BRIGHTNESS = 0.03
CHASE_SECONDS = 0.06
SWEEP_SECONDS = 0.35
ALL_ON_SECONDS = 1.5
BLACKOUT_SECONDS = 1.0
