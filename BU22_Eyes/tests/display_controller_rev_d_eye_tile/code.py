"""Identical six-channel visual test for a 9x16 serpentine eye tile."""

import time
import digitalio

import adafruit_dotstar

import config


VERSION = "0.3"
BLACK = (0, 0, 0)
CHASE_COLOR = (255, 80, 0)
COLUMN_COLOR = (0, 100, 255)
ROW_COLOR = (180, 0, 255)
ALL_ON_COLORS = (
    ("RED", (160, 0, 0)),
    ("GREEN", (0, 160, 0)),
    ("BLUE", (0, 0, 160)),
    ("DIM WHITE", (48, 48, 48)),
)
EYE_COLOR = (255, 110, 0)

# Nine characters per row, top to bottom. The LED columns have wider physical
# spacing than the pixels within each strip, so this 9x16 logical mask appears
# approximately square on the temporary strip-built tile.
EYE_MASK = (
    "...YYY...",
    "..YYYYY..",
    ".YYYYYYY.",
    ".YYYYYYY.",
    "YYYYYYYYY",
    "YYYYYYYYY",
    "YYY...YYY",
    "YYY...YYY",
    "YYY...YYY",
    "YYY...YYY",
    "YYYYYYYYY",
    "YYYYYYYYY",
    ".YYYYYYY.",
    ".YYYYYYY.",
    "..YYYYY..",
    "...YYY...",
)


def make_channels():
    return tuple(
        adafruit_dotstar.DotStar(
            clock,
            data,
            config.PIXELS_PER_CHANNEL,
            brightness=config.GLOBAL_BRIGHTNESS,
            auto_write=False,
        )
        for clock, data in config.CHANNEL_PINS
    )


def show(channels):
    for channel in channels:
        channel.show()


def clear(channels, pause=0.0):
    for channel in channels:
        channel.fill(BLACK)
    show(channels)
    if pause:
        time.sleep(pause)


def set_identical_pixel(channels, index, color):
    for channel in channels:
        channel[index] = color


def serpentine_index(column, row):
    """Top-left origin; even columns descend and odd columns ascend."""
    physical_row = row if column % 2 == 0 else config.MODULE_HEIGHT - 1 - row
    return column * config.MODULE_HEIGHT + physical_row


def bender_eye(channels):
    print("PATTERN 1: centered Bender eye")
    clear(channels)
    for row, pixels in enumerate(EYE_MASK):
        for column, pixel in enumerate(pixels):
            if pixel == "Y":
                set_identical_pixel(
                    channels, serpentine_index(column, row), EYE_COLOR
                )
    show(channels)
    time.sleep(config.EYEBALL_SECONDS)
    clear(channels, 0.5)


def path_chase(channels):
    print(
        "PATTERN 2: sequential",
        config.PIXELS_PER_CHANNEL,
        "pixel path chase",
    )
    clear(channels)
    started = time.monotonic()
    previous_index = None
    for index in range(config.PIXELS_PER_CHANNEL):
        if previous_index is not None:
            set_identical_pixel(channels, previous_index, BLACK)
        set_identical_pixel(channels, index, CHASE_COLOR)
        show(channels)
        if index % config.MODULE_HEIGHT == 0:
            print(" Starting physical column", index // config.MODULE_HEIGHT + 1)
        time.sleep(config.CHASE_SECONDS)
        previous_index = index
    elapsed = time.monotonic() - started
    print(" Chase: %.2f seconds, %.1f frames/sec" % (
        elapsed, config.PIXELS_PER_CHANNEL / elapsed
    ))
    clear(channels, 0.5)


def column_sweep(channels):
    print("PATTERN 3:", config.MODULE_WIDTH, "column sweep, left to right")
    for column in range(config.MODULE_WIDTH):
        clear(channels)
        for row in range(config.MODULE_HEIGHT):
            set_identical_pixel(
                channels, serpentine_index(column, row), COLUMN_COLOR
            )
        show(channels)
        print(" Column", column + 1)
        time.sleep(config.SWEEP_SECONDS)
    clear(channels, 0.5)


def row_sweep(channels):
    print("PATTERN 4:", config.MODULE_HEIGHT, "row sweep, top to bottom")
    for row in range(config.MODULE_HEIGHT):
        clear(channels)
        for column in range(config.MODULE_WIDTH):
            set_identical_pixel(channels, serpentine_index(column, row), ROW_COLOR)
        show(channels)
        print(" Row", row + 1)
        time.sleep(config.SWEEP_SECONDS)
    clear(channels, 0.5)


def all_on(channels):
    print("PATTERN 5: conservative all-on colors")
    for name, color in ALL_ON_COLORS:
        for channel in channels:
            channel.fill(color)
        show(channels)
        print(" ", name)
        time.sleep(config.ALL_ON_SECONDS)
    clear(channels, config.BLACKOUT_SECONDS)


def render_performance_frame(channels, frame):
    """Render a moving vertical bar on every channel."""
    active_column = frame % config.MODULE_WIDTH
    for channel in channels:
        channel.fill(BLACK)
    for row in range(config.MODULE_HEIGHT):
        set_identical_pixel(
            channels,
            serpentine_index(active_column, row),
            COLUMN_COLOR,
        )


def timed_animation(channels):
    print(
        "PATTERN 6:",
        config.PERFORMANCE_FRAMES,
        "frame six-channel animation at",
        config.TARGET_FPS,
        "FPS",
    )
    frame_period = 1.0 / config.TARGET_FPS
    started = time.monotonic()
    missed_deadlines = 0
    slowest_work = 0.0

    for frame in range(config.PERFORMANCE_FRAMES):
        deadline = started + (frame + 1) * frame_period
        work_started = time.monotonic()
        render_performance_frame(channels, frame)
        show(channels)
        work_time = time.monotonic() - work_started
        slowest_work = max(slowest_work, work_time)

        remaining = deadline - time.monotonic()
        if remaining > 0:
            time.sleep(remaining)
        else:
            missed_deadlines += 1

    elapsed = time.monotonic() - started
    print(" Timed result: %.2f FPS" % (config.PERFORMANCE_FRAMES / elapsed))
    print(" Slowest render/transmit: %.1f ms" % (slowest_work * 1000))
    print(" Missed frame deadlines:", missed_deadlines)
    clear(channels, 0.5)


def maximum_rate(channels):
    print(
        "PATTERN 7:",
        config.PERFORMANCE_FRAMES,
        "frame unrestricted six-channel benchmark",
    )
    started = time.monotonic()
    for frame in range(config.PERFORMANCE_FRAMES):
        render_performance_frame(channels, frame)
        show(channels)
    elapsed = time.monotonic() - started
    print(" Maximum measured rate: %.1f FPS" % (
        config.PERFORMANCE_FRAMES / elapsed
    ))
    clear(channels, 0.5)


print("\nBU-22 REV D 9x16 EYE TILE TEST", VERSION)
print("Identical frames on CH1 through CH6")
print("Pixels/channel:", config.PIXELS_PER_CHANNEL)
print("Global brightness:", config.GLOBAL_BRIGHTNESS)
print("Current-limit external 5 V; connect only the tile under test.")

# Hold AHCT outputs disabled until every DotStar object has a black frame ready.
output_enable = digitalio.DigitalInOut(config.BUFFER_ENABLE)
output_enable.switch_to_output(value=False)
print("AHCT outputs: DISABLED")

for remaining in range(config.SAFE_START_SECONDS, 0, -1):
    print("Starting in", remaining)
    time.sleep(1)

channels = make_channels()
clear(channels)
output_enable.value = True
clear(channels, 0.5)
print("AHCT outputs: ENABLED after black frame")

while True:
    bender_eye(channels)
    path_chase(channels)
    column_sweep(channels)
    row_sweep(channels)
    all_on(channels)
    timed_animation(channels)
    maximum_rate(channels)
