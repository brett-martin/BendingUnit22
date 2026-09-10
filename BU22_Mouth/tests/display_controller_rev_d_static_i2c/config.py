"""Rev D configuration for the half-scale static Mouth I2C test."""

import board

I2C_SCL = board.RX
I2C_SDA = board.TX
ADDRESS = board.A3
BUFFER_ENABLE = board.MOSI
CHANNEL_PINS = (
    (board.D8, board.D9),
    (board.D6, board.D7),
    (board.D4, board.D5),
    (board.D2, board.D3),
    (board.A0, board.SCK),
    (board.A2, board.A1),
)

# CH6 and CH5 render the left and center tiles. The right-tile pattern is
# duplicated on CH1 through CH4 so each of those paths can be tested directly.
LEFT_MOUTH_CHANNEL = 5
CENTER_MOUTH_CHANNEL = 4
RIGHT_PATTERN_CHANNELS = (0, 1, 2, 3)
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
