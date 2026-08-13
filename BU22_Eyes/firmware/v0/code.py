"""BU-22 Eyes firmware v0: expressions, animations, interruption, and status."""

import time
import adafruit_dotstar
import board
import i2ctarget
import config
import content

SHOW_NORMAL = 0x10
SHOW_EXPRESSION = 0x11
PLAY_ANIMATION = 0x12
STOP = 0x14
SET_OFF = 0x15
PLAY_VISOR_DOWN = 0x16
PLAY_VISOR_UP = 0x17

MAGIC = 0x22
MODULE_EYES = 1
DISPLAY_NORMAL = 0
DISPLAY_EXPRESSION = 1
DISPLAY_ANIMATION = 2
DISPLAY_OFF = 6
DISPLAY_ERROR = 9
ACTIVITY_IDLE = 0
ACTIVITY_RUNNING = 1
ACTIVITY_COMPLETE = 2
ERROR_NONE = 0
ERROR_BAD_LENGTH = 2
ERROR_UNKNOWN_CONTENT = 4
CATEGORY_NONE = 0
CATEGORY_EXPRESSION = 1
CATEGORY_ANIMATION = 2
BLACK = (0, 0, 0)


def log(*values):
    if config.ACTION_LOGGING:
        print(*values)


def make_channels():
    return tuple(
        adafruit_dotstar.DotStar(clock, data, config.PIXELS_PER_CHANNEL,
                                brightness=config.GLOBAL_BRIGHTNESS,
                                auto_write=False)
        for clock, data in config.CHANNEL_PINS
    )


def show(channels):
    for channel in channels:
        channel.show()


def clear(channels):
    for channel in channels:
        channel.fill(BLACK)
    show(channels)


def color(intensity):
    return tuple(component * intensity // 255 for component in config.EYE_COLOR)


def set_logical_pixel(channels, column, row, value):
    if config.ROTATE_DISPLAY_180:
        column = len(channels) - 1 - column
        row = config.PIXELS_PER_CHANNEL - 1 - row
    channels[column][row] = value


def expression(channels, expression_id):
    frame = content.EXPRESSIONS[expression_id]
    for eye_start in (0, 3):
        for row in range(4):
            for column in range(3):
                source_column = column
                # Angry eyelids slope inward toward the bridge of the visor.
                # The stored source matches the right eye; mirror it for left.
                if eye_start == 0 and expression_id in (
                    content.ANGRY_1,
                    content.ANGRY_2,
                ):
                    source_column = 2 - column
                set_logical_pixel(
                    channels,
                    eye_start + column,
                    row,
                    color(frame[row][source_column]),
                )
    show(channels)


channels = make_channels()
clear(channels)
target = i2ctarget.I2CTarget(board.SCL, board.SDA, (config.I2C_ADDRESS,))

display_state = DISPLAY_OFF
activity_state = ACTIVITY_IDLE
active_tag = 0
last_command = SET_OFF
active_content_id = 0
error_code = ERROR_NONE
missing_category = CATEGORY_NONE
missing_id = 0
animation_steps = None
animation_index = 0
next_step_at = None
last_contact = time.monotonic()
standalone_fallback = False
visor_direction = 0
visor_row = 0
visor_step_seconds = 0.1


def set_missing(category, content_id):
    global display_state, activity_state, error_code, missing_category, missing_id
    global animation_steps, next_step_at
    global active_content_id
    display_state = DISPLAY_ERROR
    activity_state = ACTIVITY_IDLE
    error_code = ERROR_UNKNOWN_CONTENT
    missing_category = category
    missing_id = content_id
    active_content_id = content_id
    animation_steps = None
    next_step_at = None
    # Visible development error: alternating red/black columns.
    for index, channel in enumerate(channels):
        channel.fill((255, 0, 0) if index % 2 == 0 else BLACK)
    show(channels)
    log("ERROR CONTENT_NOT_FOUND category=", category, "id=", content_id)


def start_animation(animation_id, now):
    global animation_steps, animation_index, next_step_at
    global display_state, activity_state, active_content_id
    animation_steps = content.ANIMATIONS[animation_id]
    animation_index = 0
    display_state = DISPLAY_ANIMATION
    activity_state = ACTIVITY_RUNNING
    active_content_id = animation_id
    step_id, duration_ms = animation_steps[0]
    clear(channels) if step_id is None else expression(channels, step_id)
    next_step_at = now + duration_ms / 1000
    log("START ANIMATION", content.ANIMATION_NAMES[animation_id],
        "id=", animation_id)


def accept(payload, now):
    global display_state, activity_state, active_tag, last_command
    global active_content_id, error_code, missing_category, missing_id
    global animation_steps, next_step_at
    global standalone_fallback
    global visor_direction, visor_row, visor_step_seconds
    command = payload[0]
    last_command = command
    error_code = ERROR_NONE
    missing_category = CATEGORY_NONE
    missing_id = 0
    animation_steps = None
    next_step_at = None
    visor_direction = 0
    standalone_fallback = False

    if command in (SHOW_NORMAL, STOP):
        if len(payload) != 2:
            error_code = ERROR_BAD_LENGTH
            return
        active_tag = payload[1]
        expression(channels, content.NORMAL)
        display_state = DISPLAY_NORMAL
        activity_state = ACTIVITY_COMPLETE
        active_content_id = content.NORMAL
        if command == STOP:
            log("RX STOP tag=", active_tag, "-> NORMAL")
        else:
            log("RX SHOW_NORMAL tag=", active_tag)
    elif command == SET_OFF:
        if len(payload) != 2:
            error_code = ERROR_BAD_LENGTH
            return
        active_tag = payload[1]
        clear(channels)
        display_state = DISPLAY_OFF
        activity_state = ACTIVITY_COMPLETE
        active_content_id = 0
        log("RX SET_OFF tag=", active_tag, "-> OFF")
    elif command == SHOW_EXPRESSION:
        if len(payload) != 4:
            error_code = ERROR_BAD_LENGTH
            return
        active_tag = payload[1]
        content_id = (payload[2] << 8) | payload[3]
        if content_id not in content.EXPRESSIONS:
            set_missing(CATEGORY_EXPRESSION, content_id)
            return
        expression(channels, content_id)
        display_state = DISPLAY_EXPRESSION
        activity_state = ACTIVITY_COMPLETE
        active_content_id = content_id
        log("RX SHOW_EXPRESSION tag=", active_tag,
            "name=", content.EXPRESSION_NAMES[content_id], "id=", content_id)
    elif command == PLAY_ANIMATION:
        if len(payload) != 4:
            error_code = ERROR_BAD_LENGTH
            return
        active_tag = payload[1]
        content_id = (payload[2] << 8) | payload[3]
        if content_id not in content.ANIMATIONS:
            set_missing(CATEGORY_ANIMATION, content_id)
            return
        log("RX PLAY_ANIMATION tag=", active_tag,
            "name=", content.ANIMATION_NAMES[content_id], "id=", content_id)
        start_animation(content_id, now)
    elif command in (PLAY_VISOR_DOWN, PLAY_VISOR_UP):
        if len(payload) != 4:
            error_code = ERROR_BAD_LENGTH
            return
        active_tag = payload[1]
        step_ms = (payload[2] << 8) | payload[3]
        visor_step_seconds = (step_ms if step_ms else 100) / 1000
        activity_state = ACTIVITY_RUNNING
        display_state = DISPLAY_ANIMATION
        active_content_id = 0
        if command == PLAY_VISOR_DOWN:
            visor_direction = 1
            visor_row = 0
            log("RX PLAY_VISOR_DOWN tag=", active_tag,
                "step_ms=", step_ms if step_ms else 100)
        else:
            clear(channels)
            visor_direction = -1
            visor_row = config.PIXELS_PER_CHANNEL - 1
            log("RX PLAY_VISOR_UP tag=", active_tag,
                "step_ms=", step_ms if step_ms else 100)
        next_step_at = now
    else:
        error_code = 1


def status_bytes():
    # Keep this at the proven 20-byte target-read size. On an unknown content
    # error, active_content_id is the missing ID and last_command identifies
    # whether it was an expression or animation request.
    return bytes((MAGIC, 0, 1, MODULE_EYES, 0, 1, 3, display_state,
                  activity_state, active_tag, last_command, error_code,
                  active_content_id >> 8, active_content_id & 255,
                  128, 128, 0, config.I2C_ADDRESS, 0, 0))


while True:
    now = time.monotonic()
    try:
        request = target.request(timeout=0.01)
    except OSError as error:
        if error.args and error.args[0] == 116:
            request = None
        else:
            raise
    if request:
        last_contact = now
        with request:
            if request.is_read:
                response = status_bytes()
                request.write(response)
                log("TX STATUS state=", display_state,
                    "activity=", activity_state, "tag=", active_tag,
                    "error=", error_code, "content_id=", active_content_id)
            else:
                payload = request.read()
                if payload:
                    accept(payload, now)

    if animation_steps is not None and now >= next_step_at:
        animation_index += 1
        if animation_index >= len(animation_steps):
            expression(channels, content.NORMAL)
            display_state = DISPLAY_NORMAL
            animation_steps = None
            next_step_at = None
            activity_state = ACTIVITY_COMPLETE
            log("COMPLETE ANIMATION tag=", active_tag, "-> NORMAL")
        else:
            step_id, duration_ms = animation_steps[animation_index]
            clear(channels) if step_id is None else expression(channels, step_id)
            if duration_ms == 0:
                animation_index = len(animation_steps)
            else:
                next_step_at = now + duration_ms / 1000

    if visor_direction and now >= next_step_at:
        normal_frame = content.EXPRESSIONS[content.NORMAL]
        for eye_start in (0, 3):
            for column in range(3):
                if visor_direction > 0:
                    value = BLACK
                else:
                    value = color(normal_frame[visor_row][column])
                set_logical_pixel(
                    channels,
                    eye_start + column,
                    visor_row,
                    value,
                )
        show(channels)

        if visor_direction > 0:
            visor_row += 1
            finished = visor_row >= config.PIXELS_PER_CHANNEL
        else:
            visor_row -= 1
            finished = visor_row < 0

        if finished:
            display_state = DISPLAY_OFF if visor_direction > 0 else DISPLAY_NORMAL
            activity_state = ACTIVITY_COMPLETE
            log("COMPLETE VISOR tag=", active_tag,
                "->", "OFF" if visor_direction > 0 else "NORMAL")
            visor_direction = 0
            next_step_at = None
        else:
            next_step_at = now + visor_step_seconds

    if not standalone_fallback and now - last_contact >= config.COMMS_TIMEOUT_SECONDS:
        expression(channels, content.NORMAL)
        display_state = DISPLAY_NORMAL
        activity_state = ACTIVITY_IDLE
        animation_steps = None
        visor_direction = 0
        next_step_at = None
        standalone_fallback = True
        log("BRAIN COMMS LOST -> STANDALONE NORMAL")

    time.sleep(0.001)
