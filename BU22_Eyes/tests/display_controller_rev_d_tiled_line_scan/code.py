"""Geometry-aware horizontal and vertical line scans across tiled arrays."""

import time

import adafruit_dotstar
import board
import digitalio
import supervisor

import config


supervisor.runtime.autoreload = False

BLACK = (0, 0, 0)
HORIZONTAL = (0, 180, 255)
VERTICAL = (200, 0, 255)
FRAME_SECONDS = 1.0 / config.FRAME_RATE
DISPLAY_WIDTH = config.MODULE_WIDTH * config.MODULE_COUNT
DISPLAY_HEIGHT = config.MODULE_HEIGHT
PIXEL_COUNT = config.MODULE_WIDTH * config.MODULE_HEIGHT * config.MODULE_COUNT


def pixel_index(x, y):
    """Map display coordinates into independently serpentine-wired modules."""
    module = x // config.MODULE_WIDTH
    local_x = x % config.MODULE_WIDTH
    module_base = module * config.MODULE_WIDTH * config.MODULE_HEIGHT
    if local_x % 2:
        local_y = config.MODULE_HEIGHT - 1 - y
    else:
        local_y = y
    return module_base + (local_x * config.MODULE_HEIGHT) + local_y


def show_frame(draw):
    started = time.monotonic()
    pixels.fill(BLACK)
    draw()
    pixels.show()
    remaining = FRAME_SECONDS - (time.monotonic() - started)
    if remaining > 0:
        time.sleep(remaining)


def horizontal_line(y):
    for x in range(DISPLAY_WIDTH):
        pixels[pixel_index(x, y)] = HORIZONTAL


def vertical_line(x):
    for y in range(DISPLAY_HEIGHT):
        pixels[pixel_index(x, y)] = VERTICAL


print("\nBU-22 TILED LINE-SCAN TEST")
print("Controller:", config.CONTROLLER_NAME)
print("Display:", DISPLAY_WIDTH, "x", DISPLAY_HEIGHT)
print("Modules:", config.MODULE_COUNT, "x", config.MODULE_WIDTH, "x", config.MODULE_HEIGHT)
print("Pixels:", PIXEL_COUNT)
print("Frame rate:", config.FRAME_RATE, "FPS")
print("Clock=CH5/A0, data=CH6/A1, baudrate=4 MHz")

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
pixels.fill(BLACK)
pixels.show()

for remaining in range(5, 0, -1):
    print("Enabling outputs in", remaining)
    time.sleep(1)

enable.value = True
pixels.show()

while True:
    print("Horizontal line: top to bottom")
    for row in range(DISPLAY_HEIGHT):
        show_frame(lambda row=row: horizontal_line(row))

    print("Vertical line: left to right")
    for column in range(DISPLAY_WIDTH):
        show_frame(lambda column=column: vertical_line(column))
