"""CH6-only daisy-chain LED validation for BU-22 display arrays."""

import time

import adafruit_dotstar
import board
import digitalio
import supervisor

import config


supervisor.runtime.autoreload = False

BLACK = (0, 0, 0)
COLORS = (
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (96, 96, 96),
)


print("\nBU-22 CH6 FULL-ARRAY LED TEST")
print("Controller:", config.CONTROLLER_NAME)
print("Pixels:", config.PIXEL_COUNT)
print("CH6 clock=A2, data=A1")
print("Do not power the LED array from USB.")

enable = digitalio.DigitalInOut(board.MOSI)
enable.switch_to_output(value=False)

pixels = adafruit_dotstar.DotStar(
    board.A2,
    board.A1,
    config.PIXEL_COUNT,
    brightness=config.BRIGHTNESS,
    auto_write=False,
)
pixels.fill(BLACK)
pixels.show()

for remaining in range(5, 0, -1):
    print("Enabling outputs in", remaining)
    time.sleep(1)

enable.value = True
pixels.show()

while True:
    print("Single-pixel chase")
    for index in range(config.PIXEL_COUNT):
        pixels.fill(BLACK)
        pixels[index] = (255, 160, 0)
        pixels.show()
        time.sleep(config.CHASE_DELAY)

    for color in COLORS:
        print("All pixels:", color)
        pixels.fill(color)
        pixels.show()
        time.sleep(config.SOLID_SECONDS)

    print("All pixels off")
    pixels.fill(BLACK)
    pixels.show()
    time.sleep(config.SOLID_SECONDS)
