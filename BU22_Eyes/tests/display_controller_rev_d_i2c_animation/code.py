"""Stored-frame I2C animation receiver for half-size Rev D displays."""

import time

import adafruit_dotstar
import board
import digitalio
import i2ctarget
import supervisor

import config


supervisor.runtime.autoreload = False

SHOW_NORMAL = 0x10
SHOW_EXPRESSION = 0x11
SET_OFF = 0x15
MAGIC = 0x22
DISPLAY_NORMAL = 0
DISPLAY_EXPRESSION = 1
DISPLAY_OFF = 6
ACTIVITY_COMPLETE = 2
ERROR_NONE = 0
ERROR_UNKNOWN_COMMAND = 1
ERROR_BAD_LENGTH = 2
ERROR_UNKNOWN_CONTENT = 4
BLACK = (0, 0, 0)
EYE_CENTER = 0
EYE_LEFT = 2
EYE_RIGHT = 3

WIDTH = config.MODULE_WIDTH * config.MODULE_COUNT
HEIGHT = config.MODULE_HEIGHT
PIXEL_COUNT = WIDTH * HEIGHT


def pixel_index(x, y):
    module = x // config.MODULE_WIDTH
    local_x = x % config.MODULE_WIDTH
    module_base = module * config.MODULE_WIDTH * config.MODULE_HEIGHT
    local_y = y if local_x % 2 == 0 else config.MODULE_HEIGHT - 1 - y
    return module_base + (local_x * config.MODULE_HEIGHT) + local_y


def eye_outline_lit(x, y):
    if x >= 8 or y in (0, 15):
        return False
    if y in (1, 14):
        return 2 <= x <= 5
    if y in (2, 3, 12, 13):
        return 1 <= x <= 6
    return True


def render_eyes(content_id):
    pupil_x = {EYE_LEFT: 1, EYE_CENTER: 3, EYE_RIGHT: 5}[content_id]
    pixels.fill(BLACK)
    for module in range(config.MODULE_COUNT):
        base_x = module * config.MODULE_WIDTH
        for local_x in range(config.MODULE_WIDTH):
            for y in range(HEIGHT):
                pupil = pupil_x <= local_x < pupil_x + 2 and 6 <= y <= 9
                if eye_outline_lit(local_x, y) and not pupil:
                    pixels[pixel_index(base_x + local_x, y)] = config.COLOR
    pixels.show()


def mouth_lit(x, y, level):
    if x % 4 == 3:
        return False
    distance = abs(x - ((WIDTH - 1) / 2))
    reach = max(0, level - int(distance // 2))
    upper = max(0, 3 - reach)
    lower = min(HEIGHT - 1, 7 + reach)
    return y not in (upper, lower)


def render_mouth(level):
    pixels.fill(BLACK)
    for x in range(WIDTH):
        for y in range(HEIGHT):
            if mouth_lit(x, y, level):
                pixels[pixel_index(x, y)] = config.COLOR
    pixels.show()


def render(content_id):
    if config.MODULE_TYPE == 1:
        render_eyes(content_id)
    else:
        render_mouth(content_id)


def clear():
    pixels.fill(BLACK)
    pixels.show()


print("\nBU-22 STORED-FRAME I2C ANIMATION RECEIVER")
print("Controller:", config.CONTROLLER_NAME)
print("Address: 0x%02X" % config.I2C_ADDRESS)
print("Display:", WIDTH, "x", HEIGHT, "pixels=", PIXEL_COUNT)
print("Output: CH5 clock + CH6 data, hardware SPI1 at 4 MHz")

enable = digitalio.DigitalInOut(board.MOSI)
enable.switch_to_output(value=False)
pixels = adafruit_dotstar.DotStar(
    board.A0,
    board.A1,
    PIXEL_COUNT,
    brightness=config.BRIGHTNESS,
    auto_write=False,
    baudrate=4000000,
)
clear()
time.sleep(2)
enable.value = True
render(config.NORMAL_CONTENT_ID)

target = i2ctarget.I2CTarget(board.RX, board.TX, (config.I2C_ADDRESS,))
display_state = DISPLAY_NORMAL
active_tag = 0
last_command = SHOW_NORMAL
active_content_id = config.NORMAL_CONTENT_ID
error_code = ERROR_NONE


def status_bytes():
    return bytes((MAGIC, 0, 1, config.MODULE_TYPE, 0, 1, 3, display_state,
                  ACTIVITY_COMPLETE, active_tag, last_command, error_code,
                  active_content_id >> 8, active_content_id & 255,
                  128, 128, 0, config.I2C_ADDRESS, 0, 0))


def valid_content(content_id):
    if config.MODULE_TYPE == 1:
        return content_id in (EYE_CENTER, EYE_LEFT, EYE_RIGHT)
    return 0 <= content_id <= 4


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
        active_content_id = config.NORMAL_CONTENT_ID
        if last_command == SET_OFF:
            clear()
            display_state = DISPLAY_OFF
        else:
            render(active_content_id)
            display_state = DISPLAY_NORMAL
    elif last_command == SHOW_EXPRESSION:
        if len(payload) != 4:
            error_code = ERROR_BAD_LENGTH
            return
        active_tag = payload[1]
        content_id = (payload[2] << 8) | payload[3]
        if not valid_content(content_id):
            error_code = ERROR_UNKNOWN_CONTENT
            return
        active_content_id = content_id
        render(content_id)
        display_state = DISPLAY_EXPRESSION
    else:
        error_code = ERROR_UNKNOWN_COMMAND


while True:
    try:
        request = target.request(timeout=0.02)
    except OSError:
        request = None
    if request is not None:
        with request:
            if request.is_read:
                request.write(status_bytes())
            else:
                accept(bytes(request.read()))
    time.sleep(0.001)
