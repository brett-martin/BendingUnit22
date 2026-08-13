"""BU-22 Eyes: minimal non-blocking I2C target test.

The KB2040 owns the six SK9822 channels. The Feather Brain sends one-byte
commands over I2C. Animation timing is local and non-blocking so I2C remains
responsive while the LEDs are active.
"""

import time

import adafruit_dotstar
import board
import i2ctarget

import config


BLACK = (0, 0, 0)

COMMAND_CLEAR = 0x00
COMMAND_IDENTIFY = 0x01
COMMAND_START_LONG_PATTERN = 0x02
COMMAND_SET_BRIGHTNESS = 0x03
COMMAND_SET_CHANNEL_COLOR = 0x04
COMMAND_SET_PIXEL = 0x05
COMMAND_SET_FRAME = 0x06
COMMAND_GET_STATUS = 0x07
COMMAND_SHOW_EXPRESSION = 0x08
COMMAND_PLAY_BLINK = 0x09

IDENTITY = 0x22
TEST_VERSION = 0x01
ACTIVITY_IDLE = 0
ACTIVITY_FRAME = 1
ACTIVITY_EXPRESSION = 2
ACTIVITY_ANIMATION = 3
ERROR_NONE = 0
ERROR_BAD_LENGTH = 1
ERROR_BAD_INDEX = 2
ERROR_UNKNOWN_COMMAND = 3

current_activity = ACTIVITY_IDLE
last_command = COMMAND_CLEAR
error_flag = ERROR_NONE
status_requested = False

EXPRESSION_NORMAL = 0
EXPRESSION_LOOK_LEFT = 1
EXPRESSION_LOOK_RIGHT = 2
EXPRESSION_CLOSED = 3

# Logical display is six columns (channels) by four rows (pixels). Each nested
# tuple is one 3x4 eye, stored as four rows of three intensity values.
OPEN_EYE = (
    (70, 220, 70),
    (220, 220, 220),
    (220, 220, 220),
    (70, 220, 70),
)
CLOSED_EYE = (
    (0, 0, 0),
    (0, 0, 0),
    (180, 255, 180),
    (0, 0, 0),
)


def make_channels():
    channels = []
    for clock_pin, data_pin in config.CHANNEL_PINS:
        channels.append(
            adafruit_dotstar.DotStar(
                clock_pin,
                data_pin,
                config.PIXELS_PER_CHANNEL,
                brightness=config.PIXEL_BRIGHTNESS,
                auto_write=False,
            )
        )
    return tuple(channels)


def fill_all(channels, color):
    for channel in channels:
        channel.fill(color)
    for channel in channels:
        channel.show()


def draw_pattern_frame(channels, frame):
    for channel_index, channel in enumerate(channels):
        channel.fill(BLACK)
        pixel = (frame + channel_index) % config.PIXELS_PER_CHANNEL
        channel[pixel] = config.IDENTIFY_COLOR
    for channel in channels:
        channel.show()


def intensity_color(intensity):
    return tuple(
        (component * intensity) // 255 for component in config.EYE_COLOR
    )


def draw_expression(channels, expression_id):
    for channel in channels:
        channel.fill(BLACK)

    for eye_start in (0, 3):
        source = CLOSED_EYE if expression_id == EXPRESSION_CLOSED else OPEN_EYE
        for row in range(config.PIXELS_PER_CHANNEL):
            for eye_column in range(3):
                intensity = source[row][eye_column]
                channels[eye_start + eye_column][row] = intensity_color(intensity)

        if expression_id != EXPRESSION_CLOSED:
            pupil_column = 1
            if expression_id == EXPRESSION_LOOK_LEFT:
                pupil_column = 0
            elif expression_id == EXPRESSION_LOOK_RIGHT:
                pupil_column = 2
            channels[eye_start + pupil_column][1] = BLACK
            channels[eye_start + pupil_column][2] = BLACK

    for channel in channels:
        channel.show()


def handle_packet(channels, payload, now):
    global current_activity, last_command, error_flag, status_requested

    command = payload[0]

    if command == COMMAND_CLEAR:
        print("RX CLEAR")
        fill_all(channels, BLACK)
        current_activity = ACTIVITY_IDLE
        last_command = command
        error_flag = ERROR_NONE
        return None, None, None

    if command == COMMAND_IDENTIFY:
        print("RX IDENTIFY")
        fill_all(channels, config.IDENTIFY_COLOR)
        last_command = command
        error_flag = ERROR_NONE
        return "identify", now + config.IDENTIFY_DURATION_SECONDS, None

    if command == COMMAND_START_LONG_PATTERN:
        print("RX START LONG PATTERN")
        draw_pattern_frame(channels, 0)
        last_command = command
        error_flag = ERROR_NONE
        return "pattern", now + config.LONG_PATTERN_DURATION_SECONDS, now

    if command == COMMAND_SET_BRIGHTNESS:
        if len(payload) != 2:
            print("RX BRIGHTNESS missing value; bytes:", len(payload))
            error_flag = ERROR_BAD_LENGTH
            return None, None, None

        level = payload[1]
        brightness = level / 255.0
        print("RX BRIGHTNESS", level, "of 255")
        for channel in channels:
            channel.brightness = brightness
        fill_all(channels, config.IDENTIFY_COLOR)
        last_command = command
        error_flag = ERROR_NONE
        return None, None, None

    if command == COMMAND_SET_CHANNEL_COLOR:
        if len(payload) != 5:
            print("RX CHANNEL COLOR wrong byte count:", len(payload))
            error_flag = ERROR_BAD_LENGTH
            return None, None, None

        channel_index = payload[1]
        if channel_index >= len(channels):
            print("RX CHANNEL COLOR invalid channel:", channel_index)
            error_flag = ERROR_BAD_INDEX
            return None, None, None

        color = (payload[2], payload[3], payload[4])
        print("RX CHANNEL", channel_index + 1, "RGB", color)
        channels[channel_index].fill(color)
        channels[channel_index].show()
        last_command = command
        error_flag = ERROR_NONE
        return None, None, None

    if command == COMMAND_SET_PIXEL:
        if len(payload) != 6:
            print("RX PIXEL wrong byte count:", len(payload))
            error_flag = ERROR_BAD_LENGTH
            return None, None, None

        channel_index = payload[1]
        pixel_index = payload[2]
        if channel_index >= len(channels):
            print("RX PIXEL invalid channel:", channel_index)
            error_flag = ERROR_BAD_INDEX
            return None, None, None
        if pixel_index >= config.PIXELS_PER_CHANNEL:
            print("RX PIXEL invalid pixel:", pixel_index)
            error_flag = ERROR_BAD_INDEX
            return None, None, None

        color = (payload[3], payload[4], payload[5])
        print(
            "RX CHANNEL", channel_index + 1,
            "PIXEL", pixel_index + 1,
            "RGB", color,
        )
        channels[channel_index][pixel_index] = color
        channels[channel_index].show()
        last_command = command
        error_flag = ERROR_NONE
        return None, None, None

    if command == COMMAND_SET_FRAME:
        expected_length = 1 + (len(channels) * config.PIXELS_PER_CHANNEL)
        if len(payload) != expected_length:
            print("RX FRAME wrong byte count:", len(payload))
            error_flag = ERROR_BAD_LENGTH
            return None, None, None

        offset = 1
        for channel in channels:
            for pixel_index in range(config.PIXELS_PER_CHANNEL):
                intensity = payload[offset]
                offset += 1
                channel[pixel_index] = tuple(
                    (component * intensity) // 255
                    for component in config.FRAME_COLOR
                )

        for channel in channels:
            channel.show()
        current_activity = ACTIVITY_FRAME
        last_command = command
        error_flag = ERROR_NONE
        return None, None, None

    if command == COMMAND_GET_STATUS:
        status_requested = True
        return None, None, None

    if command == COMMAND_SHOW_EXPRESSION:
        if len(payload) != 2:
            print("RX EXPRESSION wrong byte count:", len(payload))
            error_flag = ERROR_BAD_LENGTH
            return None, None, None

        expression_id = payload[1]
        if expression_id > EXPRESSION_CLOSED:
            print("RX EXPRESSION invalid id:", expression_id)
            error_flag = ERROR_BAD_INDEX
            return None, None, None

        print("RX EXPRESSION", expression_id)
        draw_expression(channels, expression_id)
        current_activity = ACTIVITY_EXPRESSION
        last_command = command
        error_flag = ERROR_NONE
        return None, None, None

    if command == COMMAND_PLAY_BLINK:
        print("RX PLAY BLINK")
        draw_expression(channels, EXPRESSION_CLOSED)
        current_activity = ACTIVITY_ANIMATION
        last_command = command
        error_flag = ERROR_NONE
        return "blink", now + config.BLINK_CLOSED_SECONDS, None

    print("RX UNKNOWN: 0x%02X" % command)
    error_flag = ERROR_UNKNOWN_COMMAND
    return None, None, None


print("\nBU-22 Eyes: basic I2C target test")
print("Address: 0x%02X" % config.I2C_ADDRESS)

channels = make_channels()
fill_all(channels, BLACK)

target = i2ctarget.I2CTarget(board.SCL, board.SDA, (config.I2C_ADDRESS,))
active_test = None
test_ends_at = None
next_frame_at = None
pattern_frame = 0
last_contact_at = time.monotonic()
comms_lost = False

while True:
    now = time.monotonic()

    # A zero timeout can wait indefinitely on this CircuitPython build. Use a
    # short finite timeout so local animation deadlines continue to advance
    # even when the Brain is not sending a transaction.
    try:
        request = target.request(timeout=0.01)
    except OSError as error:
        # CircuitPython raises ETIMEDOUT (116) when no controller addresses us
        # before the finite request timeout. That is the expected idle state.
        if error.args and error.args[0] == 116:
            request = None
        else:
            raise
    if request:
        last_contact_at = now
        if comms_lost:
            print("BRAIN COMMS RESTORED")
            comms_lost = False
        with request:
            if request.is_read:
                response = bytes((
                    IDENTITY,
                    TEST_VERSION,
                    current_activity,
                    last_command,
                    error_flag,
                ))
                request.write(response)
                status_requested = False
                print("TX STATUS", tuple(response))
            else:
                payload = request.read()
                if payload:
                    active_test, test_ends_at, next_frame_at = handle_packet(
                        channels, payload, now
                    )
                    pattern_frame = 0

    if active_test == "pattern" and now >= next_frame_at:
        pattern_frame += 1
        draw_pattern_frame(channels, pattern_frame)
        next_frame_at = now + config.LONG_PATTERN_FRAME_SECONDS

    if active_test == "blink" and now >= test_ends_at:
        draw_expression(channels, EXPRESSION_NORMAL)
        print("BLINK complete -> NORMAL")
        active_test = None
        test_ends_at = None
        next_frame_at = None
        current_activity = ACTIVITY_EXPRESSION

    if test_ends_at is not None and now >= test_ends_at:
        print("Local test complete -> BLACK")
        fill_all(channels, BLACK)
        active_test = None
        test_ends_at = None
        next_frame_at = None

    if not comms_lost and now - last_contact_at >= config.COMMS_WATCHDOG_SECONDS:
        print("BRAIN COMMS LOST -> NORMAL")
        draw_expression(channels, EXPRESSION_NORMAL)
        active_test = None
        test_ends_at = None
        next_frame_at = None
        current_activity = ACTIVITY_EXPRESSION
        comms_lost = True

    time.sleep(0.001)
