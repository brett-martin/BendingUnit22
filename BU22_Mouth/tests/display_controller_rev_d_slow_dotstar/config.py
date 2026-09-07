"""Rev D slow valid-DotStar mouth-tile test configuration."""

import board


# Clock/data reversal diagnostic. CH1-CH4 are intentionally swapped from the
# documented Rev D mapping; known-good CH5-CH6 remain normal as controls.
# Each tuple is (clock, data).
CHANNEL_PINS = (
    (board.D2, board.D3),
    (board.D4, board.D5),
    (board.D6, board.D7),
    (board.D8, board.D9),
    (board.A0, board.SCK),
    (board.A2, board.A1),
)

BUFFER_ENABLE = board.MOSI
PIXELS_PER_CHANNEL = 55

SAFE_START_SECONDS = 5
BIT_HALF_PERIOD_SECONDS = 0.0005
GLOBAL_BRIGHTNESS = 4
COLOR_HOLD_SECONDS = 2.0
