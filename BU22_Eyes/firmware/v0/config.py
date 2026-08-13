"""KB2040 and six-channel breadboard configuration for Eyes firmware v0."""

import board

I2C_ADDRESS = 0x30
CHANNEL_PINS = (
    (board.D3, board.D2), (board.D5, board.D4),
    (board.D7, board.D6), (board.D9, board.D8),
    (board.A0, board.D10), (board.A2, board.A1),
)
PIXELS_PER_CHANNEL = 4
GLOBAL_BRIGHTNESS = 0.08
EYE_COLOR = (255, 70, 0)
COMMS_TIMEOUT_SECONDS = 5.0

# The current six-strand breadboard is physically mounted 180 degrees from the
# logical orientation used when authoring expressions and animations.
ROTATE_DISPLAY_180 = True

# Development visibility: semantic actions and state changes only. No frame,
# row, or pixel-level logging. Set False when quiet output is preferred.
ACTION_LOGGING = True
