"""Button-driven BU-22 Brain development runtime."""

import time

import board
import busio
import digitalio
import keypad
import microcontroller
import random
import supervisor

import animation_catalog
import config
from common.brain_state import (
    AntennaSequence,
    BrainState,
    MODE_BENDER,
    MODE_CLOCK,
    MODE_NAMES,
    MODE_PLAY,
    MODE_SETTINGS,
    MODE_TEST,
    TEST_ANTENNA,
    TEST_NAMES,
    TEST_RTC,
)
from common import protocol
from common.brain_settings import (
    COLON_FLASH,
    ClockSettings,
    ZONE_LABELS,
    local_hour,
    utc_hour,
)


supervisor.runtime.autoreload = False
RTC_CONTROL_REGISTER = 0x0E
RTC_SQW_1HZ_MASK = 0x1C

SETTING_DST = 0
SETTING_ZONE = 1
SETTING_FORMAT = 2
SETTING_HOUR = 3
SETTING_MINUTE = 4
SETTING_AMPM = 5
SETTING_COLON = 6
SETTING_EXIT = 7


def log(*values):
    if config.LOGGING:
        print(*values)


def i2c_lock():
    while not i2c.try_lock():
        time.sleep(0.001)


def scan():
    i2c_lock()
    try:
        return tuple(i2c.scan())
    finally:
        i2c.unlock()


def next_tag():
    global display_tag
    display_tag = (display_tag + 1) & 0xFF
    return display_tag


def write_display(address, payload):
    i2c_lock()
    try:
        i2c.writeto(address, payload)
    except OSError as error:
        log("I2C WRITE ERROR 0x%02X" % address, repr(error))
        return False
    finally:
        i2c.unlock()
    if config.MIRROR_I2C:
        log("I2C TX 0x%02X" % address, tuple(payload))
    time.sleep(config.I2C_TRANSACTION_GAP)
    return True


def send_visual(address, command, content_id=None):
    return write_display(
        address, protocol.visual_packet(command, next_tag(), content_id)
    )


def send_timed_animation(address, content_id, entry_ms, hold_ms, exit_ms):
    return write_display(
        address,
        protocol.timed_animation_packet(
            next_tag(), content_id, entry_ms, hold_ms, exit_ms),
    )


def send_clock(hour, minute, use_24_hour=False, flash_colon=True):
    flags = (1 if flash_colon else 0) | (2 if use_24_hour else 0)
    return write_display(
        config.EYES_ADDRESS,
        protocol.clock_packet(next_tag(), hour, minute, flags),
    )


def send_label(text, eyes=True, mouth=True):
    tag = next_tag()
    payload = protocol.dev_text_packet(tag, text)
    if eyes:
        write_display(config.EYES_ADDRESS, payload)
    if mouth:
        write_display(config.MOUTH_ADDRESS, payload)


def play_item_count():
    return len(animation_catalog.PERFORMANCES) + len(animation_catalog.ANIMATIONS)


def selected_play_item():
    index = state.play_selection
    if index < len(animation_catalog.PERFORMANCES):
        return "performance", animation_catalog.PERFORMANCES[index]
    return "animation", animation_catalog.ANIMATIONS[
        index - len(animation_catalog.PERFORMANCES)]


def animation_address(target_name):
    return (config.EYES_ADDRESS if target_name == "eyes"
            else config.MOUTH_ADDRESS)


def show_play_selection():
    kind, item = selected_play_item()
    if kind == "performance":
        item_id, name, _duration, _events = item
        send_label("P " + name)
        log("PLAY SELECT PERFORMANCE", item_id, name)
    else:
        animation_id, target_name, name, _frame_count = item
        prefix = "E " if target_name == "eyes" else "M "
        send_label(prefix + name)
        log("PLAY SELECT ANIMATION", animation_id, target_name, name)


def play_selected_item():
    kind, item = selected_play_item()
    if kind == "performance":
        start_performance(item, time.monotonic())
    else:
        animation_id, target_name, name, _frame_count = item
        send_visual(animation_address(target_name), protocol.PLAY_ANIMATION,
                    animation_id)
        log("PLAY ANIMATION", animation_id, target_name, name)


def audio_play_slot(slot):
    filename = "T%02d     WAV" % slot
    audio_uart.reset_input_buffer()
    audio_uart.write(("P%s\n" % filename).encode("ascii"))
    log("AUDIO PLAY T%02d.WAV" % slot)


def stop_performance():
    global performance_active, performance_events, performance_event_index
    if performance_active:
        audio_uart.write(b"q\n")
    performance_active = False
    performance_events = ()
    performance_event_index = 0


def start_performance(performance, now):
    global performance_active, performance_started, performance_events
    global performance_event_index, performance_ends
    stop_performance()
    performance_id, name, duration_ms, events = performance
    send_visual(config.EYES_ADDRESS, protocol.SHOW_NORMAL)
    send_visual(config.MOUTH_ADDRESS, protocol.SHOW_NORMAL)
    performance_active = True
    performance_started = now
    performance_events = events
    performance_event_index = 0
    performance_ends = now + duration_ms / 1000
    log("PERFORMANCE START", performance_id, name, duration_ms)


def update_performance(now):
    global performance_active, performance_event_index
    elapsed_ms = int((now - performance_started) * 1000)
    while (performance_event_index < len(performance_events)
           and performance_events[performance_event_index][0] <= elapsed_ms):
        event = performance_events[performance_event_index]
        _start_ms, kind, target_or_audio, content_or_slot, entry, hold, exit_ms = event
        if kind == 0:
            address = (config.EYES_ADDRESS if target_or_audio == 1
                       else config.MOUTH_ADDRESS)
            send_timed_animation(address, content_or_slot, entry, hold, exit_ms)
        else:
            audio_play_slot(content_or_slot)
        performance_event_index += 1
    if now >= performance_ends:
        performance_active = False
        log("PERFORMANCE COMPLETE")


def schedule_bender_animation(now):
    global next_bender_animation, last_bender_animation
    choices = animation_catalog.ANIMATIONS
    selected = random.choice(choices)
    if len(choices) > 1:
        while selected[0] == last_bender_animation:
            selected = random.choice(choices)
    animation_id, target_name, name, frame_count = selected
    send_visual(animation_address(target_name), protocol.PLAY_ANIMATION,
                animation_id)
    last_bender_animation = animation_id
    playback_seconds = frame_count / animation_catalog.DEFAULT_ANIMATION_FPS
    next_bender_animation = (
        now + playback_seconds
        + random.uniform(config.BENDER_MIN_PAUSE_SECONDS,
                         config.BENDER_MAX_PAUSE_SECONDS)
    )
    log("BENDER", animation_id, target_name, name,
        "next=%.2f" % next_bender_animation)


def read_display_status(address):
    response = bytearray(20)
    i2c_lock()
    try:
        i2c.readfrom_into(address, response)
    except OSError as error:
        log("I2C STATUS ERROR 0x%02X" % address, repr(error))
        return None
    finally:
        i2c.unlock()
    if response[0] != protocol.MAGIC:
        log("BAD STATUS 0x%02X" % address, tuple(response))
        return None
    mode = protocol.local_mode_from_status(response[6], response[16])
    log(
        "STATUS 0x%02X" % address,
        "mode=", protocol.local_mode_name(mode),
        "display=", response[7],
        "error=", response[11],
    )
    return response


def rtc_device():
    import adafruit_ds3231
    return adafruit_ds3231.DS3231(i2c)


def configure_rtc_sqw(rtc):
    register = bytearray((RTC_CONTROL_REGISTER,))
    control = bytearray(1)
    with rtc.i2c_device as device:
        device.write_then_readinto(register, control)
        control[0] &= ~RTC_SQW_1HZ_MASK
        device.write(bytearray((RTC_CONTROL_REGISTER, control[0])))
    log("RTC SQW configured for 1 Hz")


def current_time():
    if rtc is None:
        return None
    try:
        return rtc.datetime
    except Exception as error:
        log("RTC READ ERROR", repr(error))
        return None


def set_antenna_output(index):
    for output_index, output in enumerate(antenna_outputs):
        output.value = index == output_index
    log("ANTENNA", "OFF" if index is None else config.ANTENNA_NAMES[index])


def stop_active_test():
    antenna_test.stop()
    set_antenna_output(None)


def show_clock(force=False):
    global last_clock_minute
    value = current_time()
    if value is None:
        return
    hour = local_hour(value.tm_hour, settings.timezone, settings.dst)
    key = (hour, value.tm_min, settings.use_24_hour, settings.colon_mode)
    if force or key != last_clock_minute:
        send_clock(hour, value.tm_min, settings.use_24_hour,
                   settings.colon_mode == COLON_FLASH)
        last_clock_minute = key
        log("CLOCK", "%02d:%02d" % (hour, value.tm_min))


def enter_mode(mode):
    global staged_time, setting_index, settings_last_activity
    global last_clock_minute, rtc_test_active, next_bender_animation
    stop_performance()
    stop_active_test()
    rtc_test_active = False
    log("MODE", MODE_NAMES[mode])
    send_label(MODE_NAMES[mode])
    time.sleep(config.MODE_ANNOUNCEMENT_SECONDS)
    if mode == MODE_CLOCK:
        last_clock_minute = None
        send_visual(config.MOUTH_ADDRESS, protocol.SET_OFF)
        show_clock(force=True)
    elif mode == MODE_SETTINGS:
        value = current_time()
        if value is not None:
            staged_time = [
                local_hour(value.tm_hour, settings.timezone, settings.dst),
                value.tm_min,
            ]
            setting_index = SETTING_DST
            settings_last_activity = time.monotonic()
            send_visual(config.MOUTH_ADDRESS, protocol.SET_OFF)
            show_setting()
    elif mode == MODE_BENDER:
        send_visual(config.EYES_ADDRESS, protocol.SHOW_NORMAL)
        send_visual(config.MOUTH_ADDRESS, protocol.SHOW_NORMAL)
        next_bender_animation = time.monotonic()
    elif mode == MODE_PLAY:
        send_visual(config.EYES_ADDRESS, protocol.SET_OFF)
        send_visual(config.MOUTH_ADDRESS, protocol.SET_OFF)
        show_play_selection()
    elif mode == MODE_TEST:
        log("TEST SELECT", TEST_NAMES[state.test_selection])


def show_setting():
    if setting_index == SETTING_DST:
        send_label("DST " + ("ON" if settings.dst else "OFF"))
    elif setting_index == SETTING_ZONE:
        send_label("ZONE " + ZONE_LABELS[settings.timezone])
    elif setting_index == SETTING_FORMAT:
        send_label("24 HOUR" if settings.use_24_hour else "12 HOUR")
    elif setting_index in (SETTING_HOUR, SETTING_MINUTE):
        send_visual(config.MOUTH_ADDRESS, protocol.SET_OFF)
        send_clock(staged_time[0], staged_time[1], settings.use_24_hour,
                   settings.colon_mode == COLON_FLASH)
    elif setting_index == SETTING_AMPM:
        send_label("PM" if staged_time[0] >= 12 else "AM")
    elif setting_index == SETTING_COLON:
        send_label("COLON " + (
            "FLASH" if settings.colon_mode == COLON_FLASH else "SOLID"
        ))
    else:
        send_label("EXIT")


def refresh_staged_hour():
    if staged_time is None:
        return
    value = current_time()
    if value is not None:
        staged_time[0] = local_hour(
            value.tm_hour, settings.timezone, settings.dst)


def adjust_setting(delta):
    if setting_index == SETTING_DST:
        settings.dst = not settings.dst
        settings.save(microcontroller.nvm)
        refresh_staged_hour()
    elif setting_index == SETTING_ZONE:
        settings.timezone = (settings.timezone + delta) % len(ZONE_LABELS)
        settings.save(microcontroller.nvm)
        refresh_staged_hour()
    elif setting_index == SETTING_FORMAT:
        settings.use_24_hour = not settings.use_24_hour
        settings.save(microcontroller.nvm)
    elif setting_index == SETTING_HOUR:
        staged_time[0] = (staged_time[0] + delta) % 24
    elif setting_index == SETTING_MINUTE:
        staged_time[1] = (staged_time[1] + delta) % 60
    elif setting_index == SETTING_AMPM:
        staged_time[0] = (staged_time[0] + 12) % 24
    elif setting_index == SETTING_COLON:
        settings.colon_mode = (settings.colon_mode + delta) % 2
        settings.save(microcontroller.nvm)
    show_setting()


def commit_staged_time():
    if staged_time is None or rtc is None:
        return
    old = rtc.datetime
    rtc.datetime = time.struct_time((
        old.tm_year, old.tm_mon, old.tm_mday,
        utc_hour(staged_time[0], settings.timezone, settings.dst),
        staged_time[1], 0,
        old.tm_wday, old.tm_yday, old.tm_isdst,
    ))
    log("RTC SET LOCAL", "%02d:%02d" % tuple(staged_time))


def next_setting():
    global setting_index
    if setting_index == SETTING_EXIT:
        state.mode = MODE_CLOCK
        enter_mode(MODE_CLOCK)
        return
    setting_index += 1
    if setting_index == SETTING_AMPM and settings.use_24_hour:
        setting_index = SETTING_COLON
    if setting_index == SETTING_COLON:
        commit_staged_time()
    show_setting()


def start_selected_test():
    global rtc_test_active, last_clock_minute
    if state.test_selection == TEST_RTC:
        rtc_test_active = not rtc_test_active
        if rtc_test_active:
            last_clock_minute = None
            send_label("RTC", eyes=False)
            show_clock(force=True)
            log("RTC TEST START; flashing colon confirms display clock activity")
        else:
            send_visual(config.EYES_ADDRESS, protocol.SET_OFF)
            log("RTC TEST STOP")
    elif state.test_selection == TEST_ANTENNA:
        rtc_test_active = False
        send_label("ANTENNA")
        set_antenna_output(antenna_test.start(time.monotonic()))
        log("ANTENNA TEST START: three RGB cycles")


def button_pressed(key_number):
    global rtc_test_active, settings_last_activity
    if key_number == config.MODE_BUTTON:
        state.next_mode()
        enter_mode(state.mode)
    elif state.mode == MODE_SETTINGS:
        settings_last_activity = time.monotonic()
        if key_number == config.UP_BUTTON:
            adjust_setting(1)
        elif key_number == config.DOWN_BUTTON:
            adjust_setting(-1)
        elif key_number == config.ENTER_BUTTON:
            next_setting()
    elif state.mode == MODE_TEST:
        if key_number == config.UP_BUTTON:
            stop_active_test()
            rtc_test_active = False
            state.select_next_test(-1)
            send_label("TEST " + TEST_NAMES[state.test_selection])
            log("TEST SELECT", TEST_NAMES[state.test_selection])
        elif key_number == config.DOWN_BUTTON:
            stop_active_test()
            rtc_test_active = False
            state.select_next_test(1)
            send_label("TEST " + TEST_NAMES[state.test_selection])
            log("TEST SELECT", TEST_NAMES[state.test_selection])
        elif key_number == config.ENTER_BUTTON:
            start_selected_test()
    elif state.mode == MODE_PLAY:
        if key_number == config.UP_BUTTON:
            stop_performance()
            state.select_next_play_item(play_item_count(), -1)
            show_play_selection()
        elif key_number == config.DOWN_BUTTON:
            stop_performance()
            state.select_next_play_item(play_item_count(), 1)
            show_play_selection()
        elif key_number == config.ENTER_BUTTON:
            play_selected_item()


log("BU-22 BRAIN DEVELOPMENT RUNTIME")
i2c = busio.I2C(config.I2C_SCL, config.I2C_SDA,
                frequency=config.I2C_FREQUENCY)
audio_uart = busio.UART(
    config.AUDIO_TX, config.AUDIO_RX,
    baudrate=config.AUDIO_BAUDRATE,
    timeout=0,
    receiver_buffer_size=512,
)
buttons = keypad.Keys(config.BUTTON_PINS, value_when_pressed=False,
                      pull=True, interval=0.02)
sqw = digitalio.DigitalInOut(config.RTC_SQW)
sqw.switch_to_input(pull=digitalio.Pull.UP)

antenna_outputs = []
for pin in config.ANTENNA_PINS:
    output = digitalio.DigitalInOut(pin)
    output.switch_to_output(value=False)
    antenna_outputs.append(output)

log("Startup delay", config.STARTUP_SCAN_DELAY_SECONDS, "seconds")
time.sleep(config.STARTUP_SCAN_DELAY_SECONDS)
found = scan()
log("I2C FOUND", tuple("0x%02X" % address for address in found))

rtc = None
if config.RTC_ADDRESS in found:
    try:
        rtc = rtc_device()
        configure_rtc_sqw(rtc)
    except Exception as error:
        log("RTC INIT ERROR", repr(error))

for display_address in (config.EYES_ADDRESS, config.MOUTH_ADDRESS):
    if display_address in found:
        read_display_status(display_address)

state = BrainState()
settings = ClockSettings()
settings.load(microcontroller.nvm)
antenna_test = AntennaSequence(repetitions=3)
rtc_test_active = False
last_clock_minute = None
staged_time = None
setting_index = SETTING_DST
settings_last_activity = time.monotonic()
display_tag = 0
next_bender_animation = time.monotonic()
last_bender_animation = None
performance_active = False
performance_started = None
performance_events = ()
performance_event_index = 0
performance_ends = None
enter_mode(state.mode)

while True:
    now = time.monotonic()
    event = buttons.events.get()
    if event is not None and event.pressed:
        log("BUTTON", config.BUTTON_NAMES[event.key_number])
        button_pressed(event.key_number)

    if state.mode == MODE_CLOCK or (
        state.mode == MODE_TEST and rtc_test_active
    ):
        show_clock()

    if state.mode == MODE_BENDER and now >= next_bender_animation:
        schedule_bender_animation(now)

    if state.mode == MODE_PLAY and performance_active:
        update_performance(now)

    if (state.mode == MODE_SETTINGS
            and now - settings_last_activity >= config.SETTINGS_TIMEOUT_SECONDS):
        staged_time = None
        state.mode = MODE_CLOCK
        enter_mode(MODE_CLOCK)

    changed, antenna_index = antenna_test.update(now)
    if changed:
        set_antenna_output(antenna_index)
        if not antenna_test.running:
            log("ANTENNA TEST COMPLETE")

    time.sleep(0.005)
