"""Temporary Feather RP2040 four-pixel SK9822 smoke-test profile."""

import board

# One four-pixel string. Each tuple is (clock, data).
CHANNEL_PINS = (
    (board.D13, board.D11),
)

PIXELS_PER_CHANNEL = 4
PIXEL_BRIGHTNESS = 0.08
FRAME_RATE = 10

# Inputs remain high-impedance briefly while USB power settles.
SAFE_START_DELAY_SECONDS = 5
