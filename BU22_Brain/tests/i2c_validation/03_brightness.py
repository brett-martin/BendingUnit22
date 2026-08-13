"""Two-byte parameter test using four conservative brightness levels."""

import time
import common

i2c = common.make_i2c()
common.wait_for_eyes(i2c)
while True:
    for level in (4, 12, 32, 64):
        print("BRIGHTNESS", level)
        common.send(i2c, common.SET_BRIGHTNESS, level)
        time.sleep(2)
    common.send(i2c, common.CLEAR)
    time.sleep(2)
