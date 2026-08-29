"""Rev D scan-only I2C target configuration."""

import board


# Rev D routes I2C to the KB2040 UART-labeled pins.
I2C_SCL = board.RX
I2C_SDA = board.TX

BUFFER_ENABLE = board.MOSI  # Keep low: AHCT outputs remain fail-dark.
ADDRESS = board.A3

EYES_ADDRESS = 0x30
MOUTH_ADDRESS = 0x31
SPARE_ADDRESS = 0x32
DEVELOPMENT_ADDRESS = 0x33

# Midpoints between the nominal ADC values produced by the 10k pull-up and
# selectable 10k/20k pull-downs. Startup prints the raw value for bench audit.
DEVELOPMENT_MOUTH_THRESHOLD = 29_500
MOUTH_SPARE_THRESHOLD = 38_200
SPARE_EYES_THRESHOLD = 54_600
