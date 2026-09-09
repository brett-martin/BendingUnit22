"""Half-scale three-tile static Mouth renderer controlled over I2C."""

import time
import analogio
import digitalio
import i2ctarget
import adafruit_dotstar

import config

VERSION = "0.1"
SHOW_NORMAL = 0x10
SHOW_EXPRESSION = 0x11
SET_OFF = 0x15
NORMAL = 0
OPEN = 1
MAGIC = 0x22
MODULE_MOUTH = 2
DISPLAY_NORMAL = 0
DISPLAY_EXPRESSION = 1
DISPLAY_OFF = 6
ACTIVITY_COMPLETE = 2
ERROR_NONE = 0
ERROR_UNKNOWN_COMMAND = 1
ERROR_BAD_LENGTH = 2
ERROR_UNKNOWN_CONTENT = 4
BLACK = (0, 0, 0)
TOTAL_WIDTH = config.MODULE_WIDTH * len(config.MOUTH_CHANNELS_LEFT_TO_RIGHT)


def read_address_adc(pin, samples=16):
    total = 0
    for _ in range(samples):
        total += pin.value
        time.sleep(0.005)
    return total // samples


def decode_address(value):
    if value < config.BOTH_A0_THRESHOLD:
        return config.SPARE_ADDRESS, "Spare"
    if value < config.A0_A1_THRESHOLD:
        return config.MOUTH_ADDRESS, "Mouth"
    if value < config.A1_OPEN_THRESHOLD:
        return config.EYES_ADDRESS, "Eyes"
    return config.DEVELOPMENT_ADDRESS, "Development"


def serpentine_index(column, row):
    physical_row = row if column % 2 == 0 else config.MODULE_HEIGHT - 1 - row
    return column * config.MODULE_HEIGHT + physical_row


def is_lit(column, row, expression_id):
    # Repeat three lit columns and one dark separator across the full display.
    # The logical grid deliberately crosses physical tile boundaries.
    if column % 4 == 3:
        return False
    if expression_id == NORMAL:
        # Eleven rows: 3 lit, 1 dark, 3 lit, 1 dark, 3 lit.
        return row % 4 != 3

    # Open mouth: the two dark horizontal lines bow apart near the center.
    distance = abs(column - (TOTAL_WIDTH - 1) / 2)
    curve = 2 if distance <= 1 else (1 if distance <= 4 else 0)
    upper = 3 - curve
    lower = 7 + curve
    return row not in (upper, lower)


def render(expression_id):
    for tile in tiles:
        tile.fill(BLACK)
    for column in range(TOTAL_WIDTH):
        tile_index = column // config.MODULE_WIDTH
        local_column = column % config.MODULE_WIDTH
        for row in range(config.MODULE_HEIGHT):
            if is_lit(column, row, expression_id):
                tiles[tile_index][serpentine_index(local_column, row)] = config.MOUTH_COLOR
    for tile in tiles:
        tile.show()


def clear():
    for tile in tiles:
        tile.fill(BLACK)
        tile.show()


print("\nBU-22 REV D STATIC MOUTH I2C", VERSION)
enable = digitalio.DigitalInOut(config.BUFFER_ENABLE)
enable.switch_to_output(value=False)

address_pin = analogio.AnalogIn(config.ADDRESS)
address_raw = read_address_adc(address_pin)
address, role = decode_address(address_raw)
address_pin.deinit()
print("Address ADC raw:", address_raw)
print("Selected role/address:", role, "0x%02X" % address)

unused_outputs = []
for channel_index, pins in enumerate(config.CHANNEL_PINS):
    if channel_index in config.MOUTH_CHANNELS_LEFT_TO_RIGHT:
        continue
    for pin in pins:
        output = digitalio.DigitalInOut(pin)
        output.switch_to_output(value=False)
        unused_outputs.append(output)

tiles = []
for channel_index in config.MOUTH_CHANNELS_LEFT_TO_RIGHT:
    clock, data = config.CHANNEL_PINS[channel_index]
    tiles.append(adafruit_dotstar.DotStar(
        clock, data, config.PIXELS_PER_CHANNEL,
        brightness=config.GLOBAL_BRIGHTNESS, auto_write=False
    ))
clear()
enable.value = True
render(NORMAL)
print("Mouth: NORMAL on CH6/CH5/CH4 left-to-right")

target = i2ctarget.I2CTarget(config.I2C_SCL, config.I2C_SDA, (address,))
display_state = DISPLAY_NORMAL
active_tag = 0
last_command = SHOW_NORMAL
active_content_id = NORMAL
error_code = ERROR_NONE


def status_bytes():
    return bytes((MAGIC, 0, 1, MODULE_MOUTH, 0, 1, 3, display_state,
                  ACTIVITY_COMPLETE, active_tag, last_command, error_code,
                  active_content_id >> 8, active_content_id & 255,
                  128, 128, 0, address, 0, 0))


def accept(payload):
    global display_state, active_tag, last_command, active_content_id, error_code
    if not payload:
        return
    last_command = payload[0]
    error_code = ERROR_NONE
    if last_command in (SHOW_NORMAL, SET_OFF):
        if len(payload) != 2:
            error_code = ERROR_BAD_LENGTH
            return
        active_tag = payload[1]
        active_content_id = NORMAL
        if last_command == SET_OFF:
            clear()
            display_state = DISPLAY_OFF
            print("Mouth: OFF")
        else:
            render(NORMAL)
            display_state = DISPLAY_NORMAL
            print("Mouth: NORMAL")
    elif last_command == SHOW_EXPRESSION:
        if len(payload) != 4:
            error_code = ERROR_BAD_LENGTH
            return
        active_tag = payload[1]
        active_content_id = (payload[2] << 8) | payload[3]
        if active_content_id not in (NORMAL, OPEN):
            error_code = ERROR_UNKNOWN_CONTENT
            return
        render(active_content_id)
        display_state = DISPLAY_EXPRESSION
        print("Mouth:", "OPEN" if active_content_id == OPEN else "NORMAL")
    else:
        error_code = ERROR_UNKNOWN_COMMAND


while True:
    try:
        request = target.request(timeout=0.05)
    except OSError as error:
        request = None if error.args and error.args[0] == 116 else None
    if request is not None:
        with request:
            if request.is_read:
                request.write(status_bytes())
            else:
                accept(bytes(request.read()))
    time.sleep(0.001)
