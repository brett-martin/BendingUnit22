"""BU-22 Brain stable development-runtime configuration."""

import board

LOGGING = False
MIRROR_I2C = False

I2C_SCL = board.SCL
I2C_SDA = board.SDA
I2C_FREQUENCY = 100_000
I2C_TRANSACTION_GAP = 0.02
STARTUP_SCAN_DELAY_SECONDS = 10.0
MODE_ANNOUNCEMENT_SECONDS = 3.0
SETTINGS_TIMEOUT_SECONDS = 60.0

EYES_ADDRESS = 0x30
MOUTH_ADDRESS = 0x31
RTC_ADDRESS = 0x68
VCNL4200_ADDRESS = 0x51

RTC_SQW = board.D13
ANTENNA_PINS = (board.A0, board.A1, board.A2)
ANTENNA_NAMES = ("RED", "GREEN", "BLUE")

# Bench-verified logical mapping for the installed four-button harness.
BUTTON_PINS = (board.D5, board.D9, board.D6, board.D10)
BUTTON_NAMES = ("MODE", "ENTER", "UP", "DOWN")
MODE_BUTTON = 0
ENTER_BUTTON = 1
UP_BUTTON = 2
DOWN_BUTTON = 3
