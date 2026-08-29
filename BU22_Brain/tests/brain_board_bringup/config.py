"""Pin assignments for the BU-22 Brain perfboard V1."""

import board

I2C_SCL = board.SCL
I2C_SDA = board.SDA

AUDIO_TX = board.TX       # Brain TX -> Audio FX RX
AUDIO_RX = board.RX       # Brain RX <- Audio FX TX
AUDIO_ACT = board.D24     # Active low
AUDIO_RESET = board.D25   # Active low; released as an input

RTC_SQW = board.D13       # DS3231 open-drain 1 Hz output
SENSOR_SIGNAL = board.A3  # Generic sensor/VCNL4200 INT input

ANTENNA_PINS = (board.A0, board.A1, board.A2)
ANTENNA_NAMES = ("RED", "GREEN", "BLUE/SPARE")

BUTTON_PINS = (
    board.D4,
    board.D5,
    board.D6,
    board.D9,
    board.D10,
    board.D11,
    board.D12,
)

RTC_ADDRESS = 0x68
VCNL4200_ADDRESS = 0x51
EYES_ADDRESS = 0x30
MOUTH_ADDRESS = 0x31
