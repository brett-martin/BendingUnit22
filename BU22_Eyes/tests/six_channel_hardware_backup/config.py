"""Wiring and conservative limits for the BU-22 Eyes LED breadboard test."""

import board

# Six independent four-pixel strings. Each tuple is (clock, data).
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
FRAME_RATE = 10

# Inputs remain high-impedance while external display power is connected.
SAFE_START_DELAY_SECONDS = 20
