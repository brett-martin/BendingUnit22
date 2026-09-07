"""Rev D six-channel CircuitPython DotStar benchmark configuration."""

import board


# Observed functional Rev D mapping. Each tuple is (clock, data).
CHANNEL_PINS = (
    (board.D2, board.D3),
    (board.D4, board.D5),
    (board.D6, board.D7),
    (board.D8, board.D9),
    (board.A0, board.SCK),
    (board.A2, board.A1),
)

BUFFER_ENABLE = board.MOSI
PIXELS_PER_CHANNEL = 144
GLOBAL_BRIGHTNESS = 0.03
SAFE_START_SECONDS = 5
SAMPLES_PER_CHANNEL = 20
AGGREGATE_SAMPLES = 20
REPEAT_PAUSE_SECONDS = 5
