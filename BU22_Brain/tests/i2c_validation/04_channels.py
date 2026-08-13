"""Address all six output channels independently and cumulatively."""

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
        common.send(i2c, common.CLEAR)
        common.send(i2c, common.SET_CHANNEL_COLOR, channel, *color)
        print("CHANNEL", channel + 1, color)
        time.sleep(1.5)
    common.send(i2c, common.CLEAR)
    for channel, color in enumerate(COLORS):
        common.send(i2c, common.SET_CHANNEL_COLOR, channel, *color)
        time.sleep(0.75)
    common.send(i2c, common.CLEAR)
    time.sleep(2)
