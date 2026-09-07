"""Repeating 10 FPS Bender-eye blink for one 9x16 eye tile."""

import time
import digitalio

import adafruit_dotstar

import config


VERSION = "0.1"
BLACK = (0, 0, 0)
EYE_COLOR = (255, 110, 0)
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


def serpentine_index(column, row):
    """Top-left origin; even columns descend and odd columns ascend."""
    physical_row = row if column % 2 == 0 else config.MODULE_HEIGHT - 1 - row
    return column * config.MODULE_HEIGHT + physical_row


def render_eye(channels, closed_rows):
    """Close an equal number of logical rows from the top and bottom."""
    for channel in channels:
        channel.fill(BLACK)

    first_visible_row = closed_rows
    last_visible_row = config.MODULE_HEIGHT - closed_rows
    for row in range(first_visible_row, last_visible_row):
        for column, pixel in enumerate(EYE_MASK[row]):
            if pixel == "Y":
                index = serpentine_index(column, row)
                for channel in channels:
                    channel[index] = EYE_COLOR
    show(channels)


def wait_for_frame(deadline):
    remaining = deadline - time.monotonic()
    if remaining > 0:
        time.sleep(remaining)
        return False
    return True


def blink(channels):
    frame_period = 1.0 / config.TARGET_FPS
    started = time.monotonic()
    frame_number = 0
    missed_deadlines = 0

    # Eight frames close one row from each edge until all 16 rows are dark.
    for closed_rows in range(1, config.MODULE_HEIGHT // 2 + 1):
        render_eye(channels, closed_rows)
        frame_number += 1
        deadline = started + frame_number * frame_period
        missed_deadlines += wait_for_frame(deadline)

    # Hold the fully closed eye for two more 10 FPS frames.
    for _ in range(config.CLOSED_HOLD_FRAMES):
        render_eye(channels, config.MODULE_HEIGHT // 2)
        frame_number += 1
        deadline = started + frame_number * frame_period
        missed_deadlines += wait_for_frame(deadline)

    # Reverse the closure, ending on the fully open eye after eight frames.
    for closed_rows in range(config.MODULE_HEIGHT // 2 - 1, -1, -1):
        render_eye(channels, closed_rows)
        frame_number += 1
        deadline = started + frame_number * frame_period
        missed_deadlines += wait_for_frame(deadline)

    elapsed = time.monotonic() - started
    print(
        "Blink: %d frames in %.2f seconds; missed deadlines: %d"
        % (frame_number, elapsed, missed_deadlines)
    )


print("\nBU-22 REV D 9x16 EYE BLINK TEST", VERSION)
print("Identical frames on CH1 through CH6")
print("Animation rate:", config.TARGET_FPS, "FPS")
print("Open hold:", config.OPEN_SECONDS, "seconds")

# Hold AHCT outputs disabled until a black frame is prepared on every channel.
output_enable = digitalio.DigitalInOut(config.BUFFER_ENABLE)
output_enable.switch_to_output(value=False)
print("AHCT outputs: DISABLED")

for remaining in range(config.SAFE_START_SECONDS, 0, -1):
    print("Starting in", remaining)
    time.sleep(1)

channels = make_channels()
for channel in channels:
    channel.fill(BLACK)
show(channels)
output_enable.value = True
show(channels)
print("AHCT outputs: ENABLED after black frame")

render_eye(channels, 0)
time.sleep(config.OPEN_SECONDS)

while True:
    blink(channels)
    time.sleep(config.OPEN_SECONDS)
