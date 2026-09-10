"""Rev D configuration for the half-scale static Eyes I2C test."""

import board

I2C_SCL = board.RX
I2C_SDA = board.TX
ADDRESS = board.A3
BUFFER_ENABLE = board.MOSI

# Exact corrected Rev D mapping. Each tuple is (clock, data).
CHANNEL_PINS = (
    (board.D8, board.D9),
    (board.D6, board.D7),
    (board.D4, board.D5),
    (board.D2, board.D3),
    (board.A0, board.SCK),
    (board.A2, board.A1),
)

# Physical half-scale installation.
LEFT_EYE_CHANNEL = 5   # CH6
RIGHT_EYE_CHANNEL = 4  # CH5
MODULE_WIDTH = 9
MODULE_HEIGHT = 16
PIXELS_PER_CHANNEL = MODULE_WIDTH * MODULE_HEIGHT
GLOBAL_BRIGHTNESS = 0.05
EYE_COLOR = (255, 110, 0)

EYES_ADDRESS = 0x30
MOUTH_ADDRESS = 0x31
SPARE_ADDRESS = 0x32
DEVELOPMENT_ADDRESS = 0x33
BOTH_A0_THRESHOLD = 29_500
A0_A1_THRESHOLD = 38_200
A1_OPEN_THRESHOLD = 54_600
