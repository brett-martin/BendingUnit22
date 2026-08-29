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
    board.D10,  # Mode: observed as the prior logical Button 5 input
    board.D9,   # Enter: observed as the prior logical Mode input
    board.D6,   # Up: observed as the prior logical Enter input
    board.D5,   # Down: observed as the prior logical Up input
    board.D4,   # Function not yet identified at the bench
    board.D11,
    board.D12,
)
BUTTON_NAMES = ("MODE", "ENTER", "UP", "DOWN", "BUTTON 5", "BUTTON 6", "BUTTON 7")

RTC_ADDRESS = 0x68
VCNL4200_ADDRESS = 0x51
EYES_ADDRESS = 0x30
MOUTH_ADDRESS = 0x31
