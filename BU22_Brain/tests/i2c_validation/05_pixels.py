"""Address all 24 test pixels independently and cumulatively."""

import time
import common

COLORS = (
    (255, 0, 0), (0, 255, 0), (0, 0, 255),
    (255, 80, 0), (0, 180, 255), (220, 0, 255),
)

i2c = common.make_i2c()
common.wait_for_eyes(i2c)
while True:
    for channel, color in enumerate(COLORS):
        for pixel in range(4):
            common.send(i2c, common.CLEAR)
            common.send(i2c, common.SET_PIXEL, channel, pixel, *color)
            print("CHANNEL", channel + 1, "PIXEL", pixel + 1)
            time.sleep(0.3)
    common.send(i2c, common.CLEAR)
    for channel, color in enumerate(COLORS):
        for pixel in range(4):
            common.send(i2c, common.SET_PIXEL, channel, pixel, *color)
            time.sleep(0.15)
    common.send(i2c, common.CLEAR)
    time.sleep(2)
