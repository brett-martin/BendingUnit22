"""Display Controller Rev D output-exerciser configuration."""

import board


# Exact Rev D PCB mapping. Each tuple is (clock, data).
CHANNEL_PINS = (
    (board.D3, board.D2),
    (board.D5, board.D4),
    (board.D7, board.D6),
    (board.D9, board.D8),
    (board.A0, board.SCK),
    (board.A2, board.A1),
)

BUFFER_ENABLE = board.MOSI  # High turns Q1 on and enables the AHCT outputs.
SAFE_START_SECONDS = 5
PHASE_SECONDS = 2.0
