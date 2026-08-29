"""Throw-away visual/electrical bring-up suite for Display Controller Rev D."""

import gc
import time
import analogio
import digitalio

import adafruit_dotstar

import config


BLACK = (0, 0, 0)
DIM_WHITE = (48, 48, 48)
CHANNEL_COLORS = (
    (255, 0, 0),       # CH1 red
    (0, 255, 0),       # CH2 green
    (0, 0, 255),       # CH3 blue
    (255, 90, 0),      # CH4 amber
    (0, 180, 255),     # CH5 cyan
    (220, 0, 255),     # CH6 magenta
)


def banner():
    print("\nBU-22 DISPLAY CONTROLLER REV D BRING-UP")
    print("Channels: 6")
    print("Pixels/channel:", config.PIXELS_PER_CHANNEL)
    print("Normal brightness:", config.NORMAL_BRIGHTNESS)
    print("Current-limit the 5 V supply for first power-up.")


def countdown():
    print("Buffers disabled during safe-start delay.")
    for remaining in range(config.SAFE_START_SECONDS, 0, -1):
        print("Starting in", remaining)
        time.sleep(1)


def make_channels():
    result = []
    for clock_pin, data_pin in config.CHANNEL_PINS:
        result.append(adafruit_dotstar.DotStar(
            clock_pin,
            data_pin,
            config.PIXELS_PER_CHANNEL,
            brightness=config.NORMAL_BRIGHTNESS,
            auto_write=False,
        ))
    return tuple(result)


def set_brightness(channels, value):
    for channel in channels:
        channel.brightness = value


def show_all(channels):
    for channel in channels:
        channel.show()


def clear(channels, pause=0.0):
    for channel in channels:
        channel.fill(BLACK)
    show_all(channels)
    if pause:
        time.sleep(pause)


def test_local_inputs(test_button, address, heartbeat):
    print("\nTEST 0: local inputs")
    print(" Address ADC raw:", address.value, "(move shunts and reboot to compare)")
    print(" TEST button:", "PRESSED" if not test_button.value else "released")

    previous = heartbeat.value
    transitions = 0
    started = time.monotonic()
    while time.monotonic() - started < 2.2:
        current = heartbeat.value
        if current != previous:
            transitions += 1
            previous = current
        time.sleep(0.005)
    print(" Heartbeat transitions in 2.2 s:", transitions,
          "(0 is expected when heartbeat is disconnected)")


def test_channel_identity(channels):
    print("\nTEST 1: channel identity and crosstalk")
    for selected, color in enumerate(CHANNEL_COLORS):
        clear(channels)
        channels[selected].fill(color)
        show_all(channels)
        print(" CH", selected + 1, "ON; every other channel must be black")
        time.sleep(1.0)
    clear(channels, 0.5)


def test_endpoints_and_order(channels):
    print("\nTEST 2: first pixel, last pixel, then forward chase")
    clear(channels)
    for index, channel in enumerate(channels):
        channel[0] = CHANNEL_COLORS[index]
    show_all(channels)
    print(" First pixel on every channel")
    time.sleep(1.2)

    clear(channels)
    for index, channel in enumerate(channels):
        channel[config.PIXELS_PER_CHANNEL - 1] = CHANNEL_COLORS[index]
    show_all(channels)
    print(" Last pixel on every channel")
    time.sleep(1.2)

    for pixel in range(config.PIXELS_PER_CHANNEL):
        clear(channels)
        for index, channel in enumerate(channels):
            channel[pixel] = CHANNEL_COLORS[index]
        show_all(channels)
        print(" Pixel", pixel + 1)
        time.sleep(0.15)
    clear(channels, 0.5)


def test_color_order(channels):
    print("\nTEST 3: RGB order and mixed colors")
    colors = (
        ("RED", (255, 0, 0)),
        ("GREEN", (0, 255, 0)),
        ("BLUE", (0, 0, 255)),
        ("YELLOW", (255, 180, 0)),
        ("CYAN", (0, 180, 255)),
        ("MAGENTA", (220, 0, 255)),
        ("DIM WHITE", DIM_WHITE),
    )
    for name, color in colors:
        for channel in channels:
            channel.fill(color)
        show_all(channels)
        print(" ", name)
        time.sleep(0.8)
    clear(channels, 0.5)


def test_brightness(channels):
    print("\nTEST 4: global brightness ladder")
    for brightness in (0.01, 0.02, 0.04, 0.08, config.STRESS_BRIGHTNESS):
        set_brightness(channels, brightness)
        for channel in channels:
            channel.fill((255, 120, 0))
        show_all(channels)
        print(" Brightness:", brightness)
        time.sleep(1.0)
    clear(channels)
    set_brightness(channels, config.NORMAL_BRIGHTNESS)
    time.sleep(0.5)


def test_ten_fps(channels, seconds=8):
    print("\nTEST 5: all-channel 10 FPS timing and load")
    period = 1.0 / config.FRAME_RATE
    frames = int(seconds * config.FRAME_RATE)
    started = time.monotonic()
    late = 0
    for frame in range(frames):
        deadline = started + ((frame + 1) * period)
        for channel_index, channel in enumerate(channels):
            channel.fill(BLACK)
            pixel = (frame + channel_index) % config.PIXELS_PER_CHANNEL
            channel[pixel] = CHANNEL_COLORS[channel_index]
        show_all(channels)
        remaining = deadline - time.monotonic()
        if remaining > 0:
            time.sleep(remaining)
        else:
            late += 1
    elapsed = time.monotonic() - started
    print(" Frames:", frames, "elapsed:", elapsed, "late:", late)
    print(" Free memory:", gc.mem_free())
    clear(channels, 0.5)


def test_blackout_and_enable(channels, output_enable):
    print("\nTEST 6: commanded blackout and hardware output enable")
    for channel in channels:
        channel.fill((24, 24, 24))
    show_all(channels)
    time.sleep(0.8)
    clear(channels, 0.4)

    # Disabling the buffers prevents new clock/data traffic. Existing LEDs
    # retain their last (black) frame, so this validates OE without flashing.
    output_enable.value = False
    print(" Buffers disabled for 1 second")
    time.sleep(1.0)
    output_enable.value = True
    clear(channels, 0.5)
    print(" Buffers re-enabled")


def run_suite(channels, output_enable, test_button, address, heartbeat):
    test_local_inputs(test_button, address, heartbeat)
    test_channel_identity(channels)
    test_endpoints_and_order(channels)
    test_color_order(channels)
    test_brightness(channels)
    test_ten_fps(channels)
    test_blackout_and_enable(channels, output_enable)
    print("\nPASS: visual suite complete; review observations above")
    print("Press TEST to repeat immediately, or wait 10 seconds.")
    clear(channels)
    deadline = time.monotonic() + 10
    while test_button.value and time.monotonic() < deadline:
        time.sleep(0.01)
    while not test_button.value:
        time.sleep(0.01)


banner()

# Hold the AHCT outputs disabled before any channel GPIO is initialized.
output_enable = digitalio.DigitalInOut(config.BUFFER_ENABLE)
output_enable.switch_to_output(value=False)
test_button = digitalio.DigitalInOut(config.TEST_BUTTON)
test_button.switch_to_input(pull=digitalio.Pull.UP)
heartbeat = digitalio.DigitalInOut(config.HEARTBEAT)
# The completed BU-22 system supplies the heartbeat pull-up at the Brain/RTC.
# Do not make an otherwise disconnected controller illuminate its HEART LED.
heartbeat.switch_to_input()
address = analogio.AnalogIn(config.ADDRESS)

countdown()
channels = make_channels()

# Enable the level shifters and immediately establish a known black frame.
output_enable.value = True
clear(channels, 0.5)

while True:
    run_suite(channels, output_enable, test_button, address, heartbeat)
