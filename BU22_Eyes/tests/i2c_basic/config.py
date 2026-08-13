"""Hardware configuration for the BU-22 Eye Controller I2C test."""

import board


I2C_ADDRESS = 0x30

# Each tuple is (clock, data). This is the proven KB2040 breadboard mapping.
CHANNEL_PINS = (
    (board.D3, board.D2),
    (board.D5, board.D4),
    (board.D7, board.D6),
    (board.D9, board.D8),
    (board.A0, board.D10),
    (board.A2, board.A1),
)

PIXELS_PER_CHANNEL = 4
PIXEL_BRIGHTNESS = 0.08
FRAME_COLOR = (255, 70, 0)

EYE_COLOR = (255, 70, 0)
EYE_EDGE_COLOR = (100, 22, 0)
BLINK_CLOSED_SECONDS = 0.25
COMMS_WATCHDOG_SECONDS = 5.0

IDENTIFY_COLOR = (255, 70, 0)
IDENTIFY_DURATION_SECONDS = 1.0

LONG_PATTERN_DURATION_SECONDS = 6.0
LONG_PATTERN_FRAME_SECONDS = 0.2
