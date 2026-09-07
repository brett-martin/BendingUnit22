"""BU-22 Display Controller Rev D hardware-test configuration."""

import board


# Rev D PCB mapping. Each tuple is (clock, data).
CHANNEL_PINS = (
    (board.D2, board.D3),
    (board.D4, board.D5),
    (board.D6, board.D7),
    (board.D8, board.D9),
    (board.A0, board.SCK),
    (board.A2, board.A1),
)

BUFFER_ENABLE = board.MOSI   # High turns Q1 on and enables all AHCT outputs.
TEST_BUTTON = board.MISO     # Active low; board supplies firmware pull-up.
HEARTBEAT = board.D10        # Optional external RTC SQW input.
ADDRESS = board.A3           # Four-level address-jumper resistor network.

# Set this to the actual strip length connected to each channel.
PIXELS_PER_CHANNEL = 4

# Conservative for first power-up. Full-scale white is intentionally omitted.
NORMAL_BRIGHTNESS = 0.08
STRESS_BRIGHTNESS = 0.15
FRAME_RATE = 10

# Allows time to open a serial console or remove power if anything looks wrong.
SAFE_START_SECONDS = 5
