"""Six-channel SK9822 electrical and animation test for BU-22 hardware."""

import gc
import time

import adafruit_dotstar

import config


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CHANNEL_COLORS = (
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 90, 0),
    (0, 180, 255),
    (220, 0, 255),
)


def wait_without_driving_outputs():
    print("\nBU-22 Eyes: KB2040 six-channel SK9822 test")
    print("All display GPIOs remain inputs during the safe-start delay.")
    print("Channels=6, Pixels per channel=", config.PIXELS_PER_CHANNEL)
    remaining = config.SAFE_START_DELAY_SECONDS
    while remaining:
        print("Starting in", remaining, "seconds")
        time.sleep(1)
        remaining -= 1


def make_channels():
    result = []
    for clock_pin, data_pin in config.CHANNEL_PINS:
        result.append(adafruit_dotstar.DotStar(
            clock_pin,
            data_pin,
            config.PIXELS_PER_CHANNEL,
            brightness=config.PIXEL_BRIGHTNESS,
            auto_write=False,
        ))
    return tuple(result)


def show_all(channels):
    for channel in channels:
        channel.show()


def clear(channels, pause=0):
    for channel in channels:
        channel.fill(BLACK)
    show_all(channels)
    if pause:
        time.sleep(pause)


def test_channel_identity(channels):
    print("TEST 1: channel identity and crosstalk")
    for selected, color in enumerate(CHANNEL_COLORS[:len(channels)]):
        clear(channels)
        channels[selected].fill(color)
        show_all(channels)
        print(" Channel", selected + 1)
        time.sleep(0.8)
    clear(channels, 0.5)


def test_pixel_order(channels):
    print("TEST 2: pixel order")
    for pixel in range(config.PIXELS_PER_CHANNEL):
        clear(channels)
        for channel_index, channel in enumerate(channels):
            channel[pixel] = CHANNEL_COLORS[channel_index]
        show_all(channels)
        print(" Pixel", pixel + 1)
        time.sleep(0.5)
    clear(channels, 0.5)


def test_primary_colors(channels):
    print("TEST 3: RGB color order")
    for name, color in (("RED", (255, 0, 0)),
                        ("GREEN", (0, 255, 0)),
                        ("BLUE", (0, 0, 255)),
                        ("WHITE", WHITE)):
        print(" ", name)
        for channel in channels:
            channel.fill(color)
        show_all(channels)
        time.sleep(0.8)
    clear(channels, 0.5)


def test_low_levels(channels):
    print("TEST 4: low-level brightness steps")
    # RGB values stay low in addition to the global 8% limit.
    for value in (2, 4, 8, 16, 32, 64, 128, 255):
        color = (value, value, value)
        for channel in channels:
            channel.fill(color)
        show_all(channels)
        print(" Level", value)
        time.sleep(0.45)
    clear(channels, 0.5)


def test_ten_fps(channels, seconds=12):
    print("TEST 5: 10 FPS animation")
    frame_period = 1.0 / config.FRAME_RATE
    frames = int(seconds * config.FRAME_RATE)
    started = time.monotonic()
    late_frames = 0
    for frame_number in range(frames):
        deadline = started + ((frame_number + 1) * frame_period)
        for channel_index, channel in enumerate(channels):
            channel.fill(BLACK)
            pixel = (frame_number + channel_index) % config.PIXELS_PER_CHANNEL
            channel[pixel] = CHANNEL_COLORS[channel_index]
        show_all(channels)
        remaining = deadline - time.monotonic()
        if remaining > 0:
            time.sleep(remaining)
        else:
            late_frames += 1
    elapsed = time.monotonic() - started
    print(" Frames:", frames, "elapsed:", elapsed, "late:", late_frames)
    print(" Free memory:", gc.mem_free())
    clear(channels, 0.5)


def run_suite(channels):
    clear(channels, 1.0)  # Always transmit black first.
    test_channel_identity(channels)
    test_pixel_order(channels)
    test_primary_colors(channels)
    test_low_levels(channels)
    test_ten_fps(channels)
    print("PASS: suite complete; repeating in 3 seconds")
    clear(channels, 3.0)


wait_without_driving_outputs()
channels = make_channels()

while True:
    run_suite(channels)
