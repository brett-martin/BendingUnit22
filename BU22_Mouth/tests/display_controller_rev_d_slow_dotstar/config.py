"""Rev D slow valid-DotStar mouth-tile test configuration."""

import board


# Observed functional Rev D mapping. Each tuple is (clock, data). CH1-CH4 are
# reversed from the original schematic labels; see the Rev D errata.
CHANNEL_PINS = (
    (board.D8, board.D9),
    (board.D6, board.D7),
    (board.D4, board.D5),
    (board.D2, board.D3),
    (board.A0, board.SCK),
    (board.A2, board.A1),
)

BUFFER_ENABLE = board.MOSI
PIXELS_PER_CHANNEL = 55

SAFE_START_SECONDS = 5
BIT_HALF_PERIOD_SECONDS = 0.0005
GLOBAL_BRIGHTNESS = 4
COLOR_HOLD_SECONDS = 2.0
