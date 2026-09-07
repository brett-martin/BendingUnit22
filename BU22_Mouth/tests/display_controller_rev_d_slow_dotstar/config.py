"""Rev D slow valid-DotStar mouth-tile test configuration."""

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
PIXELS_PER_CHANNEL = 55

SAFE_START_SECONDS = 5
BIT_HALF_PERIOD_SECONDS = 0.0005
GLOBAL_BRIGHTNESS = 4
COLOR_HOLD_SECONDS = 2.0
