"""Rev D configuration for the half-scale static Mouth I2C test."""

import board

I2C_SCL = board.RX
I2C_SDA = board.TX
ADDRESS = board.A3
BUFFER_ENABLE = board.MOSI
CHANNEL_PINS = (
    (board.D2, board.D3),
    (board.D4, board.D5),
    (board.D6, board.D7),
    (board.D8, board.D9),
    (board.A0, board.SCK),
    (board.A2, board.A1),
)

# The installed tiles run opposite numeric order: CH6, CH5, CH4 left-to-right.
MOUTH_CHANNELS_LEFT_TO_RIGHT = (5, 4, 3)
MODULE_WIDTH = 5
MODULE_HEIGHT = 11
PIXELS_PER_CHANNEL = MODULE_WIDTH * MODULE_HEIGHT
GLOBAL_BRIGHTNESS = 0.05
MOUTH_COLOR = (255, 110, 0)

EYES_ADDRESS = 0x30
MOUTH_ADDRESS = 0x31
SPARE_ADDRESS = 0x32
DEVELOPMENT_ADDRESS = 0x33
BOTH_A0_THRESHOLD = 29_500
A0_A1_THRESHOLD = 38_200
A1_OPEN_THRESHOLD = 54_600
