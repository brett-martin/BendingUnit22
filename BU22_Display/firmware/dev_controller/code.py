"""Stable Rev D Eyes/Mouth development-controller runtime."""

import time

import adafruit_dotstar
import analogio
import digitalio
import i2ctarget
import random
import supervisor

import catalog
import config
from common.display_model import (
    DisplayGeometry,
    LocalModeState,
    animation_sequence,
    blank_frame,
    clock_frame,
    local_mode_label,
    retimed_frame_index,
    scrolling_frame_at,
    scrolling_frame_count,
    text_frame,
)
from common import protocol


supervisor.runtime.autoreload = False

BLACK = (0, 0, 0)
TEST_COLORS = (
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    config.BENDER_COLOR,
    BLACK,
)


def log(*values):
    if config.LOGGING:
        print(*values)


def read_address_adc(pin, samples=16):
    total = 0
    for _ in range(samples):
        total += pin.value
        time.sleep(0.005)
    return total // samples


def decode_role(value):
    if value < config.BOTH_A0_THRESHOLD:
        return config.SPARE_ADDRESS, None
    if value < config.A0_A1_THRESHOLD:
        return config.MOUTH_ADDRESS, protocol.MODULE_MOUTH
    if value < config.A1_OPEN_THRESHOLD:
        return config.EYES_ADDRESS, protocol.MODULE_EYES
    return config.DEVELOPMENT_ADDRESS, None


def geometry_for(module_type):
    if module_type == protocol.MODULE_EYES:
        return DisplayGeometry(
            config.EYES_MODULE_COUNT,
            config.EYES_MODULE_WIDTH,
            config.EYES_MODULE_HEIGHT,
        )
    return DisplayGeometry(
        config.MOUTH_MODULE_COUNT,
        config.MOUTH_MODULE_WIDTH,
        config.MOUTH_MODULE_HEIGHT,
    )


def show_frame(frame):
    pixels.fill(BLACK)
    for y in range(geometry.height):
        row = y * geometry.width
        for x in range(geometry.width):
            if frame[row + x]:
                pixels[geometry.pixel_index(x, y)] = config.BENDER_COLOR
    pixels.show()


def show_color(color):
    pixels.fill(color)
    pixels.show()


def show_packed_frame(frame):
    pixels.fill(BLACK)
    for logical in range(geometry.pixel_count):
        if frame[logical >> 3] & (1 << (7 - (logical & 7))):
            x = logical % geometry.width
            y = logical // geometry.width
            pixels[geometry.pixel_index(x, y)] = config.BENDER_COLOR
    pixels.show()


def show_scrolling_text(text, seconds):
    frame_count = scrolling_frame_count(geometry, text)
    count = max(1, int(seconds * config.STARTUP_TEXT_FPS))
    started = time.monotonic()
    for step in range(count):
        index = min(frame_count - 1, step * frame_count // count)
        show_frame(scrolling_frame_at(geometry, text, index))
        deadline = started + ((step + 1) / config.STARTUP_TEXT_FPS)
        remaining = deadline - time.monotonic()
        if remaining > 0:
            time.sleep(remaining)


def start_message(text, duration=config.MODE_ANNOUNCEMENT_SECONDS,
                  mode_announcement=False):
    global message_text, message_index, next_message_frame
    global message_duration, message_is_mode_announcement
    message_text = text
    message_index = 0
    message_duration = duration
    message_is_mode_announcement = mode_announcement
    next_message_frame = time.monotonic()


def update_message(now):
    global message_text, message_index, next_message_frame, display_state
    global message_is_mode_announcement
    if message_text is None or now < next_message_frame:
        return
    frame_count = scrolling_frame_count(geometry, message_text)
    output_count = max(1, int(message_duration * config.MESSAGE_TEXT_FPS))
    frame_index = min(
        frame_count - 1,
        message_index * frame_count
        // (output_count * config.MESSAGE_SCROLL_SLOWDOWN),
    )
    show_frame(scrolling_frame_at(geometry, message_text, frame_index))
    message_index += 1
    next_message_frame = now + 1.0 / config.MESSAGE_TEXT_FPS
    if message_index >= output_count:
        was_mode_announcement = message_is_mode_announcement
        message_text = None
        message_index = 0
        message_is_mode_announcement = False
        if was_mode_announcement:
            render_current_mode(now)
        else:
            show_frame(blank_frame(geometry))
            display_state = protocol.DISPLAY_OFF


def eye_lit(x, y, pupil_x=3):
    local_x = x % config.EYES_MODULE_WIDTH
    if local_x >= 8 or y < 2 or y >= 14:
        return False
    if y in (1, 14):
        outline = 2 <= local_x <= 5
    elif y in (2, 3, 12, 13):
        outline = 1 <= local_x <= 6
    else:
        outline = True
    pupil = pupil_x <= local_x < pupil_x + 2 and 6 <= y <= 9
    return outline and not pupil


def mouth_lit(x, y, level=0):
    if x % 4 == 3:
        return False
    distance = abs(x - ((geometry.width - 1) / 2))
    reach = max(0, level - int(distance // 2))
    upper = max(0, 3 - reach)
    lower = min(geometry.height - 1, 7 + reach)
    return y not in (upper, lower)


def bender_frame(content_id=0):
    frame = blank_frame(geometry)
    for y in range(geometry.height):
        for x in range(geometry.width):
            if module_type == protocol.MODULE_EYES:
                pupil_x = {2: 1, 3: 5}.get(content_id, 3)
                lit = eye_lit(x, y, pupil_x)
            else:
                lit = mouth_lit(x, y, min(4, content_id))
            if lit:
                frame[y * geometry.width + x] = 1
    return frame


def render_current_mode(now=None):
    global display_state
    if modes.mode == protocol.LOCAL_TARGET:
        show_frame(blank_frame(geometry))
        display_state = protocol.DISPLAY_OFF
    elif modes.mode == protocol.LOCAL_TEST:
        update_test(time.monotonic() if now is None else now, force=True)
        display_state = protocol.DISPLAY_LOCAL_TEST
    else:
        show_packed_frame(catalog_frames[catalog_normal_frame])
        display_state = protocol.DISPLAY_NORMAL


def start_animation(animation_id, now, local=False):
    global animation_frames, animation_index, next_animation_frame
    global active_content_id, display_state, activity_state
    animation_frames = animation_sequence(catalog_animations[animation_id])
    animation_index = 0
    next_animation_frame = now + 1.0 / catalog.DEFAULT_ANIMATION_FPS
    active_content_id = animation_id
    display_state = protocol.DISPLAY_ANIMATION
    activity_state = protocol.ACTIVITY_RUNNING
    show_packed_frame(catalog_frames[animation_frames[0]])
    log("LOCAL" if local else "RX", "PLAY ANIMATION", animation_id,
        catalog_animations[animation_id][0])


def update_animation(now):
    global animation_frames, animation_index, next_animation_frame
    global display_state, activity_state, next_bender_animation
    if animation_frames is None or now < next_animation_frame:
        return
    animation_index += 1
    if animation_index < len(animation_frames):
        show_packed_frame(catalog_frames[animation_frames[animation_index]])
        next_animation_frame += 1.0 / catalog.DEFAULT_ANIMATION_FPS
        return
    animation_frames = None
    animation_index = 0
    next_animation_frame = None
    show_packed_frame(catalog_frames[catalog_normal_frame])
    display_state = protocol.DISPLAY_NORMAL
    activity_state = protocol.ACTIVITY_COMPLETE
    if modes.mode == protocol.LOCAL_BENDER:
        next_bender_animation = now + random.uniform(
            config.MIN_BENDER_PAUSE_SECONDS,
            config.MAX_BENDER_PAUSE_SECONDS,
        )


def update_bender(now):
    global next_bender_animation, last_bender_animation
    if animation_frames is not None or now < next_bender_animation:
        return
    choices = tuple(catalog_animations)
    animation_id = random.choice(choices)
    if len(choices) > 1:
        while animation_id == last_bender_animation:
            animation_id = random.choice(choices)
    last_bender_animation = animation_id
    start_animation(animation_id, now, local=True)


def start_timed_animation(animation_id, entry_ms, hold_ms, exit_ms, now):
    global timed_entry, timed_exit, timed_phase, timed_phase_started
    global timed_durations, next_timed_frame, timed_last_frame
    global active_content_id, display_state, activity_state
    animation = catalog_animations[animation_id]
    timed_entry = animation[1]
    timed_exit = (animation[2] if animation[3] == "custom"
                  else tuple(reversed(timed_entry)))
    timed_phase = 0
    timed_phase_started = now
    timed_durations = (entry_ms, hold_ms, exit_ms)
    next_timed_frame = now
    timed_last_frame = None
    active_content_id = animation_id
    display_state = protocol.DISPLAY_ANIMATION
    activity_state = protocol.ACTIVITY_RUNNING
    log("RX PLAY TIMED", animation_id, animation[0],
        entry_ms, hold_ms, exit_ms)


def complete_timed_animation():
    global timed_phase, next_timed_frame, timed_last_frame
    global display_state, activity_state
    timed_phase = None
    next_timed_frame = None
    timed_last_frame = None
    show_packed_frame(catalog_frames[catalog_normal_frame])
    display_state = protocol.DISPLAY_NORMAL
    activity_state = protocol.ACTIVITY_COMPLETE


def update_timed_animation(now):
    global timed_phase, timed_phase_started, next_timed_frame, timed_last_frame
    while timed_phase is not None:
        duration = timed_durations[timed_phase]
        elapsed_ms = int((now - timed_phase_started) * 1000)
        if timed_phase == 1:
            if elapsed_ms < duration:
                return
        else:
            sequence = timed_entry if timed_phase == 0 else timed_exit
            if now >= next_timed_frame or elapsed_ms >= duration:
                index = retimed_frame_index(elapsed_ms, duration, len(sequence))
                frame_id = sequence[index]
                if frame_id != timed_last_frame:
                    show_packed_frame(catalog_frames[frame_id])
                    timed_last_frame = frame_id
                next_timed_frame = now + 1.0 / catalog.MAX_DISPLAY_FPS
            if elapsed_ms < duration:
                return
        timed_phase_started += duration / 1000
        timed_phase += 1
        next_timed_frame = now
        timed_last_frame = None
        if timed_phase >= 3:
            complete_timed_animation()
            return


def update_test(now, force=False):
    global test_step, next_test_frame
    if not force and now < next_test_frame:
        return
    frame = blank_frame(geometry)
    horizontal_end = geometry.height
    vertical_end = horizontal_end + geometry.width
    chase_frames = geometry.pixel_count
    chase_end = vertical_end + chase_frames
    solid_end = chase_end + len(TEST_COLORS) * config.FRAME_RATE
    position = test_step % solid_end
    if position < horizontal_end:
        y = position
        for x in range(geometry.width):
            frame[y * geometry.width + x] = 1
        show_frame(frame)
    elif position < vertical_end:
        x = position - horizontal_end
        for y in range(geometry.height):
            frame[y * geometry.width + x] = 1
        show_frame(frame)
    elif position < chase_end:
        logical = position - vertical_end
        x = (logical // geometry.height) % geometry.width
        local_y = logical % geometry.height
        module_x = x % geometry.module_width
        y = local_y if module_x % 2 == 0 else geometry.height - 1 - local_y
        frame[y * geometry.width + x] = 1
        show_frame(frame)
    else:
        color_index = (position - chase_end) // config.FRAME_RATE
        show_color(TEST_COLORS[color_index])
    test_step = (test_step + 1) % solid_end
    next_test_frame = now + 1.0 / config.FRAME_RATE


def change_mode():
    global test_step, next_test_frame, error_code, lifecycle_state, message_text
    global animation_frames, next_animation_frame, activity_state
    global next_bender_animation
    global timed_phase, next_timed_frame
    modes.advance()
    message_text = None
    animation_frames = None
    next_animation_frame = None
    timed_phase = None
    next_timed_frame = None
    activity_state = protocol.ACTIVITY_IDLE
    next_bender_animation = time.monotonic()
    test_step = 0
    next_test_frame = time.monotonic()
    error_code = protocol.ERROR_NONE
    lifecycle_state = (
        protocol.LIFECYCLE_LOCAL_TEST
        if modes.mode == protocol.LOCAL_TEST
        else protocol.LIFECYCLE_STANDALONE_NORMAL
        if modes.mode == protocol.LOCAL_BENDER
        else protocol.LIFECYCLE_WAITING_FOR_BRAIN
    )
    log("MODE", local_mode_label(modes.mode))
    start_message(local_mode_label(modes.mode), mode_announcement=True)


def status_bytes():
    flags = 0
    if activity_state == protocol.ACTIVITY_COMPLETE:
        flags |= protocol.STATUS_FLAG_ACTIVITY_COMPLETE
    if brain_seen:
        flags |= protocol.STATUS_FLAG_BRAIN_SEEN
    if modes.mode == protocol.LOCAL_TEST:
        flags |= protocol.STATUS_FLAG_LOCAL_TEST
    elif modes.mode == protocol.LOCAL_BENDER:
        flags |= protocol.STATUS_FLAG_LOCAL_BENDER
    return bytes((
        protocol.MAGIC, protocol.PROTOCOL_MAJOR, protocol.PROTOCOL_MINOR,
        module_type, 0, 2, lifecycle_state, display_state,
        activity_state, active_tag, last_command, error_code,
        active_content_id >> 8, active_content_id & 0xFF,
        int(config.BRIGHTNESS * 255), int(config.BRIGHTNESS * 255), flags,
        address, 0, 0,
    ))


def accept(payload):
    global active_tag, last_command, error_code, active_content_id
    global display_state, lifecycle_state, clock_value, clock_flags, brain_seen
    global message_text, animation_frames, next_animation_frame, activity_state
    global timed_phase, next_timed_frame
    if not payload:
        return
    brain_seen = True
    command = payload[0]
    if config.MIRROR_I2C:
        log("I2C RX", tuple(payload))
    if not modes.accepts_visual_commands:
        error_code = protocol.ERROR_LOCAL_MODE_BUSY
        return
    message_text = None
    animation_frames = None
    next_animation_frame = None
    timed_phase = None
    next_timed_frame = None
    error_code = protocol.ERROR_NONE
    if command in (protocol.SHOW_NORMAL, protocol.SET_OFF):
        if len(payload) != 2:
            error_code = protocol.ERROR_BAD_LENGTH
            return
        active_tag = payload[1]
        last_command = command
        active_content_id = 0
        if command == protocol.SET_OFF:
            show_frame(blank_frame(geometry))
            display_state = protocol.DISPLAY_OFF
        else:
            show_packed_frame(catalog_frames[catalog_normal_frame])
            display_state = protocol.DISPLAY_NORMAL
        activity_state = protocol.ACTIVITY_COMPLETE
    elif command == protocol.SHOW_EXPRESSION:
        if len(payload) != 4:
            error_code = protocol.ERROR_BAD_LENGTH
            return
        content_id = (payload[2] << 8) | payload[3]
        if module_type == protocol.MODULE_EYES and content_id not in (0, 2, 3):
            error_code = protocol.ERROR_UNKNOWN_CONTENT
            return
        if module_type == protocol.MODULE_MOUTH and not 0 <= content_id <= 4:
            error_code = protocol.ERROR_UNKNOWN_CONTENT
            return
        active_tag = payload[1]
        last_command = command
        active_content_id = content_id
        show_frame(bender_frame(content_id))
        display_state = protocol.DISPLAY_EXPRESSION
        activity_state = protocol.ACTIVITY_COMPLETE
    elif command == protocol.PLAY_ANIMATION:
        if len(payload) != 4:
            error_code = protocol.ERROR_BAD_LENGTH
            return
        content_id = (payload[2] << 8) | payload[3]
        if content_id not in catalog_animations:
            error_code = protocol.ERROR_UNKNOWN_CONTENT
            return
        active_tag = payload[1]
        last_command = command
        start_animation(content_id, time.monotonic())
    elif command == protocol.PLAY_ANIMATION_TIMED:
        if len(payload) != 10:
            error_code = protocol.ERROR_BAD_LENGTH
            return
        content_id = (payload[2] << 8) | payload[3]
        if content_id not in catalog_animations:
            error_code = protocol.ERROR_UNKNOWN_CONTENT
            return
        entry_ms = (payload[4] << 8) | payload[5]
        hold_ms = (payload[6] << 8) | payload[7]
        exit_ms = (payload[8] << 8) | payload[9]
        active_tag = payload[1]
        last_command = command
        start_timed_animation(content_id, entry_ms, hold_ms, exit_ms,
                              time.monotonic())
    elif command == protocol.SHOW_CLOCK:
        if len(payload) != 5:
            error_code = protocol.ERROR_BAD_LENGTH
            return
        if payload[2] > 23 or payload[3] > 59:
            error_code = protocol.ERROR_INVALID_ARGUMENT
            return
        active_tag = payload[1]
        last_command = command
        clock_value = (payload[2], payload[3])
        clock_flags = payload[4]
        render_clock(time.monotonic(), force=True)
        display_state = protocol.DISPLAY_CLOCK
        activity_state = protocol.ACTIVITY_COMPLETE
    elif command == protocol.SHOW_DEV_TEXT:
        if not 3 <= len(payload) <= 31:
            error_code = protocol.ERROR_BAD_LENGTH
            return
        try:
            text = payload[2:].decode("ascii")
        except UnicodeError:
            error_code = protocol.ERROR_INVALID_ARGUMENT
            return
        active_tag = payload[1]
        last_command = command
        active_content_id = 0
        start_message(text)
        display_state = protocol.DISPLAY_MESSAGE
        activity_state = protocol.ACTIVITY_COMPLETE
    else:
        error_code = protocol.ERROR_UNKNOWN_COMMAND
        return
    lifecycle_state = protocol.LIFECYCLE_BRAIN_CONTROLLED


def render_clock(now, force=False):
    global last_colon
    if clock_value is None or display_state != protocol.DISPLAY_CLOCK and not force:
        return
    colon = True
    if clock_flags & 1:
        colon = int(now * 2) % 2 == 0
    if not force and colon == last_colon:
        return
    hour, minute = clock_value
    if not clock_flags & 2:
        hour = hour % 12 or 12
    show_frame(clock_frame(geometry, hour, minute, colon))
    last_colon = colon


enable = digitalio.DigitalInOut(config.BUFFER_ENABLE)
enable.switch_to_output(value=False)
mode_button = digitalio.DigitalInOut(config.MODE_BUTTON)
mode_button.switch_to_input(pull=digitalio.Pull.UP)
address_input = analogio.AnalogIn(config.ADDRESS_PIN)
address_raw = read_address_adc(address_input)
address, module_type = decode_role(address_raw)
address_input.deinit()

if module_type is None:
    # Development/spare jumper states cannot infer attached display geometry.
    module_type = protocol.MODULE_EYES
    log("WARNING: unknown role; using Eyes geometry")

geometry = geometry_for(module_type)
if module_type == protocol.MODULE_EYES:
    catalog_frames = catalog.EYES_FRAMES
    catalog_animations = catalog.EYES_ANIMATIONS
    catalog_normal_frame = catalog.EYES_NORMAL_FRAME
else:
    catalog_frames = catalog.MOUTH_FRAMES
    catalog_animations = catalog.MOUTH_ANIMATIONS
    catalog_normal_frame = catalog.MOUTH_NORMAL_FRAME
pixels = adafruit_dotstar.DotStar(
    config.DISPLAY_CLOCK,
    config.DISPLAY_DATA,
    geometry.pixel_count,
    brightness=config.BRIGHTNESS,
    auto_write=False,
    baudrate=config.SPI_BAUDRATE,
)
show_frame(blank_frame(geometry))

log("BU-22 DEVELOPMENT CONTROLLER")
log("address_adc=", address_raw, "address=0x%02X" % address)
log("display=", geometry.width, "x", geometry.height)

time.sleep(config.STARTUP_DARK_SECONDS)
enable.value = True
show_scrolling_text("TARGET MODE", config.STARTUP_MESSAGE_SECONDS)
identity = ("E" if module_type == protocol.MODULE_EYES else "M") + "%02X" % address
show_frame(text_frame(geometry, identity))
time.sleep(config.STARTUP_IDENTITY_SECONDS)

modes = LocalModeState()
display_state = protocol.DISPLAY_OFF
lifecycle_state = protocol.LIFECYCLE_WAITING_FOR_BRAIN
active_tag = 0
last_command = protocol.SET_OFF
active_content_id = 0
error_code = protocol.ERROR_NONE
activity_state = protocol.ACTIVITY_IDLE
brain_seen = False
clock_value = None
clock_flags = 0
last_colon = None
message_text = None
message_index = 0
message_duration = config.MODE_ANNOUNCEMENT_SECONDS
message_is_mode_announcement = False
next_message_frame = time.monotonic()
test_step = 0
next_test_frame = time.monotonic()
animation_frames = None
animation_index = 0
next_animation_frame = None
next_bender_animation = time.monotonic()
last_bender_animation = None
timed_entry = None
timed_exit = None
timed_phase = None
timed_phase_started = None
timed_durations = None
next_timed_frame = None
timed_last_frame = None
render_current_mode()

target = i2ctarget.I2CTarget(config.I2C_SCL, config.I2C_SDA, (address,))
button_was_down = False
button_changed_at = time.monotonic()

while True:
    now = time.monotonic()
    button_down = not mode_button.value
    if button_down != button_was_down and now - button_changed_at >= config.BUTTON_DEBOUNCE_SECONDS:
        button_changed_at = now
        button_was_down = button_down
        if button_down:
            change_mode()

    if message_text is not None:
        update_message(now)
    elif timed_phase is not None:
        update_timed_animation(now)
    elif animation_frames is not None:
        update_animation(now)
    elif modes.mode == protocol.LOCAL_TEST:
        update_test(now)
    elif modes.mode == protocol.LOCAL_BENDER:
        update_bender(now)
    elif modes.mode == protocol.LOCAL_TARGET and display_state == protocol.DISPLAY_CLOCK:
        render_clock(now)

    try:
        request = target.request(timeout=0.005)
    except OSError:
        request = None
    if request is not None:
        with request:
            if request.is_read:
                request.write(status_bytes())
            else:
                accept(bytes(request.read()))
    time.sleep(0.001)
